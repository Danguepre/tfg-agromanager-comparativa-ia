"""Schemas Pydantic para autenticación."""

from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Schema para solicitud de login."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Schema para respuesta de token JWT."""
    access_token: str
    token_type: str = "bearer"