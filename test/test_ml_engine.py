"""
Unit Tests for ML Triage Engine
Student Name: Shambhavi Holkar | Reg No: 26BAI10454
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.modules.ml_triage_engine import MLTriageEngine
from src.models.triage_model import VitalSigns, UrgencyLevel


class TestMLTriageEngine:

    @pytest.fixture
    def ml_engine(self):
        return MLTriageEngine()

    def test_normal_patient_triage(self, ml_engine):
        vitals = VitalSigns(
            heart_rate=72,
            systolic_bp=120,
            diastolic_bp=80,
            spo2=98.5,
            temp_c=36.8,
            resp_rate=16
        )
        assessment = ml_engine.predict_triage(age=30, vitals=vitals, chief_complaint="Minor routine checkup")
        
        assert assessment.urgency_level in [
            UrgencyLevel.CATEGORY_3_URGENT,
            UrgencyLevel.CATEGORY_4_LESS_URGENT,
            UrgencyLevel.CATEGORY_5_NON_URGENT
        ]
        assert assessment.composite_score <= 60.0
        assert len(assessment.detected_red_flags) == 0

    def test_critical_hypoxia_red_flag_override(self, ml_engine):
        vitals = VitalSigns(
            heart_rate=110,
            systolic_bp=110,
            diastolic_bp=70,
            spo2=86.0,  # Critical hypoxia (< 90%)
            temp_c=37.0,
            resp_rate=28
        )
        assessment = ml_engine.predict_triage(age=55, vitals=vitals, chief_complaint="Difficulty breathing")

        assert assessment.urgency_level == UrgencyLevel.CATEGORY_1_RESUSCITATION
        assert assessment.composite_score >= 80.0
        assert any("CRITICAL HYPOXIA" in flag for flag in assessment.detected_red_flags)

    def test_symptom_nlp_extraction(self, ml_engine):
        score, flags = ml_engine.extract_symptom_score("Patient complains of crushing chest pain and stroke symptoms")
        assert score > 1.5
        assert any("Chest Pain" in f for f in flags)
        assert any("Stroke" in f for f in flags)
