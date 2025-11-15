"""
Utilidades de autenticación - Manejo seguro de contraseñas.
Soporta Argon2 (recomendado) y bcrypt (compatibilidad).
"""

import argon2
import bcrypt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash


# Inicializar hasher de Argon2
ph = PasswordHasher()


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash.
    Soporta Argon2 y bcrypt.
    
    Retorna True si la contraseña es correcta, False si no.
    """
    if not password or not password_hash:
        return False
    
    # Intentar con Argon2 primero (más seguro)
    if password_hash.startswith('$argon2'):
        try:
            ph.verify(password_hash, password)
            return True
        except (VerifyMismatchError, InvalidHash):
            return False
    
    # Intentar con bcrypt (compatibilidad)
    elif password_hash.startswith('$2a$') or password_hash.startswith('$2b$') or password_hash.startswith('$2y$'):
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
        except Exception:
            return False
    
    return False


def hash_password(password: str, use_argon2: bool = True) -> str:
    """
    Encripta una contraseña usando Argon2 o bcrypt.
    
    Por defecto usa Argon2 (más seguro).
    Retorna la contraseña encriptada.
    """
    if use_argon2:
        return ph.hash(password)
    else:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def needs_rehash(password_hash: str) -> bool:
    """
    Verifica si una contraseña necesita ser re-encriptada.
    
    Retorna True si necesita actualización, False si no.
    """
    if password_hash.startswith('$argon2'):
        try:
            return ph.check_needs_rehash(password_hash)
        except Exception:
            return True
    
    # Las contraseñas bcrypt deberían migrarse a Argon2
    return True
