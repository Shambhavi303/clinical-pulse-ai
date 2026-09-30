"""
Unit Tests for Analytics Engine and Report Exports
Student Name: Shambhavi Holkar | Reg No: 26BAI10454
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.modules.patient_manager import PatientManager
from src.modules.ml_triage_engine import MLTriageEngine
from src.modules.analytics_engine import AnalyticsEngine


class TestAnalyticsEngine:

    @pytest.fixture
    def setup_system(self, tmp_path):
        pm = PatientManager()
        ml = MLTriageEngine()
        analytics = AnalyticsEngine(pm)

        # Create 2 sample patients
        p1 = pm.create_patient("Alice", 30, "Female", "Flu symptoms", {"heart_rate": 80, "systolic_bp": 120, "diastolic_bp": 80, "spo2": 98.0, "temp_c": 38.0, "resp_rate": 18})
        p1.update_assessment(ml.predict_triage(p1.age, p1.vitals, p1.chief_complaint))

        p2 = pm.create_patient("Bob", 60, "Male", "Unconscious and severe bleeding", {"heart_rate": 145, "systolic_bp": 80, "diastolic_bp": 50, "spo2": 85.0, "temp_c": 36.0, "resp_rate": 32})
        p2.update_assessment(ml.predict_triage(p2.age, p2.vitals, p2.chief_complaint))

        return pm, analytics, tmp_path

    def test_analytics_metrics_computation(self, setup_system):
        _, analytics, _ = setup_system
        summary = analytics.generate_department_summary()

        assert summary["total_encounters"] == 2
        assert summary["assessed_patients"] == 2
        assert summary["critical_patient_count"] >= 1
        assert summary["average_composite_risk_score"] > 0

    def test_ascii_dashboard_formatting(self, setup_system):
        _, analytics, _ = setup_system
        dashboard = analytics.format_ascii_dashboard()
        assert "CLINICALPULSE AI - REAL-TIME DASHBOARD" in dashboard
        assert "URGENCY CATEGORY DISTRIBUTION" in dashboard

    def test_export_reports(self, setup_system):
        _, analytics, tmp_path = setup_system
        csv_file = str(tmp_path / "test_report.csv")
        json_file = str(tmp_path / "test_summary.json")

        analytics.export_report_csv(csv_file)
        analytics.export_summary_json(json_file)

        assert os.path.exists(csv_file)
        assert os.path.exists(json_file)
        assert os.path.getsize(csv_file) > 0
        assert os.path.getsize(json_file) > 0
