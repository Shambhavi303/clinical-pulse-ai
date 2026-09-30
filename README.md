# ClinicalPulse AI: Intelligent Patient Risk Stratification & Clinical Decision Support System

**Student Name:** Shambhavi Holkar  
**Registration No:** 26BAI10454  
**Course:** AI & Data Science / Computer Science & Engineering with AI Specialization  
**Academic Project:** VITyarthi - Build Your Own Project (Flipped Course Evaluation)  

---

## 📋 Executive Overview
**ClinicalPulse AI** is an advanced, production-grade clinical decision support and patient risk stratification platform designed for Emergency Departments (ED) and outpatient medical clinics. 

In high-volume hospital environments, traditional emergency triage relies heavily on manual assessment and static vital sign cutoffs, leading to triage delays, subjective human error, and prolonged wait times for critical patients. **ClinicalPulse AI** solves this bottleneck by synthesizing multi-modal clinical data—physiological vital signs, patient age/demographics, and symptom text—using a hybrid framework combining **Ensemble Machine Learning (Random Forest Classification)** and a **Clinical Red-Flag Rule Engine**.

The system dynamically prioritizes emergency queues, provides actionable decision support for clinicians, computes real-time operational throughput analytics, and enforces robust security via Role-Based Access Control (RBAC).

---

## 🌟 Key Features & Module Breakdown

### 1. Security & Role-Based Access Control (RBAC) Module
- **Cryptographic Security:** Passwords hashed using PBKDF2-HMAC-SHA256 with 100,000 iterations and unique per-user salts.
- **Session Authentication:** Token-based session verification with automatic token expiration.
- **Granular RBAC:** Role enforcement across three distinct operational tiers:
  - `Administrator`: Full system access, user management, and report generation.
  - `Triage Nurse`: Patient encounter intake, vital signs entry, and initial assessment.
  - `Clinician (Doctor)`: Queue inspection, AI recommendation review, encounter status updates (In Treatment / Discharged).

### 2. Multi-Modal Data Intake & Validation Module
- **Input Sanitization:** XSS and SQL injection protection for text inputs using regex cleaners.
- **Physiological Boundary Validation:** Strict medical range checks for Heart Rate (20-250 bpm), Blood Pressure (Systolic: 40-280 mmHg, Diastolic: 20-200 mmHg), SpO2 (50-100%), Temperature (30-45°C), and Respiratory Rate (4-60 bpm).

### 3. Machine Learning Triage & Clinical Decision Support Engine
- **Supervised Classifier:** Scikit-Learn Random Forest Classifier predicting standard Emergency Severity Index (ESI) categories (1: Resuscitation to 5: Non-Urgent).
- **Natural Language Processing (NLP):** Symptom keyword extraction parsing chief complaints for high-risk flags (e.g., chest pain, shortness of breath, stroke, severe bleeding).
- **Hybrid Safety Override:** Deterministic clinical rule engine overriding ML predictions if acute physiological decompensation (e.g., SpO2 < 90%, hypertensive shock) is detected.
- **Composite Risk Scoring:** Computes a continuous Composite Risk Score (0.0 to 100.0) alongside confidence metrics.

### 4. Dynamic Queue & Patient Encounter Manager (CRUD)
- **Thread-Safe Repository:** Full lifecycle CRUD operations for patient records.
- **Dynamic Risk Priority Queue:** Replaces legacy FIFO queues with real-time risk sorting, placing high-urgency resuscitation cases at the top of the queue instantly.

### 5. Analytics & Visualization Dashboard
- **Operational Metrics:** Real-time computation of total encounters, critical patient percentages, average department risk score, and top red flag frequencies.
- **Export Engine:** Exports operational reports into formatted CSV and JSON files for administrative auditing.

---

## 🛠️ Technologies & Dependencies Used
- **Programming Language:** Python 3.10+
- **Machine Learning & Data Processing:** `scikit-learn`, `numpy`, `pandas`
- **Unit Testing Framework:** `pytest`, `unittest`
- **System Utilities:** `tabulate`, `json`, `csv`, `hashlib`, `secrets`, `re`, `logging`
- **Diagramming & Design:** Mermaid.js, ASCII Diagrams

---

## 📂 Project Directory Structure Map

