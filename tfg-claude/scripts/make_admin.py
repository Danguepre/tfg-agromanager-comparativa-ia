#!/usr/bin/env python3
"""
Script para convertir un usuario normal en admin en la base de datos SQLite.
Útil para pruebas del panel admin sin modificar el código.

Uso:
    python scripts/make_admin.py <user_id>
    
Ejemplo:
    python scripts/make_admin.py 1
    
Esto convertirá el usuario con ID 1 en admin.
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole

def make_admin(user_id: int):
    """Convierte un usuario en admin."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"❌ Usuario con ID {user_id} no encontrado.")
            return False
        
        if user.role == UserRole.ADMIN:
            print(f"⚠️  El usuario {user.email} ya es admin.")
            return True
        
        user.role = UserRole.ADMIN
        db.commit()
        print(f"✅ Usuario {user.email} (ID: {user.id}) convertido a admin.")
        print(f"   Role: {user.role}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scripts/make_admin.py <user_id>")
        print("")
        print("Ejemplos:")
        print("  python scripts/make_admin.py 1")
        print("  python scripts/make_admin.py 2")
        sys.exit(1)
    
    try:
        user_id = int(sys.argv[1])
        success = make_admin(user_id)
        sys.exit(0 if success else 1)
    except ValueError:
        print(f"❌ Error: {sys.argv[1]} no es un número válido.")
        sys.exit(1)
