"""JWT token verification for Supabase authentication."""

from uuid import UUID

from jose import JWTError, jwt

from ..core.config import settings


class AuthError(Exception):
    """Authentication error."""

    def __init__(self, message: str, status_code: int = 401):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def verify_supabase_token(token: str) -> dict:
    """Verify a Supabase JWT token.

    Args:
        token: The JWT token to verify.

    Returns:
        The decoded token payload.

    Raises:
        AuthError: If the token is invalid or expired.
    """
    if not settings.supabase_jwt_secret:
        raise AuthError("JWT secret not configured", 500)

    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthError("Token has expired")
    except JWTError as e:
        raise AuthError(f"Invalid token: {e}")


def extract_user_id(payload: dict) -> UUID:
    """Extract user ID from JWT payload.

    Args:
        payload: The decoded JWT payload.

    Returns:
        The user ID as a UUID.

    Raises:
        AuthError: If the payload doesn't contain a valid user ID.
    """
    sub = payload.get("sub")
    if not sub:
        raise AuthError("Token missing user ID (sub claim)")

    try:
        return UUID(sub)
    except ValueError:
        raise AuthError("Invalid user ID format in token")


def create_mock_token_payload(user_id: UUID, email: str = "dev@example.com") -> dict:
    """Create a mock token payload for development/testing.

    Args:
        user_id: The user ID to include in the payload.
        email: The email to include in the payload.

    Returns:
        A mock JWT payload dict.
    """
    return {
        "sub": str(user_id),
        "email": email,
        "aud": "authenticated",
        "role": "authenticated",
    }
