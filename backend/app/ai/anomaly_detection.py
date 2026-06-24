import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor
from app.ai.feature_engineering import FeatureEngineering
import logging
from typing import List, Dict, Any

logger = logging.getLogger("AnomalyDetection")

class AnomalyDetector:
    def __init__(self):
        self.iso_forest = None
        self.one_class_svm = None
        self.lof = None
        self.is_trained = False

    def _generate_synthetic_history(self) -> np.ndarray:
        """
        Creates synthetic normal scans to establish a baseline.
        Normal scans typically have:
        - Total findings: 2 to 10
        - Avg CVSS: 2.0 to 5.0
        - High/Crit ratio: 0.0 to 0.3
        - Med ratio: 0.2 to 0.5
        - Low ratio: 0.4 to 0.8
        - Unique OWASP categories: 1 to 4
        """
        np.random.seed(42)
        n_samples = 40
        
        totals = np.random.randint(2, 9, n_samples)
        avg_cvss = np.random.uniform(2.0, 4.8, n_samples)
        crit_high_ratios = np.random.uniform(0.0, 0.25, n_samples)
        med_ratios = np.random.uniform(0.2, 0.5, n_samples)
        low_ratios = 1.0 - (crit_high_ratios + med_ratios)
        unique_owasps = np.random.randint(1, 4, n_samples)
        
        # Matrix
        history = np.column_stack([
            totals.astype(float),
            avg_cvss,
            crit_high_ratios,
            med_ratios,
            low_ratios,
            unique_owasps.astype(float)
        ])
        
        # Inject 3 outliers intentionally to allow models to learn boundary
        outliers = np.array([
            [35.0, 8.2, 0.8, 0.1, 0.1, 8.0],  # High volume, high severity
            [1.0, 9.8, 1.0, 0.0, 0.0, 1.0],   # Single critical spike
            [22.0, 1.5, 0.0, 0.1, 0.9, 2.0]   # Unusually high low-vuln count
        ])
        
        return np.vstack([history, outliers])

    def train(self, historical_scans_findings: List[List[Dict[str, Any]]] = None):
        """
        Trains models on history. Fallback to synthetic if history is insufficient.
        """
        if historical_scans_findings and len(historical_scans_findings) >= 8:
            X_train = FeatureEngineering.extract_multiple_assessments(historical_scans_findings)
            logger.info(f"Training anomaly detection on {len(X_train)} real scans.")
        else:
            X_train = self._generate_synthetic_history()
            logger.info("Using synthetic historical baseline to fit anomaly detection models.")

        # 1. Isolation Forest
        self.iso_forest = IsolationForest(contamination=0.1, random_state=42)
        self.iso_forest.fit(X_train)

        # 2. One-Class SVM
        self.one_class_svm = OneClassSVM(nu=0.1, kernel='rbf', gamma='scale')
        self.one_class_svm.fit(X_train)

        # 3. Local Outlier Factor (Novelty = True is required to call predict())
        self.lof = LocalOutlierFactor(n_neighbors=5, novelty=True, contamination=0.1)
        self.lof.fit(X_train)

        self.is_trained = True

    def check_anomaly(self, current_scan_findings: List[Dict[str, Any]], 
                      history: List[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Scores current scan run against trained model ensemble.
        Returns: is_anomaly, anomaly_confidence, raw_predictions, features
        """
        if not self.is_trained:
            self.train(history)

        features = FeatureEngineering.extract_assessment_features(current_scan_findings)
        X_test = features.reshape(1, -1)

        # Predictors return 1 for normal, -1 for anomaly
        pred_if = int(self.iso_forest.predict(X_test)[0])
        pred_svm = int(self.one_class_svm.predict(X_test)[0])
        pred_lof = int(self.lof.predict(X_test)[0])

        # Convert to boolean anomaly flags (True if anomaly, False if normal)
        is_if_anomaly = (pred_if == -1)
        is_svm_anomaly = (pred_svm == -1)
        is_lof_anomaly = (pred_lof == -1)

        # Ensemble voting
        anomaly_votes = sum([is_if_anomaly, is_svm_anomaly, is_lof_anomaly])
        is_anomaly = anomaly_votes >= 2 # Majority vote
        
        # Calculate confidence
        confidence = round((anomaly_votes / 3) * 100, 1) if is_anomaly else round(((3 - anomaly_votes) / 3) * 100, 1)

        # Interpret the feature vector
        trigger_reasons = []
        if features[0] > 15:
            trigger_reasons.append(f"Unusually high finding count ({int(features[0])} findings)")
        if features[1] > 6.0:
            trigger_reasons.append(f"Elevated average CVSS severity ({features[1]:.1f})")
        if features[2] > 0.4:
            trigger_reasons.append(f"High ratio of Critical/High severity weaknesses ({features[2]*100:.1f}%)")

        explanation = "Scan pattern is consistent with historical baselines."
        if is_anomaly:
            if trigger_reasons:
                explanation = "Scan pattern flagged as anomalous: " + "; ".join(trigger_reasons)
            else:
                explanation = "Scan pattern exhibits multi-dimensional divergence from normal baseline configuration profile."

        return {
            "is_anomaly": is_anomaly,
            "confidence": confidence,
            "explanation": explanation,
            "individual_runs": {
                "isolation_forest_anomaly": is_if_anomaly,
                "one_class_svm_anomaly": is_svm_anomaly,
                "local_outlier_factor_anomaly": is_lof_anomaly
            },
            "features": {
                "total_findings": int(features[0]),
                "avg_cvss": round(features[1], 2),
                "high_crit_ratio": round(features[2], 3),
                "med_ratio": round(features[3], 3),
                "low_ratio": round(features[4], 3),
                "unique_owasp": int(features[5])
            }
        }
