"""
ClinicalPulse AI - Main Application Entrypoint
Student Name: Shambhavi Holkar | Reg No: 26BAI10454
"""

import sys
import os
from typing import Optional

# Ensure package root is in system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models.user_model import UserRole, AuthToken
from src.modules.auth_manager import AuthManager
from src.modules.ml_triage_engine import MLTriageEngine
from src.modules.patient_manager import PatientManager
from src.modules.analytics_engine import AnalyticsEngine
from src.utils.validators import ValidationError
from src.utils.logger import logger


class ClinicalPulseApp:
    """
    Main Application Controller for ClinicalPulse AI.
    Integrates authentication, triage prediction, patient CRUD, and analytics dashboard.
    """

    def __init__(self):
        print("Initializing ClinicalPulse AI Subsystems...")
        self.auth_mgr = AuthManager()
        self.ml_engine = MLTriageEngine()
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "db.json")
        self.patient_mgr = PatientManager(data_file=data_path)
        self.analytics_engine = AnalyticsEngine(self.patient_mgr)
        self.current_token: Optional[AuthToken] = None
        self._seed_sample_patient_encounters()

    def _seed_sample_patient_encounters(self):
        """Seeds initial synthetic patient encounters if queue is empty."""
        if len(self.patient_mgr.list_all_patients()) > 0:
            return

        samples = [
            {
                "name": "Robert Chen",
                "age": 62,
                "gender": "Male",
                "chief_complaint": "Severe crushing chest pain radiating to left arm and shortness of breath",
                "vitals": {"heart_rate": 115, "systolic_bp": 175, "diastolic_bp": 105, "spo2": 91.5, "temp_c": 37.1, "resp_rate": 26}
            },
            {
                "name": "Emily Watson",
                "age": 28,
                "gender": "Female",
                "chief_complaint": "Mild fever and sore throat for 2 days",
                "vitals": {"heart_rate": 78, "systolic_bp": 118, "diastolic_bp": 76, "spo2": 98.5, "temp_c": 38.2, "resp_rate": 16}
            },
            {
                "name": "Marcus Johnson",
                "age": 45,
                "gender": "Male",
                "chief_complaint": "Sudden onset right-sided weakness, slurred speech, and stroke suspicion",
                "vitals": {"heart_rate": 92, "systolic_bp": 188, "diastolic_bp": 112, "spo2": 95.0, "temp_c": 36.8, "resp_rate": 20}
            },
            {
                "name": "Sofia Rodriguez",
                "age": 8,
                "gender": "Female",
                "chief_complaint": "Persistent wheezing and asthma exacerbation",
                "vitals": {"heart_rate": 132, "systolic_bp": 102, "diastolic_bp": 64, "spo2": 89.0, "temp_c": 37.4, "resp_rate": 34}
            }
        ]

        for s in samples:
            patient = self.patient_mgr.create_patient(
                name=s["name"],
                age=s["age"],
                gender=s["gender"],
                chief_complaint=s["chief_complaint"],
                vitals_dict=s["vitals"]
            )
            assessment = self.ml_engine.predict_triage(
                age=patient.age,
                vitals=patient.vitals,
                chief_complaint=patient.chief_complaint
            )
            patient.update_assessment(assessment)

        logger.info("Sample clinical dataset initialized successfully.")

    def run_login(self) -> bool:
        """Prompts user for login credentials."""
        print("\n==========================================================================")
        print("          CLINICALPULSE AI - SYSTEM AUTHENTICATION LOG IN                ")
        print("==========================================================================")
        print(" Default Accounts for Demonstration:")
        print("   1. Admin         -> Username: admin       | Password: Admin123!")
        print("   2. Triage Nurse  -> Username: nurse_sarah | Password: NursePass123!")
        print("   3. Clinician     -> Username: dr_smith    | Password: DoctorPass123!")
        print("==========================================================================")

        username = input("Enter Username: ").strip()
        password = input("Enter Password: ").strip()

        try:
            self.current_token = self.auth_mgr.authenticate(username, password)
            print(f"\n[+] Authentication Successful! Logged in as: {self.current_token.username} ({self.current_token.role.value})")
            return True
        except ValidationError as e:
            print(f"\n[-] Authentication Error: {e}")
            return False

    def handle_add_patient(self):
        """Intake workflow for Triage Nurse."""
        try:
            self.auth_mgr.enforce_role(self.current_token.token, [UserRole.TRIAGE_NURSE, UserRole.ADMIN])
            print("\n--- NEW PATIENT TRIAGE INTAKE ---")
            name = input("Patient Full Name: ")
            age = int(input("Age: "))
            gender = input("Gender (Male/Female/Other): ")
            complaint = input("Chief Complaint / Symptoms Description: ")

            print("\nEnter Vital Signs:")
            hr = int(input("  Heart Rate (bpm): "))
            sbp = int(input("  Systolic BP (mmHg): "))
            dbp = int(input("  Diastolic BP (mmHg): "))
            spo2 = float(input("  SpO2 Oxygen Saturation (%): "))
            temp = float(input("  Temperature (°C): "))
            rr = int(input("  Respiratory Rate (breaths/min): "))

            vitals_dict = {
                "heart_rate": hr,
                "systolic_bp": sbp,
                "diastolic_bp": dbp,
                "spo2": spo2,
                "temp_c": temp,
                "resp_rate": rr
            }

            patient = self.patient_mgr.create_patient(name, age, gender, complaint, vitals_dict)
            assessment = self.ml_engine.predict_triage(patient.age, patient.vitals, patient.chief_complaint)
            patient.update_assessment(assessment)

            print("\n==========================================================================")
            print(f" [+] Patient Registered & Assessed Successfully!")
            print(f" Patient ID      : {patient.patient_id}")
            print(f" AI Urgency Level: Category {assessment.urgency_level.value} - {assessment.urgency_level.label}")
            print(f" Composite Risk  : {assessment.composite_score:.2f} / 100")
            print(f" ML Confidence   : {assessment.confidence_score * 100:.1f}%")
            if assessment.detected_red_flags:
                print(" RED FLAGS DETECTED:")
                for rf in assessment.detected_red_flags:
                    print(f"   * {rf}")
            print("==========================================================================")

        except (ValidationError, ValueError) as e:
            print(f"\n[-] Error: {e}")

    def handle_view_prioritized_queue(self):
        """Displays live clinical priority queue."""
        queue = self.patient_mgr.get_prioritized_queue()
        print("\n==========================================================================")
        print("                PRIORITIZED CLINICAL EMERGENCY QUEUE                      ")
        print("==========================================================================")
        if not queue:
            print(" No patients currently waiting in triage queue.")
            return

        print(f"{'Priority':<8} | {'Patient ID':<12} | {'Name':<18} | {'Urgency Level':<25} | {'Risk Score'}")
        print("-" * 75)
        for idx, p in enumerate(queue, 1):
            urgency_str = f"Cat {p.assessment.urgency_level.value}: {p.assessment.urgency_level.name}"
            print(f"{idx:<8} | {p.patient_id:<12} | {p.name:<18} | {urgency_str:<25} | {p.assessment.composite_score:.1f}")
        print("==========================================================================")

    def handle_clinician_consult(self):
        """Clinician workflow to examine top patient and update status."""
        try:
            self.auth_mgr.enforce_role(self.current_token.token, [UserRole.CLINICIAN, UserRole.ADMIN])
            queue = self.patient_mgr.get_prioritized_queue()
            if not queue:
                print("\n[!] No waiting patients in queue.")
                return

            top_patient = queue[0]
            print("\n==========================================================================")
            print(f"          PATIENT CLINICAL DECISION SUPPORT - {top_patient.patient_id}    ")
            print("==========================================================================")
            print(f" Patient Name    : {top_patient.name} ({top_patient.age} y/o {top_patient.gender})")
            print(f" Chief Complaint : {top_patient.chief_complaint}")
            print(f" Vital Signs     : HR={top_patient.vitals.heart_rate} | BP={top_patient.vitals.systolic_bp}/{top_patient.vitals.diastolic_bp} | SpO2={top_patient.vitals.spo2}% | Temp={top_patient.vitals.temp_c}°C | RR={top_patient.vitals.resp_rate}")
            print(f" AI Urgency      : Category {top_patient.assessment.urgency_level.value} ({top_patient.assessment.urgency_level.label})")
            print(f" Composite Risk  : {top_patient.assessment.composite_score:.2f} / 100.0")
            if top_patient.assessment.detected_red_flags:
                print(" Active Red Flags:")
                for rf in top_patient.assessment.detected_red_flags:
                    print(f"   [!] {rf}")
            print("==========================================================================")

            action = input("\nUpdate Status [1: Move to Treatment, 2: Discharge Patient, 3: Skip]: ").strip()
            if action == "1":
                self.patient_mgr.update_patient_status(top_patient.patient_id, "In Treatment", self.current_token.username)
                print(f"[+] Patient {top_patient.name} moved to 'In Treatment' under Dr. {self.current_token.username}.")
            elif action == "2":
                self.patient_mgr.update_patient_status(top_patient.patient_id, "Discharged", self.current_token.username)
                print(f"[+] Patient {top_patient.name} has been Discharged.")

        except ValidationError as e:
            print(f"\n[-] Access Denied: {e}")

    def handle_analytics_dashboard(self):
        """Displays real-time dashboard and options to export reports."""
        print("\n" + self.analytics_engine.format_ascii_dashboard())
        opt = input("\nExport Analytics Report? [1: Export CSV, 2: Export JSON, 3: Back]: ").strip()
        if opt == "1":
            path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "export_report.csv")
            self.analytics_engine.export_report_csv(path)
            print(f"[+] CSV Report generated at '{path}'")
        elif opt == "2":
            path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "export_summary.json")
            self.analytics_engine.export_summary_json(path)
            print(f"[+] JSON Summary generated at '{path}'")

    def run_cli_menu(self):
        """Main CLI navigation loop."""
        while True:
            if not self.current_token or not self.current_token.is_valid():
                if not self.run_login():
                    retry = input("\nRetry Login? (y/n): ").strip().lower()
                    if retry != 'y':
                        print("Exiting ClinicalPulse AI. Goodbye!")
                        sys.exit(0)
                    continue

            print("\n==========================================================================")
            print(f" CLINICALPULSE AI MAIN MENU | User: {self.current_token.username} ({self.current_token.role.value})")
            print("==========================================================================")
            print(" 1. Intake New Patient Encounter (Triage Nurse / Admin)")
            print(" 2. View Prioritized Emergency Queue (All Roles)")
            print(" 3. Clinical Decision Support & Examination (Clinician / Admin)")
            print(" 4. Real-Time Analytics Dashboard & Reports (All Roles)")
            print(" 5. Search Patient Records (All Roles)")
            print(" 6. Switch User / Logout")
            print(" 7. Exit System")
            print("==========================================================================")

            choice = input("Select Option (1-7): ").strip()

            if choice == "1":
                self.handle_add_patient()
            elif choice == "2":
                self.handle_view_prioritized_queue()
            elif choice == "3":
                self.handle_clinician_consult()
            elif choice == "4":
                self.handle_analytics_dashboard()
            elif choice == "5":
                q = input("\nEnter Patient Name or ID to search: ").strip()
                res = self.patient_mgr.search_patients(q)
                print(f"\nFound {len(res)} record(s):")
                for p in res:
                    u_name = p.assessment.urgency_level.name if p.assessment else 'Unassessed'
                    print(f" - [{p.patient_id}] {p.name} | Age: {p.age} | Status: {p.status} | Urgency: {u_name}")
            elif choice == "6":
                self.current_token = None
                print("\n[+] Successfully logged out.")
            elif choice == "7":
                data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "db.json")
                os.makedirs(os.path.dirname(data_path), exist_ok=True)
                self.patient_mgr.save_to_file(data_path)
                print("\n[+] System state saved. Exiting ClinicalPulse AI. Goodbye!")
                sys.exit(0)
            else:
                print("\n[-] Invalid menu selection. Please try again.")


def main():
    app = ClinicalPulseApp()
    app.run_cli_menu()


if __name__ == "__main__":
    main()
