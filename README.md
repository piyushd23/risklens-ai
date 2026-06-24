# RiskLens AI

> **Intelligent Security Assessment. Actionable Risk Insights.**

RiskLens AI is an enterprise-grade AI-Assisted DAST (Dynamic Application Security Testing) Web Security Analytics Platform designed to automate security audits, categorize vulnerabilities using OWASP guidelines, compute CVSS v3.1 scores, prioritize threats using machine learning regressors, detect scan trends anomalies, and compile high-fidelity PDF, HTML, and JSON reports with live Power BI data streams.

---

## 1. System Architecture

The following diagram illustrates the flow from target specification through background scanning, ML processing, and dashboard presentation.

```mermaid
graph TD
    User([Security Operator]) -->|Configures Scope / Consents| ReactFE[React Frontend v19]
    ReactFE -->|JWT Auth / API Calls| FastAPIBE[FastAPI Backend Gateway]
    
    subgraph FastAPI Core
        FastAPIBE -->|Triggers Background Task| Worker[Asyncio DAST Worker]
        Worker -->|Crawl & Map Sitemap| BS4Crawler[BS4 & Requests Crawler]
        Worker -->|Evaluate Security Vectors| AuditEngine[Vulnerability Assessment Engine]
        
        AuditEngine -->|Calculates CVSS 3.1| CVSS[CVSS Calculator]
        AuditEngine -->|Maps to Categories| OWASP[OWASP Mapper]
        
        Worker -->|Predicts Risk Score| RidgeReg[Ridge Regressor Risk Model]
        Worker -->|Ensemble Outlier Scan| IsolationForest[Isolation Forest / LOF / One-Class SVM]
        
        Worker -->|Writes Flat Analytics| DB[(SQLite Database)]
    end
    
    FastAPIBE -->|Exposes analytical datasets| PowerBI[Power BI Desktop Link]
    FastAPIBE -->|Streams FileResponse| PDFReports[ReportLab PDF Compiler]
```

---

## 2. Database ER Diagram

The SQLite database consists of 11 interrelated tables representing the operation telemetry.

```mermaid
erDiagram
    users ||--o{ audit_logs : logs
    users ||--o{ notifications : receives
    roles ||--o{ users : assigns
    
    targets ||--o{ assets : catalogs
    targets ||--o{ assessments : runs
    targets ||--o{ analytics : tracks
    
    assessments ||--o{ findings : yields
    assessments ||--o{ reports : exports
    findings ||--|| risk_scores : prioritises
    
    users {
        int id PK
        string username
        string email
        string hashed_password
        int role_id FK
        boolean is_active
        datetime created_at
    }
    roles {
        int id PK
        string name
        string description
    }
    targets {
        int id PK
        string name
        string url
        string description
        string environment
        int crawl_depth
        text include_paths
        text exclude_paths
        string auth_type
        text auth_config
        int created_by FK
        datetime created_at
    }
    assets {
        int id PK
        int target_id FK
        string url
        string asset_type
        string method
        text parameters
        text headers
        text cookies
        datetime discovered_at
    }
    assessments {
        int id PK
        int target_id FK
        string status
        int progress
        text log_data
        datetime started_at
        datetime completed_at
        int created_by FK
    }
    findings {
        int id PK
        int assessment_id FK
        string title
        text description
        string severity
        float cvss_score
        string confidence_level
        string owasp_category
        text evidence
        text risk_explanation
        text remediation_guidance
        boolean is_false_positive
        datetime discovered_at
    }
    reports {
        int id PK
        int assessment_id FK
        string name
        string report_type
        string file_path
        int created_by FK
        datetime created_at
    }
    analytics {
        int id PK
        int target_id FK
        float security_score
        float compliance_score
        int total_vulns
        int critical_vulns
        int high_vulns
        int medium_vulns
        int low_vulns
        datetime calculated_at
    }
    risk_scores {
        int id PK
        int finding_id FK
        float priority_score
        string recommended_action
        string remediation_priority
        string model_version
    }
    audit_logs {
        int id PK
        int user_id FK
        string username
        string action
        text details
        string ip_address
        datetime created_at
    }
    notifications {
        int id PK
        int user_id FK
        string message
        boolean is_read
        datetime created_at
    }
```

---

## 3. Local Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 18+

### Backend Installation

1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install the dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. Run the database initialization and seeding script (seeds demo accounts, sample targets, historical runs, and trains models):
   ```bash
   python init_db.py
   ```
5. Launch the FastAPI Uvicorn server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### Frontend Installation

1. Navigate to the `frontend/` directory:
   ```bash
   cd ../frontend
   ```
2. Install the node packages:
   ```bash
   npm install
   ```
3. Run the frontend development build:
   ```bash
   npm run dev
   ```
4. Open your browser and navigate to the local address displayed (typically `http://localhost:5173`).

---

## 4. REST APIs & Power BI Feeds

The REST APIs are fully documented in the Swagger UI endpoint directory (available at `http://localhost:8000/docs`).

### Core Endpoints
- `POST /api/v1/auth/login`: Issue JWT authentication tokens.
- `POST /api/v1/auth/register`: Create user and select roles.
- `POST /api/v1/targets/`: Configure web application scope.
- `POST /api/v1/assessments/`: Start DAST security scan task.
- `POST /api/v1/reports/generate/{assessment_id}`: Compile PDF, HTML, JSON files.
- `GET /api/v1/reports/download/{report_id}`: Directly stream a compiled report to the browser.
- `GET /api/v1/analytics/powerbi/findings`: Expose flattened dataset for Power BI.

---

## 5. Production Deployment Guide

To deploy RiskLens AI into production without Docker:

### Backend Deployment (ASGI Gunicorn + Uvicorn)

1. Lock down permissions on the SQLite database file:
   ```bash
   chmod 600 risklens_ai.db
   ```
2. Set strong production environment variables:
   ```bash
   export SECRET_KEY="generate-a-strong-random-key"
   ```
3. Deploy the FastAPI app using Gunicorn with Uvicorn worker class:
   ```bash
   venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
   ```
4. Setup a systemd service descriptor file (`/etc/systemd/system/risklens-backend.service`) to ensure the process restarts automatically.

### Frontend Deployment (Nginx)

1. Compile the production optimized static build:
   ```bash
   npm run build
   ```
2. Move the compiled outputs (located inside `dist/`) to your web server root:
   ```bash
   cp -r dist/* /var/www/risklens-app/
   ```
3. Configure Nginx to serve the build files and proxy `/api/` traffic to the backend:
   ```nginx
   server {
       listen 80;
       server_name risklens.yourdomain.com;

       location / {
           root /var/www/risklens-app;
           index index.html;
           try_files $uri $uri/ /index.html;
       }

       location /api/ {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```
4. Install an SSL certificate using Let's Encrypt Certbot:
   ```bash
   sudo certbot --nginx -d risklens.yourdomain.com
   ```
