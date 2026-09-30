"""
Input Validation and Data Sanitization Module
Student Name: Shambhavi Holkar | Reg No: 26BAI10454
"""

import re
from typing import Tuple, Dict, Any, Union


class ValidationError(Exception):
    """Custom exception raised when clinical or user input validation fails."""
    pass


class ClinicalValidator:
    """
    Provides clinical boundary checks, regex sanitization, and security validations.
    """

    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Sanitizes text inputs by removing malicious characters and leading/trailing spaces.
        """
        if not isinstance(text, str):
            raise ValidationError("Input must be a string.")
        # Strip script tags or SQL special tokens
        clean = re.sub(r"<[^>]*>", "", text)
        clean = re.sub(r"[;'\"]", "", clean)
        return clean.strip()

    @staticmethod
    def validate_username(username: str) -> str:
        """
        Validates username length and alphanumeric character constraints.
        """
        sanitized = ClinicalValidator.sanitize_text(username)
        if not re.match(r"^[a-zA-Z0-9_.]{3,30}$", sanitized):
            raise ValidationError(
                "Username must be 3-30 characters long and contain only letters, numbers, dots, or underscores."
            )
        return sanitized

    @staticmethod
    def validate_password(password: str) -> bool:
        """
        Validates password strength (min 8 chars, 1 letter, 1 number).
        """
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
            raise ValidationError("Password must contain both letters and digits.")
        return True

    @staticmethod
    def validate_vitals(vitals: Dict[str, Union[int, float, str]]) -> Dict[str, Any]:
        """
        Validates medical vital sign ranges and data formats.
        Expected keys: heart_rate, systolic_bp, diastolic_bp, spo2, temp_c, resp_rate
        """
        required_keys = ["heart_rate", "systolic_bp", "diastolic_bp", "spo2", "temp_c", "resp_rate"]
        for key in required_keys:
            if key not in vitals or vitals[key] is None:
                raise ValidationError(f"Missing required vital parameter: {key}")

        try:
            hr = float(vitals["heart_rate"])
            sbp = float(vitals["systolic_bp"])
            dbp = float(vitals["diastolic_bp"])
            spo2 = float(vitals["spo2"])
            temp = float(vitals["temp_c"])
            rr = float(vitals["resp_rate"])
        except (ValueError, TypeError):
            raise ValidationError("All vital signs must be valid numerical values.")

        if not (20 <= hr <= 250):
            raise ValidationError(f"Heart rate ({hr} bpm) is out of physiological range (20-250 bpm).")
        if not (40 <= sbp <= 280):
            raise ValidationError(f"Systolic BP ({sbp} mmHg) is out of valid range (40-280 mmHg).")
        if not (20 <= dbp <= 200):
            raise ValidationError(f"Diastolic BP ({dbp} mmHg) is out of valid range (20-200 mmHg).")
        if dbp >= sbp:
            raise ValidationError("Diastolic BP cannot be greater than or equal to Systolic BP.")
        if not (50.0 <= spo2 <= 100.0):
            raise ValidationError(f"SpO2 ({spo2}%) is out of valid physiological range (50-100%).")
        if not (30.0 <= temp <= 45.0):
            raise ValidationError(f"Body temperature ({temp}°C) is out of valid range (30-45°C).")
        if not (4 <= rr <= 60):
            raise ValidationError(f"Respiratory rate ({rr} bpm) is out of valid range (4-60 bpm).")

        return {
            "heart_rate": int(hr),
            "systolic_bp": int(sbp),
            "diastolic_bp": int(dbp),
            "spo2": float(spo2),
            "temp_c": round(temp, 1),
            "resp_rate": int(rr)
        }

    @staticmethod
    def validate_patient_demographics(name: str, age: int, gender: str) -> Tuple[str, int, str]:
        """
        Validates demographic inputs.
        """
        clean_name = ClinicalValidator.sanitize_text(name)
        if len(clean_name) < 2:
            raise ValidationError("Patient name must be at least 2 characters long.")
        if not (0 <= age <= 120):
            raise ValidationError("Patient age must be between 0 and 120 years.")
        clean_gender = gender.strip().capitalize()
        if clean_gender not in ["Male", "Female", "Other"]:
            raise ValidationError("Gender must be 'Male', 'Female', or 'Other'.")

        return clean_name, age, clean_gender
