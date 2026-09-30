"""
Patient Record CRUD and Queue Management Module
Student Name: Shambhavi Holkar | Reg No: 26BAI10454
"""

import json
import os
from typing import Dict, List, Optional
from src.models.triage_model import PatientRecord, VitalSigns, UrgencyLevel
from src.utils.validators import ClinicalValidator, ValidationError
from src.utils.logger import logger, audit_log, measure_performance


class PatientManager:
    """
    Handles Patient Encounter CRUD lifecycle, active triage queues, and data persistence.
    """

    def __init__(self, data_file: Optional[str] = None):
        self._patients: Dict[str, PatientRecord] = {}
        self.data_file = data_file
        if data_file and os.path.exists(data_file):
            self.load_from_file(data_file)

    @measure_performance
    def create_patient(
        self,
        name: str,
        age: int,
        gender: str,
        chief_complaint: str,
        vitals_dict: dict
    ) -> PatientRecord:
        """
        Creates and registers a new patient encounter after input validation.
        """
        clean_name, valid_age, clean_gender = ClinicalValidator.validate_patient_demographics(name, age, gender)
        clean_complaint = ClinicalValidator.sanitize_text(chief_complaint)
        validated_vitals = ClinicalValidator.validate_vitals(vitals_dict)

        vitals_obj = VitalSigns(**validated_vitals)
        patient = PatientRecord(
            name=clean_name,
            age=valid_age,
            gender=clean_gender,
            chief_complaint=clean_complaint,
            vitals=vitals_obj
        )

        self._patients[patient.patient_id] = patient
        logger.info(f"PATIENT_CREATED | ID: {patient.patient_id} | Name: {patient.name}")
        return patient

    def get_patient(self, patient_id: str) -> PatientRecord:
        """
        Retrieves a patient record by ID.
        """
        patient = self._patients.get(patient_id.upper())
        if not patient:
            raise ValidationError(f"Patient with ID '{patient_id}' not found.")
        return patient

    def list_all_patients(self) -> List[PatientRecord]:
        """
        Returns all registered patient records.
        """
        return list(self._patients.values())

    def update_patient_vitals(self, patient_id: str, new_vitals_dict: dict) -> PatientRecord:
        """
        Updates patient vital signs and logs the change.
        """
        patient = self.get_patient(patient_id)
        validated_vitals = ClinicalValidator.validate_vitals(new_vitals_dict)
        patient.vitals = VitalSigns(**validated_vitals)
        patient.updated_at = patient.vitals.to_dict()  # timestamp updated
        logger.info(f"PATIENT_UPDATED | Vitals refreshed for Patient ID: {patient_id}")
        return patient

    def update_patient_status(self, patient_id: str, new_status: str, doctor_name: Optional[str] = None) -> PatientRecord:
        """
        Updates clinical encounter status (e.g., 'In Treatment', 'Discharged').
        """
        patient = self.get_patient(patient_id)
        valid_statuses = ["Triage Pending", "Waiting for Doctor", "In Treatment", "Discharged"]
        if new_status not in valid_statuses:
            raise ValidationError(f"Invalid status '{new_status}'. Allowed: {valid_statuses}")

        patient.status = new_status
        if doctor_name:
            patient.assigned_doctor = doctor_name
        logger.info(f"STATUS_CHANGE | Patient: {patient_id} -> Status: {new_status}")
        return patient

    def delete_patient(self, patient_id: str) -> bool:
        """
        Removes a patient record from the system.
        """
        patient = self.get_patient(patient_id)
        del self._patients[patient.patient_id]
        logger.info(f"PATIENT_DELETED | ID: {patient_id}")
        return True

    def get_prioritized_queue(self) -> List[PatientRecord]:
        """
        Returns active waiting patients sorted dynamically by Urgency Level and Composite Risk Score.
        High-risk resuscitation cases (Urgency 1) appear at top of queue.
        """
        waiting_patients = [
            p for p in self._patients.values()
            if p.status in ["Triage Pending", "Waiting for Doctor"] and p.assessment is not None
        ]

        # Sort primary by Urgency Level (ascending: 1 to 5), secondary by Composite Risk Score (descending: 100 to 0)
        sorted_queue = sorted(
            waiting_patients,
            key=lambda p: (p.assessment.urgency_level.value, -p.assessment.composite_score)
        )
        return sorted_queue

    def search_patients(self, query: str) -> List[PatientRecord]:
        """
        Searches patient records by name or patient ID.
        """
        clean_q = query.strip().lower()
        results = [
            p for p in self._patients.values()
            if clean_q in p.name.lower() or clean_q in p.patient_id.lower()
        ]
        return results

    def save_to_file(self, file_path: str):
        """
        Serializes all patient records to a JSON file.
        """
        data = [p.to_dict() for p in self._patients.values()]
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info(f"DATA_SAVED | Exported {len(data)} patient records to '{file_path}'")

    def load_from_file(self, file_path: str):
        """
        Loads patient records from a JSON file.
        """
        if not os.path.exists(file_path):
            return
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for item in data:
            vitals = VitalSigns(**item["vitals"])
            patient = PatientRecord(
                name=item["name"],
                age=item["age"],
                gender=item["gender"],
                chief_complaint=item["chief_complaint"],
                vitals=vitals,
                patient_id=item["patient_id"]
            )
            patient.status = item.get("status", "Triage Pending")
            patient.assigned_doctor = item.get("assigned_doctor")
            self._patients[patient.patient_id] = patient
        logger.info(f"DATA_LOADED | Imported {len(data)} patient records from '{file_path}'")
