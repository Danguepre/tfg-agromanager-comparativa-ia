"""
Rutas de autenticación: registro, login, Google OAuth preparado.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import UserRole
from app.schemas.auth import AuthRegisterRequest, AuthLoginRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.auth_service import create_access_token
from app.services.user_service import create_user, authenticate_user, get_user_by_email

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(request: AuthRegisterRequest, db: Annotated[Session, Depends(get_db)]):
    """
    Registra un nuevo usuario.
    - Email debe ser único
    - Contraseña se hashea con bcrypt
    - Usuario nuevo tiene role=USER por defecto
    """
    # Validar que email no exista
    existing_user = get_user_by_email(db, request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Validar contraseña (mínimo 8 caracteres)
    if len(request.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters",
        )

    # Crear usuario
    user = create_user(db, email=request.email, password=request.password, name=request.name, role=UserRole.USER)

    return user


@router.post("/login", response_model=TokenResponse)
def login(request: AuthLoginRequest, db: Annotated[Session, Depends(get_db)]):
    """
    Login de usuario.
    - Valida credenciales
    - Retorna JWT access_token
    """
    # Autenticar
    user = authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
        )

    # Crear token
    token, expire = create_access_token(data={"user_id": user.id, "role": user.role.value})

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=int((expire - __import__("datetime").datetime.now(__import__("datetime").timezone.utc)).total_seconds()),
    )


# Google OAuth (preparado, sin implementación)
@router.get("/google/login")
def google_login_redirect():
    """
    Endpoint preparado para Google OAuth.
    Redirige a Google para login.
    [IMPLEMENTACIÓN EN FASE 5]
    """
    return {"message": "Google OAuth login endpoint (not implemented yet)"}


@router.get("/google/callback")
def google_oauth_callback(code: str = None):
    """
    Callback de Google OAuth.
    Intercambia código por token.
    [IMPLEMENTACIÓN EN FASE 5]
    """
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing authorization code",
        )
    return {"message": "Google OAuth callback (not implemented yet)"}
