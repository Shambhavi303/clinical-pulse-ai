"""
Reporting, Analytics, and Data Visualization Module
Student Name: Shambhavi Holkar | Reg No: 26BAI10454
"""

import json
import csv
import os
from typing import Dict, List, Any
from src.modules.patient_manager import PatientManager
from src.models.triage_model import UrgencyLevel
from src.utils.logger import logger, measure_performance


class AnalyticsEngine:
    """
    Generates real-time clinical department performance statistics, risk category
    distribution summaries, and exportable audit reports.
    """

    def __init__(self, patient_manager: PatientManager):
        self.pm = patient_manager

    @measure_performance
    def generate_department_summary(self) -> Dict[str, Any]:
        """
        Computes key operational and clinical performance metrics.
        """
        all_patients = self.pm.list_all_patients()
        total_encounters = len(all_patients)

        if total_encounters == 0:
            return {
                "total_encounters": 0,
                "urgency_distribution": {},
                "status_breakdown": {},
                "average_risk_score": 0.0,
                "critical_patient_count": 0,
                "red_flag_prevalence": {}
            }

        urgency_counts = {level.name: 0 for level in UrgencyLevel}
        status_counts = {}
        total_risk = 0.0
        assessed_count = 0
        critical_count = 0
        red_flag_counts: Dict[str, int] = {}

        for p in all_patients:
            # Status breakdown
            status_counts[p.status] = status_counts.get(p.status, 0) + 1

            if p.assessment:
                assessed_count += 1
                urgency_name = p.assessment.urgency_level.name
                urgency_counts[urgency_name] = urgency_counts.get(urgency_name, 0) + 1
                total_risk += p.assessment.composite_score

                if p.assessment.urgency_level in [UrgencyLevel.CATEGORY_1_RESUSCITATION, UrgencyLevel.CATEGORY_2_EMERGENCY]:
                    critical_count += 1

                for flag in p.assessment.detected_red_flags:
                    red_flag_counts[flag] = red_flag_counts.get(flag, 0) + 1

        avg_risk = (total_risk / assessed_count) if assessed_count > 0 else 0.0

        metrics = {
            "total_encounters": total_encounters,
            "assessed_patients": assessed_count,
            "critical_patient_count": critical_count,
            "critical_percentage": round((critical_count / total_encounters) * 100.0, 2) if total_encounters > 0 else 0.0,
            "average_composite_risk_score": round(avg_risk, 2),
            "urgency_distribution": urgency_counts,
            "status_breakdown": status_counts,
            "top_red_flags": dict(sorted(red_flag_counts.items(), key=lambda item: item[1], reverse=True)[:5])
        }

        logger.info(f"ANALYTICS | Total: {total_encounters} | Critical: {critical_count} | Avg Risk: {avg_risk:.2f}")
        return metrics

    def format_ascii_dashboard(self) -> str:
        """
        Formats metrics into an ASCII terminal dashboard string.
        """
        summary = self.generate_department_summary()
        lines = [
            "==========================================================================",
            "                 CLINICALPULSE AI - REAL-TIME DASHBOARD                   ",
            "==========================================================================",
            f" Total Patient Encounters : {summary['total_encounters']}",
            f" Assessed by AI Triage   : {summary['assessed_patients']}",
            f" Critical Patient Count   : {summary['critical_patient_count']} ({summary['critical_percentage']}%)",
            f" Average Risk Score       : {summary['average_composite_risk_score']} / 100.0",
            "--------------------------------------------------------------------------",
            " URGENCY CATEGORY DISTRIBUTION:",
        ]

        dist = summary["urgency_distribution"]
        for cat, count in dist.items():
            bar = "#" * (count * 2)
            lines.append(f"  - {cat:<26}: {count:>3} {bar}")

        lines.append("--------------------------------------------------------------------------")
        lines.append(" ENCOUNTER STATUS BREAKDOWN:")
        for status, count in summary["status_breakdown"].items():
            lines.append(f"  - {status:<26}: {count}")

        lines.append("--------------------------------------------------------------------------")
        lines.append(" TOP DETECTED CLINICAL RED FLAGS:")
        if summary["top_red_flags"]:
            for flag, count in summary["top_red_flags"].items():
                lines.append(f"  * {flag}: {count} occurrence(s)")
        else:
            lines.append("  * None detected in active queue.")

        lines.append("==========================================================================")
        return "\n".join(lines)

    def export_report_csv(self, export_path: str) -> str:
        """
        Exports all patient triage records to a CSV file.
        """
        all_patients = self.pm.list_all_patients()
        os.makedirs(os.path.dirname(export_path) or ".", exist_ok=True)

        fieldnames = [
            "Patient_ID", "Name", "Age", "Gender", "Status",
            "Chief_Complaint", "Heart_Rate", "Systolic_BP", "Diastolic_BP",
            "SpO2", "Temp_C", "Resp_Rate", "Urgency_Level", "Composite_Score",
            "Assessed_At"
        ]

        with open(export_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for p in all_patients:
                row = {
                    "Patient_ID": p.patient_id,
                    "Name": p.name,
                    "Age": p.age,
                    "Gender": p.gender,
                    "Status": p.status,
                    "Chief_Complaint": p.chief_complaint,
                    "Heart_Rate": p.vitals.heart_rate,
                    "Systolic_BP": p.vitals.systolic_bp,
                    "Diastolic_BP": p.vitals.diastolic_bp,
                    "SpO2": p.vitals.spo2,
                    "Temp_C": p.vitals.temp_c,
                    "Resp_Rate": p.vitals.resp_rate,
                    "Urgency_Level": p.assessment.urgency_level.name if p.assessment else "N/A",
                    "Composite_Score": p.assessment.composite_score if p.assessment else "N/A",
                    "Assessed_At": p.assessment.assessed_at if p.assessment else "N/A"
                }
                writer.writerow(row)

        logger.info(f"EXPORT | CSV analytics report written to '{export_path}'")
        return export_path

    def export_summary_json(self, export_path: str) -> str:
        """
        Exports system analytical summary to JSON file.
        """
        summary = self.generate_department_summary()
        os.makedirs(os.path.dirname(export_path) or ".", exist_ok=True)
        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"EXPORT | JSON summary report written to '{export_path}'")
        return export_path
