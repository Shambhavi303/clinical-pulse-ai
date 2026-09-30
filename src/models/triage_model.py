"""
Patient Encounter and Triage Assessment Data Models
Student Name: Shambhavi Holkar | Reg No: 26BAI10454
"""

import uuid
from enum import IntEnum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional


class UrgencyLevel(IntEnum):
    CATEGORY_1_RESUSCITATION = 1  # Immediate life-threatening condition
    CATEGORY_2_EMERGENCY = 2      # Imminent threat to life or limb
    CATEGORY_3_URGENT = 3         # Potential life threat or severe pain
    CATEGORY_4_LESS_URGENT = 4    # Moderate distress or complexity
    CATEGORY_5_NON_URGENT = 5     # Minor or chronic condition

    @property
    def label(self) -> str:
        labels = {
            1: "Resuscitation (Immediate)",
            2: "Emergency (15 mins)",
            3: "Urgent (30 mins)",
            4: "Less Urgent (60 mins)",
            5: "Non-Urgent (120 mins)"
        }
        return labels[self.value]


@dataclass
class VitalSigns:
    heart_rate: int          # bpm
    systolic_bp: int         # mmHg
    diastolic_bp: int        # mmHg
    spo2: float              # percentage
    temp_c: float            # Celsius
    resp_rate: int           # breaths/min

    def to_dict(self) -> Dict[str, Any]:
        return {
            "heart_rate": self.heart_rate,
            "systolic_bp": self.systolic_bp,
            "diastolic_bp": self.diastolic_bp,
            "spo2": self.spo2,
            "temp_c": self.temp_c,
            "resp_rate": self.resp_rate
        }


@dataclass
class TriageAssessment:
    urgency_level: UrgencyLevel
    composite_score: float
    confidence_score: float
    detected_red_flags: List[str]
    model_version: str
    assessed_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "urgency_level": self.urgency_level.value,
            "urgency_label": self.urgency_level.label,
            "composite_score": round(self.composite_score, 2),
            "confidence_score": round(self.confidence_score, 4),
            "detected_red_flags": self.detected_red_flags,
            "model_version": self.model_version,
            "assessed_at": self.assessed_at
        }


class PatientRecord:
    """
    Represents an active patient encounter in the clinical triage system.
    """

    def __init__(
        self,
        name: str,
        age: int,
        gender: str,
        chief_complaint: str,
        vitals: VitalSigns,
        patient_id: Optional[str] = None
    ):
        self.patient_id = patient_id or f"PAT-{uuid.uuid4().hex[:8].upper()}"
        self.name = name
        self.age = age
        self.gender = gender
        self.chief_complaint = chief_complaint
        self.vitals = vitals
        self.assessment: Optional[TriageAssessment] = None
        self.status: str = "Triage Pending"  # Triage Pending, Waiting for Doctor, In Treatment, Discharged
        self.created_at: str = datetime.now().isoformat()
        self.updated_at: str = datetime.now().isoformat()
        self.assigned_doctor: Optional[str] = None

    def update_assessment(self, assessment: TriageAssessment):
        self.assessment = assessment
        self.status = "Waiting for Doctor"
        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "patient_id": self.patient_id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "chief_complaint": self.chief_complaint,
            "vitals": self.vitals.to_dict(),
            "assessment": self.assessment.to_dict() if self.assessment else None,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "assigned_doctor": self.assigned_doctor
        }
