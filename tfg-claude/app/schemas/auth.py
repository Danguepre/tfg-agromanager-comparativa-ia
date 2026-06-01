"""
Schemas de autenticación.
"""
from pydantic import BaseModel, EmailStr


class TokenResponse(BaseModel):
    """Respuesta de token JWT."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    """Payload del token JWT."""

    user_id: int
    role: str


class AuthRegisterRequest(BaseModel):
    """Solicitud de registro."""

    email: EmailStr
    password: str  # Mínimo 8 caracteres, debe contener mayúscula, minúscula, número
    name: str


class AuthLoginRequest(BaseModel):
    """Solicitud de login."""

    email: EmailStr
    password: str
