"""
User and RBAC Data Models
Student Name: Shambhavi Holkar | Reg No: 26BAI10454
"""

import hashlib
import os
import secrets
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional


class UserRole(Enum):
    ADMIN = "Administrator"
    TRIAGE_NURSE = "Triage Nurse"
    CLINICIAN = "Clinician"

    @classmethod
    def from_string(cls, role_str: str) -> "UserRole":
        for role in cls:
            if role.value.lower() == role_str.lower() or role.name.lower() == role_str.lower():
                return role
        raise ValueError(f"Invalid user role: {role_str}")


@dataclass
class AuthToken:
    token: str
    username: str
    role: UserRole
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=8))

    def is_valid(self) -> bool:
        return datetime.now() < self.expires_at


class User:
    """
    Represents a system user with secure PBKDF2 password hashing and token generation.
    """

    def __init__(self, username: str, password_raw: str, role: UserRole, user_id: Optional[str] = None):
        self.user_id = user_id or f"USR-{secrets.token_hex(4).upper()}"
        self.username = username
        self.role = role
        self.salt = os.urandom(16).hex()
        self.password_hash = self.hash_password(password_raw, self.salt)
        self.created_at = datetime.now().isoformat()

    @staticmethod
    def hash_password(password: str, salt_hex: str) -> str:
        """
        Derives secure SHA256 PBKDF2 hash using 100,000 iterations.
        """
        salt_bytes = bytes.fromhex(salt_hex)
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt_bytes, 100000)
        return key.hex()

    def verify_password(self, password_raw: str) -> bool:
        """
        Verifies raw password against stored hash.
        """
        computed_hash = self.hash_password(password_raw, self.salt)
        return secrets.compare_digest(computed_hash, self.password_hash)

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "role": self.role.value,
            "salt": self.salt,
            "password_hash": self.password_hash,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        user = cls.__new__(cls)
        user.user_id = data["user_id"]
        user.username = data["username"]
        user.role = UserRole.from_string(data["role"])
        user.salt = data["salt"]
        user.password_hash = data["password_hash"]
        user.created_at = data.get("created_at", datetime.now().isoformat())
        return user
