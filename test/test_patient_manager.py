"""
Unit Tests for Patient Record Manager and CRUD Operations
Student Name: Shambhavi Holkar | Reg No: 26BAI10454
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.modules.patient_manager import PatientManager
from src.modules.ml_triage_engine import MLTriageEngine
from src.models.triage_model import UrgencyLevel
from src.utils.validators import ValidationError


class TestPatientManager:

    @pytest.fixture
    def pm(self):
        return PatientManager()

    @pytest.fixture
    def ml_engine(self):
        return MLTriageEngine()

    def test_create_and_get_patient(self, pm):
        vitals = {"heart_rate": 80, "systolic_bp": 120, "diastolic_bp": 80, "spo2": 98.0, "temp_c": 36.6, "resp_rate": 18}
        patient = pm.create_patient("John Doe", 40, "Male", "Headache", vitals)
        
        assert patient.patient_id.startswith("PAT-")
        assert patient.name == "John Doe"

        retrieved = pm.get_patient(patient.patient_id)
        assert retrieved.name == "John Doe"

    def test_invalid_vital_signs_rejected(self, pm):
        vitals = {"heart_rate": 350, "systolic_bp": 120, "diastolic_bp": 80, "spo2": 98.0, "temp_c": 36.6, "resp_rate": 18}
        with pytest.raises(ValidationError) as exc_info:
            pm.create_patient("Jane Doe", 30, "Female", "Fever", vitals)
        assert "physiological range" in str(exc_info.value)

    def test_prioritized_queue_sorting(self, pm, ml_engine):
        # Patient 1: Low risk
        p1 = pm.create_patient("Patient Mild", 25, "Female", "Cold", {"heart_rate": 70, "systolic_bp": 115, "diastolic_bp": 75, "spo2": 99.0, "temp_c": 36.5, "resp_rate": 14})
        a1 = ml_engine.predict_triage(p1.age, p1.vitals, p1.chief_complaint)
        p1.update_assessment(a1)

        # Patient 2: High risk cardiac emergency
        p2 = pm.create_patient("Patient Severe", 65, "Male", "Chest pain and stroke", {"heart_rate": 130, "systolic_bp": 170, "diastolic_bp": 100, "spo2": 88.0, "temp_c": 37.2, "resp_rate": 28})
        a2 = ml_engine.predict_triage(p2.age, p2.vitals, p2.chief_complaint)
        p2.update_assessment(a2)

        queue = pm.get_prioritized_queue()
        assert len(queue) == 2
        # Severe patient should be first in queue
        assert queue[0].patient_id == p2.patient_id
