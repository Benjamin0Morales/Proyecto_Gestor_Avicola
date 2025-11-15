-- ============================================================================
-- Script para crear usuario ADMIN inicial en PostgreSQL
-- Base de datos: Avicola_Eugenio_BBDD
-- ============================================================================
-- 
-- IMPORTANTE: Este script usa un password hash de Argon2 generado.
-- Password: admin123
-- Hash: $argon2id$v=19$m=65536,t=3,p=4$k1fg4liegVTSH+xYnzUgYg$vy/+nCiGslKObV8c9Ksb0JGSiFoflaRGGOgaTv0o3Kw
--
-- Si quieres cambiar el password, debes generar un nuevo hash usando:
-- Python: from argon2 import PasswordHasher; print(PasswordHasher().hash('tu_password'))
-- ============================================================================

-- Deshabilitar temporalmente las restricciones de FK para permitir el bootstrap
BEGIN;

-- Insertar el usuario admin inicial
-- Nota: created_by y updated_by se dejan NULL inicialmente porque no existe ningún usuario aún
INSERT INTO users (
    email,
    password_hash,
    full_name,
    rol,
    is_active,
    created_at,
    updated_at,
    created_by,
    updated_by
) VALUES (
    'admin@avicola.com',
    '$argon2id$v=19$m=65536,t=3,p=4$k1fg4liegVTSH+xYnzUgYg$vy/+nCiGslKObV8c9Ksb0JGSiFoflaRGGOgaTv0o3Kw',
    'Administrador Principal',
    'admin',
    TRUE,
    NOW(),
    NOW(),
    NULL,  -- Se puede actualizar después con el propio ID
    NULL
);

-- Opcional: Actualizar created_by y updated_by para que apunten al mismo usuario
-- (Esto es cosmético, no es estrictamente necesario)
UPDATE users 
SET created_by = id, updated_by = id 
WHERE email = 'admin@avicola.com';

COMMIT;

-- ============================================================================
-- Verificar que el usuario fue creado correctamente
-- ============================================================================
SELECT 
    id,
    email,
    full_name,
    rol,
    is_active,
    created_at
FROM users 
WHERE email = 'admin@avicola.com';

-- ============================================================================
-- USUARIOS ADICIONALES (OPCIONAL)
-- ============================================================================
-- Puedes descomentar estas líneas para crear usuarios adicionales:

/*
-- Usuario Worker (Trabajador)
-- Password: worker123
INSERT INTO users (email, password_hash, full_name, rol, is_active, created_at, updated_at, created_by, updated_by)
VALUES (
    'worker@avicola.com',
    '$argon2id$v=19$m=65536,t=3,p=4$VlQMifIaUU0UWVHhRlhrFQ$lfgbBbCaA0tB6Z0n9L5+N1vSiN5d6lqXNYqPvKLOFCw',
    'Trabajador de Campo',
    'worker',
    TRUE,
    NOW(),
    NOW(),
    (SELECT id FROM users WHERE email = 'admin@avicola.com'),
    (SELECT id FROM users WHERE email = 'admin@avicola.com')
);

-- Usuario Accountant (Contador)
-- Password: accountant123
INSERT INTO users (email, password_hash, full_name, rol, is_active, created_at, updated_at, created_by, updated_by)
VALUES (
    'accountant@avicola.com',
    '$argon2id$v=19$m=65536,t=3,p=4$vi2kjWgw+15E3Ilhx+Thgg$AzxZoajmHrhIqJV8mJr1TvAD9UKOX5hIo6T3mjLzHIg',
    'Contador Principal',
    'accountant',
    TRUE,
    NOW(),
    NOW(),
    (SELECT id FROM users WHERE email = 'admin@avicola.com'),
    (SELECT id FROM users WHERE email = 'admin@avicola.com')
);
*/

-- ============================================================================
-- NOTAS IMPORTANTES:
-- ============================================================================
-- 1. Los password hashes mostrados aquí son EJEMPLOS y NO son seguros para producción
-- 2. Para generar hashes reales, usa el script create_test_users.py del proyecto
-- 3. Los passwords de ejemplo son:
--    - admin@avicola.com: admin123
--    - worker@avicola.com: worker123
--    - accountant@avicola.com: accountant123
-- 4. En producción, SIEMPRE usa passwords fuertes y únicos
-- ============================================================================
