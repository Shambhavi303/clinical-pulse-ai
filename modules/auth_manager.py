"""
Authentication and Role-Based Access Control Manager
Student Name: Shambhavi Holkar | Reg No: 26BAI10454
"""

from typing import Dict, Optional
from src.models.user_model import User, UserRole, AuthToken
from src.utils.validators import ClinicalValidator, ValidationError
from src.utils.logger import logger, audit_log, measure_performance


class AuthManager:
    """
    Manages in-memory user registry, authentication credentials, and session tokens.
    """

    def __init__(self):
        self._users: Dict[str, User] = {}
        self._active_tokens: Dict[str, AuthToken] = {}
        self._seed_default_users()

    def _seed_default_users(self):
        """Seeds initial default administrative and clinical staff accounts."""
        default_accounts = [
            ("admin", "Admin123!", UserRole.ADMIN),
            ("nurse_sarah", "NursePass123!", UserRole.TRIAGE_NURSE),
            ("dr_smith", "DoctorPass123!", UserRole.CLINICIAN)
        ]
        for username, password, role in default_accounts:
            user = User(username=username, password_raw=password, role=role)
            self._users[username.lower()] = user
        logger.info("Default system users successfully initialized.")

    @measure_performance
    def register_user(self, username: str, password_raw: str, role_str: str) -> User:
        """
        Registers a new user account with validated credentials and role.
        """
        valid_username = ClinicalValidator.validate_username(username)
        if valid_username.lower() in self._users:
            raise ValidationError(f"User with username '{username}' already exists.")

        ClinicalValidator.validate_password(password_raw)
        role = UserRole.from_string(role_str)

        new_user = User(username=valid_username, password_raw=password_raw, role=role)
        self._users[valid_username.lower()] = new_user

        audit_log("USER_REGISTER", valid_username, f"Registered new user with role {role.value}")
        return new_user

    @measure_performance
    def authenticate(self, username: str, password_raw: str) -> AuthToken:
        """
        Authenticates user credentials and returns a valid session AuthToken.
        """
        clean_username = username.strip().lower()
        user = self._users.get(clean_username)

        if not user or not user.verify_password(password_raw):
            audit_log("AUTH_FAILURE", clean_username, "Invalid username or password attempt.")
            raise ValidationError("Invalid username or password.")

        token_str = f"TK-{user.user_id}-{user.salt[:8]}"
        auth_token = AuthToken(token=token_str, username=user.username, role=user.role)
        self._active_tokens[token_str] = auth_token

        audit_log("AUTH_SUCCESS", user.username, f"Successfully logged in as {user.role.value}")
        return auth_token

    def validate_session(self, token_str: str) -> AuthToken:
        """
        Verifies session token existence and expiration status.
        """
        token = self._active_tokens.get(token_str)
        if not token or not token.is_valid():
            if token and token_str in self._active_tokens:
                del self._active_tokens[token_str]
            raise ValidationError("Session token expired or invalid. Please log in again.")
        return token

    def enforce_role(self, token_str: str, allowed_roles: list) -> AuthToken:
        """
        Enforces Role-Based Access Control (RBAC) rules.
        """
        token = self.validate_session(token_str)
        if token.role not in allowed_roles:
            audit_log(
                "PERMISSION_DENIED",
                token.username,
                f"Attempted unauthorized operation requiring {allowed_roles}"
            )
            raise ValidationError(f"Access Denied. Required role: {[r.value for r in allowed_roles]}")
        return token
