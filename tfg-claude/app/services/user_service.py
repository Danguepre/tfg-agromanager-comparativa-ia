"""
Servicios de usuario.
"""
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.services.auth_service import hash_password, verify_password


def create_user(db: Session, email: str, password: str, name: str, role: UserRole = UserRole.USER) -> User:
    """Crea un nuevo usuario con contraseña hasheada."""
    password_hash = hash_password(password)
    user = User(email=email, name=name, password_hash=password_hash, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    """Obtiene usuario por email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Obtiene usuario por ID."""
    return db.query(User).filter(User.id == user_id).first()


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """
    Autentica usuario.
    Retorna User si credenciales son válidas, None si no.
    """
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def get_all_users(db: Session) -> list[User]:
    """Obtiene todos los usuarios (solo para admin)."""
    return db.query(User).all()


def delete_user(db: Session, user_id: int) -> bool:
    """Elimina usuario por ID."""
    user = get_user_by_id(db, user_id)
    if user:
        db.delete(user)
        db.commit()
        return True
    return False
