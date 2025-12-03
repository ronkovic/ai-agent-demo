"""Tests for authentication module."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from jose import jwt

from agent_platform.auth import AuthError, extract_user_id, verify_supabase_token
from agent_platform.core.config import settings


class TestJWTVerification:
    """Tests for JWT token verification."""

    @pytest.fixture
    def valid_payload(self) -> dict:
        """Create a valid JWT payload."""
        return {
            "sub": "12345678-1234-1234-1234-123456789012",
            "email": "test@example.com",
            "aud": "authenticated",
            "role": "authenticated",
            "exp": int((datetime.now(UTC) + timedelta(hours=1)).timestamp()),
            "iat": int(datetime.now(UTC).timestamp()),
        }

    @pytest.fixture
    def jwt_secret(self) -> str:
        """Get or create a test JWT secret."""
        return "test-jwt-secret-for-testing-only"

    def test_verify_valid_token(
        self, valid_payload: dict, jwt_secret: str, monkeypatch
    ):
        """Test that a valid token is verified successfully."""
        monkeypatch.setattr(settings, "supabase_jwt_secret", jwt_secret)

        token = jwt.encode(valid_payload, jwt_secret, algorithm="HS256")
        result = verify_supabase_token(token)

        assert result["sub"] == valid_payload["sub"]
        assert result["email"] == valid_payload["email"]

    def test_verify_expired_token(
        self, valid_payload: dict, jwt_secret: str, monkeypatch
    ):
        """Test that an expired token raises AuthError."""
        monkeypatch.setattr(settings, "supabase_jwt_secret", jwt_secret)

        # Set expiration to past
        valid_payload["exp"] = int(
            (datetime.now(UTC) - timedelta(hours=1)).timestamp()
        )
        token = jwt.encode(valid_payload, jwt_secret, algorithm="HS256")

        with pytest.raises(AuthError) as exc_info:
            verify_supabase_token(token)

        assert "expired" in exc_info.value.message.lower()
        assert exc_info.value.status_code == 401

    def test_verify_invalid_signature(
        self, valid_payload: dict, jwt_secret: str, monkeypatch
    ):
        """Test that a token with invalid signature raises AuthError."""
        monkeypatch.setattr(settings, "supabase_jwt_secret", jwt_secret)

        # Encode with different secret
        token = jwt.encode(valid_payload, "wrong-secret", algorithm="HS256")

        with pytest.raises(AuthError) as exc_info:
            verify_supabase_token(token)

        assert "invalid" in exc_info.value.message.lower()
        assert exc_info.value.status_code == 401

    def test_verify_missing_secret(self, valid_payload: dict, monkeypatch):
        """Test that missing JWT secret raises AuthError with 500."""
        monkeypatch.setattr(settings, "supabase_jwt_secret", "")

        token = jwt.encode(valid_payload, "any-secret", algorithm="HS256")

        with pytest.raises(AuthError) as exc_info:
            verify_supabase_token(token)

        assert "not configured" in exc_info.value.message.lower()
        assert exc_info.value.status_code == 500

    def test_verify_malformed_token(self, jwt_secret: str, monkeypatch):
        """Test that a malformed token raises AuthError."""
        monkeypatch.setattr(settings, "supabase_jwt_secret", jwt_secret)

        with pytest.raises(AuthError) as exc_info:
            verify_supabase_token("not.a.valid.token")

        assert exc_info.value.status_code == 401


class TestExtractUserId:
    """Tests for extracting user ID from JWT payload."""

    def test_extract_valid_user_id(self):
        """Test extracting a valid user ID."""
        payload = {"sub": "12345678-1234-1234-1234-123456789012"}
        result = extract_user_id(payload)

        assert isinstance(result, UUID)
        assert str(result) == "12345678-1234-1234-1234-123456789012"

    def test_extract_missing_sub(self):
        """Test that missing sub claim raises AuthError."""
        payload = {"email": "test@example.com"}

        with pytest.raises(AuthError) as exc_info:
            extract_user_id(payload)

        assert "sub claim" in exc_info.value.message.lower()
        assert exc_info.value.status_code == 401

    def test_extract_invalid_uuid(self):
        """Test that invalid UUID format raises AuthError."""
        payload = {"sub": "not-a-uuid"}

        with pytest.raises(AuthError) as exc_info:
            extract_user_id(payload)

        assert "invalid" in exc_info.value.message.lower()
        assert exc_info.value.status_code == 401
