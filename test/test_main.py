"""
Main Integration & Validation Test Suite Entrypoint
Student Name: Shambhavi Holkar | Reg No: 26BAI10454
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.modules.auth_manager import AuthManager
from src.modules.ml_triage_engine import MLTriageEngine
from src.modules.patient_manager import PatientManager
from src.modules.analytics_engine import AnalyticsEngine
from src.models.triage_model import UrgencyLevel


class TestSystemIntegration(unittest.TestCase):
    """
    End-to-end integration test suite for ClinicalPulse AI.
    """

    def setUp(self):
        self.auth_mgr = AuthManager()
        self.ml_engine = MLTriageEngine()
        self.patient_mgr = PatientManager()
        self.analytics_engine = AnalyticsEngine(self.patient_mgr)

    def test_full_patient_intake_to_analytics_workflow(self):
        # 1. Authenticate Nurse
        token = self.auth_mgr.authenticate("nurse_sarah", "NursePass123!")
        self.assertIsNotNone(token.token)

        # 2. Intake Critical Cardiac Patient
        patient = self.patient_mgr.create_patient(
            name="Emergency Test Patient",
            age=68,
            gender="Male",
            chief_complaint="Severe chest pain and sudden cardiac arrest symptoms",
            vitals_dict={
                "heart_rate": 142,
                "systolic_bp": 178,
                "diastolic_bp": 110,
                "spo2": 87.5,
                "temp_c": 37.0,
                "resp_rate": 30
            }
        )

        # 3. AI Triage Assessment
        assessment = self.ml_engine.predict_triage(patient.age, patient.vitals, patient.chief_complaint)
        patient.update_assessment(assessment)

        self.assertEqual(assessment.urgency_level, UrgencyLevel.CATEGORY_1_RESUSCITATION)
        self.assertTrue(len(assessment.detected_red_flags) > 0)

        # 4. Verify Prioritized Queue
        queue = self.patient_mgr.get_prioritized_queue()
        self.assertTrue(len(queue) > 0)
        self.assertEqual(queue[0].patient_id, patient.patient_id)

        # 5. Doctor Examination & Status Change
        doc_token = self.auth_mgr.authenticate("dr_smith", "DoctorPass123!")
        self.auth_mgr.enforce_role(doc_token.token, [self.auth_mgr._users["dr_smith"].role])
        updated_patient = self.patient_mgr.update_patient_status(patient.patient_id, "In Treatment", doc_token.username)
        self.assertEqual(updated_patient.status, "In Treatment")

        # 6. Analytics Verification
        summary = self.analytics_engine.generate_department_summary()
        self.assertGreaterEqual(summary["total_encounters"], 1)


if __name__ == "__main__":
    unittest.main()
