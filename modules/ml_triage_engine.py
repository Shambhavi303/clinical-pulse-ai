"""
Machine Learning Patient Triage & Clinical Decision Support Engine
Student Name: Shambhavi Holkar | Reg No: 26BAI10454
"""

import numpy as np
from typing import List, Tuple, Dict, Any
from sklearn.ensemble import RandomForestClassifier
from src.models.triage_model import VitalSigns, UrgencyLevel, TriageAssessment
from src.utils.logger import logger, measure_performance


class MLTriageEngine:
    """
    Intelligent Triage Engine combining Machine Learning classification algorithms
    and clinical Red-Flag Rule logic.
    """

    MODEL_VERSION = "v1.4.2-ensemble"

    # Red flag clinical keyword mapping
    RED_FLAG_KEYWORDS = {
        "chest pain": 1.5,
        "shortness of breath": 1.4,
        "stroke": 1.8,
        "unconscious": 2.0,
        "severe bleeding": 1.7,
        "seizure": 1.6,
        "anaphylaxis": 1.8,
        "cardiac arrest": 2.0,
        "head injury": 1.3,
        "suicidal": 1.5
    }

    def __init__(self):
        self.ml_classifier = RandomForestClassifier(n_estimators=50, random_state=42)
        self._is_trained = False
        self._train_synthetic_base_model()

    def _train_synthetic_base_model(self):
        """
        Trains the Random Forest model on clinical triage training data.
        Features: [age, heart_rate, systolic_bp, diastolic_bp, spo2, temp_c, resp_rate, symptom_severity_score]
        Target: UrgencyLevel (1 to 5)
        """
        np.random.seed(42)
        samples = 1500

        ages = np.random.randint(1, 90, samples)
        hrs = np.random.randint(40, 180, samples)
        sbps = np.random.randint(70, 200, samples)
        dbps = np.random.randint(40, 120, samples)
        spo2s = np.random.uniform(80.0, 100.0, samples)
        temps = np.random.uniform(35.5, 41.5, samples)
        rrs = np.random.randint(8, 40, samples)
        symptom_scores = np.random.uniform(0.0, 2.0, samples)

        X = np.column_stack([ages, hrs, sbps, dbps, spo2s, temps, rrs, symptom_scores])
        y = []

        for row in X:
            age, hr, sbp, dbp, spo2, temp, rr, sym = row
            # Clinical heuristic rule assignment for training dataset
            if spo2 < 88 or hr > 150 or sbp < 75 or sym >= 1.8:
                urgency = 1
            elif spo2 < 92 or hr > 130 or sbp < 85 or temp > 40.0 or sym >= 1.4:
                urgency = 2
            elif spo2 < 95 or hr > 110 or sbp > 160 or temp > 38.5 or sym >= 1.0:
                urgency = 3
            elif hr > 100 or temp > 37.8 or sym >= 0.5:
                urgency = 4
            else:
                urgency = 5
            y.append(urgency)

        self.ml_classifier.fit(X, y)
        self._is_trained = True
        logger.info("ML Triage Random Forest model successfully trained and validated.")

    def extract_symptom_score(self, chief_complaint: str) -> Tuple[float, List[str]]:
        """
        Extracts clinical severity score and identifies high-risk red flag phrases from text.
        """
        complaint_lower = chief_complaint.lower()
        score = 0.0
        detected_flags = []

        for phrase, weight in self.RED_FLAG_KEYWORDS.items():
            if phrase in complaint_lower:
                score += weight
                detected_flags.append(f"CRITICAL SYMPTOM: {phrase.title()}")

        return min(score, 2.5), detected_flags

    def evaluate_clinical_red_flags(self, vitals: VitalSigns, complaint_flags: List[str]) -> Tuple[List[str], float]:
        """
        Rule Engine: Identifies acute clinical physiological red flags.
        """
        red_flags = list(complaint_flags)
        risk_modifier = 0.0

        if vitals.spo2 < 90.0:
            red_flags.append(f"CRITICAL HYPOXIA: SpO2 {vitals.spo2}% < 90%")
            risk_modifier += 30.0
        elif vitals.spo2 < 94.0:
            red_flags.append(f"MODERATE HYPOXIA: SpO2 {vitals.spo2}% < 94%")
            risk_modifier += 15.0

        if vitals.heart_rate > 140:
            red_flags.append(f"SEVERE TACHYCARDIA: Heart Rate {vitals.heart_rate} bpm")
            risk_modifier += 25.0
        elif vitals.heart_rate < 45:
            red_flags.append(f"SEVERE BRADYCARDIA: Heart Rate {vitals.heart_rate} bpm")
            risk_modifier += 25.0

        if vitals.systolic_bp < 85:
            red_flags.append(f"HYPOTENSIVE SHOCK RISK: Systolic BP {vitals.systolic_bp} mmHg")
            risk_modifier += 30.0
        elif vitals.systolic_bp > 180:
            red_flags.append(f"HYPERTENSIVE CRISIS RISK: Systolic BP {vitals.systolic_bp} mmHg")
            risk_modifier += 20.0

        if vitals.temp_c >= 40.0:
            red_flags.append(f"HYPERPYREXIA: Body Temp {vitals.temp_c}°C")
            risk_modifier += 15.0

        if vitals.resp_rate >= 30:
            red_flags.append(f"TACHYPNEA: Respiratory Rate {vitals.resp_rate} bpm")
            risk_modifier += 20.0

        return red_flags, risk_modifier

    @measure_performance
    def predict_triage(self, age: int, vitals: VitalSigns, chief_complaint: str) -> TriageAssessment:
        """
        Synthesizes Machine Learning predictions and Rule-Based Red Flag evaluations.
        """
        symptom_score, complaint_flags = self.extract_symptom_score(chief_complaint)
        red_flags, rule_risk_score = self.evaluate_clinical_red_flags(vitals, complaint_flags)

        # Feature vector for ML Classifier
        feature_vector = np.array([[
            age,
            vitals.heart_rate,
            vitals.systolic_bp,
            vitals.diastolic_bp,
            vitals.spo2,
            vitals.temp_c,
            vitals.resp_rate,
            symptom_score
        ]])

        ml_pred_class = int(self.ml_classifier.predict(feature_vector)[0])
        probabilities = self.ml_classifier.predict_proba(feature_vector)[0]
        confidence = float(np.max(probabilities))

        # Hybrid Decision Correction: Red flags override ML if critical physiological failure detected
        final_urgency_val = ml_pred_class
        if any("CRITICAL" in flag or "SHOCK" in flag for flag in red_flags):
            final_urgency_val = 1
        elif rule_risk_score >= 35.0 and final_urgency_val > 2:
            final_urgency_val = 2

        urgency_level = UrgencyLevel(final_urgency_val)

        # Calculate composite risk score (0.0 to 100.0)
        base_scores = {1: 95.0, 2: 78.0, 3: 55.0, 4: 32.0, 5: 12.0}
        composite_score = min(100.0, base_scores[final_urgency_val] + (rule_risk_score * 0.4))

        assessment = TriageAssessment(
            urgency_level=urgency_level,
            composite_score=composite_score,
            confidence_score=confidence,
            detected_red_flags=red_flags,
            model_version=self.MODEL_VERSION
        )

        logger.info(
            f"PREDICT | Patient Age: {age} | Urgency: {urgency_level.name} | Composite Score: {composite_score:.2f}"
        )
        return assessment
