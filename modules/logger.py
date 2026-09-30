"""
Logging and Performance Audit Module
Student Name: Shambhavi Holkar | Reg No: 26BAI10454
"""

import os
import time
import logging
from functools import wraps

# Ensure log directory exists
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "clinical_pulse.log")

# Configure custom logger
logger = logging.getLogger("ClinicalPulseAI")
logger.setLevel(logging.INFO)

if not logger.handlers:
    # File Handler
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s:%(module)s:%(lineno)d] - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        "[%(levelname)s] %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)


def audit_log(event_type: str, user_id: str, details: str):
    """
    Records security and operational audit events into system log.
    """
    log_msg = f"AUDIT | Event: {event_type} | User: {user_id} | Details: {details}"
    logger.info(log_msg)


def measure_performance(func):
    """
    Decorator to measure execution latency of critical clinical modules.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        logger.debug(f"PERF | Function '{func.__name__}' executed in {elapsed_ms:.2f} ms")
        return result
    return wrapper
