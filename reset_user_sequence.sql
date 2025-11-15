-- Script para resetear IDs de usuarios
-- Situación actual: usuarios con ID 17 y 18
-- Objetivo: renumerar a ID 1 y 2

BEGIN;

-- 1. Crear tabla temporal con los usuarios actuales
CREATE TEMP TABLE users_backup AS 
SELECT * FROM users WHERE id IN (17, 18) ORDER BY id;

-- 2. Eliminar los usuarios actuales
DELETE FROM users WHERE id IN (17, 18);

-- 3. Resetear la secuencia a 1
ALTER SEQUENCE users_id_seq RESTART WITH 1;

-- 4. Reinsertar usuarios con nuevos IDs (1 y 2)
INSERT INTO users (
    email, password_hash, full_name, rol, is_active, 
    last_login_at, created_at, updated_at
)
SELECT 
    email, password_hash, full_name, rol, is_active,
    last_login_at, created_at, updated_at
FROM users_backup
ORDER BY id;

-- 5. Verificar resultado
SELECT id, email, full_name, rol FROM users ORDER BY id;

-- 6. Si todo está bien, hacer COMMIT
-- Si algo salió mal, hacer ROLLBACK
COMMIT;

-- ROLLBACK; -- Descomenta esta línea si algo salió mal
