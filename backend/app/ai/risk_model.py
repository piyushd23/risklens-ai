import os
import pickle
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import logging

logger = logging.getLogger("RiskModel")

MODEL_PATH = "backend/app/ai/risk_model.pkl"
# Adjust path if running inside backend vs root
if not os.path.exists("backend") and os.path.exists("app"):
    MODEL_PATH = "app/ai/risk_model.pkl"

class RiskPrioritizationModel:
    def __init__(self):
        self.pipeline = None
        self.model_version = "1.0.0"
        self._initialize_model()

    def _generate_synthetic_data(self) -> pd.DataFrame:
        """
        Generates structured synthetic training data to train the regressor.
        """
        np.random.seed(42)
        n_samples = 500
        
        cvss_scores = np.random.uniform(0.0, 10.0, n_samples)
        
        owasp_categories = np.random.choice([
            "A01:2021-Broken Access Control",
            "A02:2021-Cryptographic Failures",
            "A03:2021-Injection",
            "A04:2021-Insecure Design",
            "A05:2021-Security Misconfiguration",
            "A07:2021-Identification and Authentication Failures"
        ], n_samples)
        
        finding_frequencies = np.random.randint(1, 25, n_samples)
        
        asset_criticalities = np.random.choice(["High", "Medium", "Low"], n_samples, p=[0.25, 0.50, 0.25])
        
        historical_findings = np.random.randint(0, 100, n_samples)
        
        # Calculate target Risk Priority Score (0 to 100) based on domain heuristic rules
        criticality_weight = {"High": 20, "Medium": 10, "Low": 2}
        
        target_scores = []
        for i in range(n_samples):
            # Base logic
            base = cvss_scores[i] * 6.5 # max 65
            crit = criticality_weight[asset_criticalities[i]] # max 20
            freq = min(finding_frequencies[i] * 0.5, 10.0) # max 10
            hist = min(historical_findings[i] * 0.05, 5.0) # max 5
            
            raw_score = base + crit + freq + hist
            # Bound
            risk_score = max(0.0, min(100.0, raw_score))
            target_scores.append(risk_score)
            
        df = pd.DataFrame({
            "cvss_score": cvss_scores,
            "owasp_category": owasp_categories,
            "finding_frequency": finding_frequencies,
            "asset_criticality": asset_criticalities,
            "historical_findings": historical_findings,
            "risk_priority_score": target_scores
        })
        return df

    def _initialize_model(self):
        # Ensure parent directories exist
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        
        if os.path.exists(MODEL_PATH):
            try:
                with open(MODEL_PATH, "rb") as f:
                    self.pipeline = pickle.load(f)
                logger.info("Loaded pre-trained AI Risk Prioritization Model.")
                return
            except Exception as e:
                logger.error(f"Error loading model pkl: {e}. Retraining...")

        # If not exist, train and save
        logger.info("Training AI Risk Prioritization Model using Ridge Regressor...")
        df = self._generate_synthetic_data()
        
        X = df[["cvss_score", "owasp_category", "finding_frequency", "asset_criticality", "historical_findings"]]
        y = df["risk_priority_score"]
        
        categorical_features = ["owasp_category", "asset_criticality"]
        numerical_features = ["cvss_score", "finding_frequency", "historical_findings"]
        
        preprocessor = ColumnTransformer(
            transformers=[
                ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
            ],
            remainder="passthrough" # leaves numerical features alone
        )
        
        pipeline = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("regressor", Ridge(alpha=1.0))
        ])
        
        pipeline.fit(X, y)
        self.pipeline = pipeline
        
        try:
            with open(MODEL_PATH, "wb") as f:
                pickle.dump(pipeline, f)
            logger.info("Successfully trained and saved AI Risk Model.")
        except Exception as e:
            logger.error(f"Failed to save AI Risk Model: {e}")

    def predict_risk(self, cvss_score: float, owasp_category: str, finding_frequency: int,
                     asset_criticality: str, historical_findings: int) -> dict:
        """
        Predicts Risk Priority Score, recommended action, and remediation priority.
        """
        if not self.pipeline:
            self._initialize_model()
            
        data = pd.DataFrame([{
            "cvss_score": cvss_score,
            "owasp_category": owasp_category,
            "finding_frequency": finding_frequency,
            "asset_criticality": asset_criticality,
            "historical_findings": historical_findings
        }])
        
        try:
            pred = self.pipeline.predict(data)[0]
            priority_score = max(0.0, min(100.0, float(pred)))
        except Exception as e:
            logger.error(f"Prediction error: {e}. Using fallback heuristic.")
            # Fallback
            crit_val = 20 if asset_criticality == "High" else (10 if asset_criticality == "Medium" else 2)
            priority_score = (cvss_score * 6.5) + crit_val + min(finding_frequency * 0.5, 10.0)
            priority_score = max(0.0, min(100.0, priority_score))
            
        # Determine remediation priority and action recommendation
        if priority_score >= 80.0:
            remediation_priority = "Immediate"
            recommended_action = "Initiate immediate patch deployment, restrict perimeter access, and escalate to CISO dashboard."
        elif 60.0 <= priority_score < 80.0:
            remediation_priority = "High"
            recommended_action = "Schedule remediation within 48 hours, audit access vectors, and notify DevSecOps teams."
        elif 35.0 <= priority_score < 60.0:
            remediation_priority = "Medium"
            recommended_action = "Queue for next standard sprint deployment lifecycle. Apply configuration hardening controls."
        else:
            remediation_priority = "Low"
            recommended_action = "Monitor asset posture. Address during regular maintenance windows."
            
        return {
            "priority_score": round(priority_score, 1),
            "remediation_priority": remediation_priority,
            "recommended_action": recommended_action,
            "model_version": self.model_version
        }
