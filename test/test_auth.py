"""
Unit Tests for Authentication and RBAC Module
Student Name: Shambhavi Holkar | Reg No: 26BAI10454
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.modules.auth_manager import AuthManager
from src.models.user_model import UserRole, User
from src.utils.validators import ValidationError


class TestAuthManager:

    @pytest.fixture
    def auth_mgr(self):
        return AuthManager()

    def test_default_users_seeded(self, auth_mgr):
        token = auth_mgr.authenticate("admin", "Admin123!")
        assert token is not None
        assert token.username == "admin"
        assert token.role == UserRole.ADMIN

    def test_register_new_user(self, auth_mgr):
        new_user = auth_mgr.register_user("nurse_jane", "JanePass123!", "Triage Nurse")
        assert new_user.username == "nurse_jane"
        assert new_user.role == UserRole.TRIAGE_NURSE

        # Authenticate newly registered user
        token = auth_mgr.authenticate("nurse_jane", "JanePass123!")
        assert token.role == UserRole.TRIAGE_NURSE

    def test_duplicate_username_fails(self, auth_mgr):
        with pytest.raises(ValidationError) as exc_info:
            auth_mgr.register_user("admin", "NewPass123!", "Clinician")
        assert "already exists" in str(exc_info.value)

    def test_invalid_password_authentication(self, auth_mgr):
        with pytest.raises(ValidationError) as exc_info:
            auth_mgr.authenticate("admin", "WrongPassword!")
        assert "Invalid username or password" in str(exc_info.value)

    def test_rbac_enforcement(self, auth_mgr):
        nurse_token = auth_mgr.authenticate("nurse_sarah", "NursePass123!")
        
        # Nurse should be allowed for TRIAGE_NURSE role
        validated = auth_mgr.enforce_role(nurse_token.token, [UserRole.TRIAGE_NURSE, UserRole.ADMIN])
        assert validated.username == "nurse_sarah"

        # Nurse should be denied for CLINICIAN role
        with pytest.raises(ValidationError) as exc_info:
            auth_mgr.enforce_role(nurse_token.token, [UserRole.CLINICIAN])
        assert "Access Denied" in str(exc_info.value)