```
Vithyarthi Project (Shambhavi)/
├── docs/
│   ├── design_diagrams/
│   │   ├── architecture.mermaid
│   │   ├── use_case.mermaid
│   │   ├── workflow.mermaid
│   │   ├── sequence.mermaid
│   │   ├── class_diagram.mermaid
│   │   └── er_diagram.mermaid
│   ├── project_report.md     # Full 15-Section Comprehensive Project Report
│   └── statement.md          # Dedicated Problem Statement Document
├── src/                      # Modular Source Code Package
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user_model.py     # User, UserRole, and AuthToken Data Models
│   │   └── triage_model.py   # PatientRecord, VitalSigns, UrgencyLevel Data Models
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── auth_manager.py   # User Registration, Authentication & RBAC
│   │   ├── ml_triage_engine.py # ML Classifier & Clinical Rule Engine
│   │   ├── patient_manager.py # Patient CRUD & Dynamic Priority Queue
│   │   └── analytics_engine.py # Metrics Dashboard & Export Service
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py         # Structured Logging & Audit Logger
│   │   └── validators.py     # Input Sanitization & Medical Range Checks
│   ├── __init__.py
│   └── main.py               # Application Entrypoint & Interactive CLI
├── tests/                    # Dedicated Unit & Integration Test Suite
│   ├── __init__.py
│   ├── test_auth.py          # Auth & Security Tests
│   ├── test_ml_engine.py     # ML Engine & Red-Flag Tests
│   ├── test_patient_manager.py # Patient CRUD & Queue Tests
│   ├── test_analytics.py     # Analytics & Export Tests
│   └── test_main.py          # System Integration End-to-End Test Runner
├── .gitignore                # Standard Python GitIgnore Rules
├── README.md                 # Project Overview & Setup Guide
├── statement.md              # Root Copy of VITyarthi Statement Document
└── requirements.txt          # Third-Party Dependencies
```

---

## 🚀 Setup, Installation & Execution Instructions

### Prerequisites
- Python 3.10 or higher installed on Windows/Linux/macOS.
- Git installed (optional, for repository management).

### Step 1: Clone or Navigate to Directory
```bash
cd "c:\Vithyarthi Project (Shambhavi)"
```

### Step 2: Create and Activate Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
Launch the interactive CLI dashboard:
```bash
python src/main.py
```

#### Default Demonstration Login Credentials:
| Role | Username | Password |
| :--- | :--- | :--- |
| **Administrator** | `admin` | `Admin123!` |
| **Triage Nurse** | `nurse_sarah` | `NursePass123!` |
| **Clinician (Doctor)** | `dr_smith` | `DoctorPass123!` |

---

## 🧪 Testing Instructions

Run the full automated unit test suite using `pytest`:

```bash
python -m pytest tests/
```

To run individual test modules:
```bash
# Test Authentication & RBAC
python -m pytest tests/test_auth.py

# Test ML Engine
python -m pytest tests/test_ml_engine.py

# Test System Integration Workflow
python tests/test_main.py
```

---

## 📸 System Screenshots & UI Visualizations

### 1. Authentication & System Main Menu
```
==========================================================================
 CLINICALPULSE AI MAIN MENU | User: nurse_sarah (Triage Nurse)
==========================================================================
 1. Intake New Patient Encounter (Triage Nurse / Admin)
 2. View Prioritized Emergency Queue (All Roles)
 3. Clinical Decision Support & Examination (Clinician / Admin)
 4. Real-Time Analytics Dashboard & Reports (All Roles)
 5. Search Patient Records (All Roles)
 6. Switch User / Logout
 7. Exit System
==========================================================================
```

### 2. Prioritized Emergency Queue Dashboard
```
==========================================================================
                PRIORITIZED CLINICAL EMERGENCY QUEUE                      
==========================================================================
Priority | Patient ID   | Name               | Urgency Level             | Risk Score
--------------------------------------------------------------------------
1        | PAT-A9F4B12C | Robert Chen        | Cat 1: RESUSCITATION      | 95.0
2        | PAT-C3D7E811 | Marcus Johnson     | Cat 1: RESUSCITATION      | 95.0
3        | PAT-F12098AA | Sofia Rodriguez    | Cat 1: RESUSCITATION      | 95.0
4        | PAT-B882109E | Emily Watson       | Cat 4: LESS_URGENT        | 32.0
==========================================================================
```

### 3. Real-Time Clinical Analytics Output
```
==========================================================================
                 CLINICALPULSE AI - REAL-TIME DASHBOARD                   
==========================================================================
 Total Patient Encounters : 4
 Assessed by AI Triage   : 4
 Critical Patient Count   : 3 (75.0%)
 Average Risk Score       : 79.25 / 100.0
--------------------------------------------------------------------------
 URGENCY CATEGORY DISTRIBUTION:
  - CATEGORY_1_RESUSCITATION  :   3 ######
  - CATEGORY_4_LESS_URGENT    :   1 ##
==========================================================================
```

---

## 👤 Author Information
- **Student Name:** Shambhavi Holkar
- **Registration Number:** 26BAI10454
- **Institution:** Vellore Institute of Technology (VIT)
