-- Script SQL para poblar la base de datos con datos de prueba
-- Ejecutar con: psql -U postgres -d avicola -f seed_data.sql

-- Limpiar datos existentes (opcional, comentar si no quieres borrar)
-- TRUNCATE TABLE users, farm_status, egg_production, mortality_event, 
--   feed_item, feed_mix, feed_mix_item, feed_consumption,
--   finance_category, finance_transaction, finance_summary, report_export 
--   RESTART IDENTITY CASCADE;

-- ============================================================================
-- USUARIOS
-- ============================================================================
-- Nota: Los password_hash aquí son ejemplos. Usa create_test_users.py para generar hashes reales.

INSERT INTO users (email, password_hash, full_name, rol, is_active, created_at, updated_at) VALUES
('admin@avicola.com', '$argon2id$v=19$m=65536,t=3,p=4$...', 'Administrador Principal', 'admin', true, NOW(), NOW()),
('worker@avicola.com', '$argon2id$v=19$m=65536,t=3,p=4$...', 'Trabajador de Campo', 'worker', true, NOW(), NOW()),
('accountant@avicola.com', '$argon2id$v=19$m=65536,t=3,p=4$...', 'Contador', 'accountant', true, NOW(), NOW())
ON CONFLICT (email) DO NOTHING;

-- ============================================================================
-- ESTADO DE LA GRANJA
-- ============================================================================

INSERT INTO farm_status (status_date, juveniles_count, males_count, hens_count, notes, created_at, updated_at, created_by, is_active) VALUES
('2024-11-01', 120, 55, 520, 'Estado inicial del mes', NOW(), NOW(), 1, true),
('2024-11-02', 118, 55, 518, 'Dos bajas de juveniles', NOW(), NOW(), 1, true),
('2024-11-03', 118, 54, 517, 'Una baja de macho y una gallina', NOW(), NOW(), 1, true),
('2024-11-04', 118, 54, 516, 'Una baja de gallina', NOW(), NOW(), 1, true),
('2024-11-05', 118, 54, 515, 'Una baja de gallina', NOW(), NOW(), 1, true),
('2024-11-06', 117, 54, 514, 'Una baja de juvenil y una gallina', NOW(), NOW(), 1, true),
('2024-11-07', 117, 54, 513, 'Una baja de gallina', NOW(), NOW(), 1, true),
('2024-11-08', 117, 54, 512, 'Una baja de gallina', NOW(), NOW(), 1, true)
ON CONFLICT (status_date) DO NOTHING;

-- ============================================================================
-- PRODUCCIÓN DE HUEVOS
-- ============================================================================

INSERT INTO egg_production (production_date, size_code, quantity, source_method, is_validated, notes, created_at, updated_at, created_by, is_active) VALUES
-- 2024-11-01
('2024-11-01', 'small', 45, 'manual', true, 'Producción matutina', NOW(), NOW(), 1, true),
('2024-11-01', 'medium', 180, 'manual', true, 'Producción matutina', NOW(), NOW(), 1, true),
('2024-11-01', 'large', 295, 'manual', true, 'Producción matutina', NOW(), NOW(), 1, true),
-- 2024-11-02
('2024-11-02', 'small', 42, 'manual', true, 'Producción matutina', NOW(), NOW(), 1, true),
('2024-11-02', 'medium', 185, 'manual', true, 'Producción matutina', NOW(), NOW(), 1, true),
('2024-11-02', 'large', 288, 'manual', true, 'Producción matutina', NOW(), NOW(), 1, true),
-- 2024-11-03
('2024-11-03', 'small', 48, 'manual', true, 'Producción matutina', NOW(), NOW(), 1, true),
('2024-11-03', 'medium', 175, 'manual', true, 'Producción matutina', NOW(), NOW(), 1, true),
('2024-11-03', 'large', 292, 'manual', true, 'Producción matutina', NOW(), NOW(), 1, true),
-- 2024-11-04
('2024-11-04', 'small', 50, 'manual', true, 'Producción matutina', NOW(), NOW(), 1, true),
('2024-11-04', 'medium', 178, 'manual', true, 'Producción matutina', NOW(), NOW(), 1, true),
('2024-11-04', 'large', 287, 'manual', true, 'Producción matutina', NOW(), NOW(), 1, true),
-- 2024-11-05
('2024-11-05', 'small', 46, 'manual', true, 'Producción matutina', NOW(), NOW(), 1, true),
('2024-11-05', 'medium', 182, 'manual', true, 'Producción matutina', NOW(), NOW(), 1, true),
('2024-11-05', 'large', 290, 'manual', true, 'Producción matutina', NOW(), NOW(), 1, true),
-- 2024-11-06
('2024-11-06', 'small', 44, 'manual', true, 'Producción matutina', NOW(), NOW(), 1, true),
('2024-11-06', 'medium', 180, 'manual', true, 'Producción matutina', NOW(), NOW(), 1, true),
('2024-11-06', 'large', 285, 'manual', true, 'Producción matutina', NOW(), NOW(), 1, true),
-- 2024-11-07
('2024-11-07', 'small', 47, 'manual', true, 'Producción matutina', NOW(), NOW(), 1, true),
('2024-11-07', 'medium', 183, 'manual', true, 'Producción matutina', NOW(), NOW(), 1, true),
('2024-11-07', 'large', 283, 'manual', true, 'Producción matutina', NOW(), NOW(), 1, true),
-- 2024-11-08
('2024-11-08', 'small', 49, 'manual', false, 'Producción matutina - pendiente validación', NOW(), NOW(), 1, true),
('2024-11-08', 'medium', 181, 'manual', false, 'Producción matutina - pendiente validación', NOW(), NOW(), 1, true),
('2024-11-08', 'large', 286, 'manual', false, 'Producción matutina - pendiente validación', NOW(), NOW(), 1, true)
ON CONFLICT (production_date, size_code) DO NOTHING;

-- ============================================================================
-- EVENTOS DE MORTALIDAD
-- ============================================================================

INSERT INTO mortality_event (event_date, bird_type, quantity, cause, notes, created_at, updated_at, created_by, is_active) VALUES
('2024-11-02', 'juvenile', 2, 'Enfermedad respiratoria', 'Aislados del resto', NOW(), NOW(), 1, true),
('2024-11-03', 'male', 1, 'Pelea entre machos', 'Heridas graves', NOW(), NOW(), 1, true),
('2024-11-03', 'hen', 1, 'Edad avanzada', 'Muerte natural', NOW(), NOW(), 1, true),
('2024-11-04', 'hen', 1, 'Desconocida', 'Encontrada muerta en la mañana', NOW(), NOW(), 1, true),
('2024-11-05', 'hen', 1, 'Enfermedad digestiva', 'Síntomas de diarrea', NOW(), NOW(), 1, true),
('2024-11-06', 'juvenile', 1, 'Debilidad', 'No se alimentaba bien', NOW(), NOW(), 1, true),
('2024-11-06', 'hen', 1, 'Edad avanzada', 'Muerte natural', NOW(), NOW(), 1, true),
('2024-11-07', 'hen', 1, 'Desconocida', 'Encontrada muerta', NOW(), NOW(), 1, true),
('2024-11-08', 'hen', 1, 'Enfermedad respiratoria', 'Aislada', NOW(), NOW(), 1, true);

-- ============================================================================
-- ITEMS DE ALIMENTO
-- ============================================================================

INSERT INTO feed_item (item_name, supplier_name, unit_cost_clp, unit_type, notes, created_at, updated_at, created_by, is_active) VALUES
('Maíz molido', 'Agrícola del Sur', 450.00, 'kg', 'Grano fino de calidad', NOW(), NOW(), 1, true),
('Soya procesada', 'Proteínas Chile', 680.00, 'kg', 'Alta proteína', NOW(), NOW(), 1, true),
('Trigo integral', 'Molinos Central', 420.00, 'kg', 'Grano entero', NOW(), NOW(), 1, true),
('Carbonato de calcio', 'Minerales SA', 250.00, 'kg', 'Para cáscara de huevo', NOW(), NOW(), 1, true),
('Premezcla vitamínica', 'NutriAves', 1200.00, 'kg', 'Vitaminas y minerales', NOW(), NOW(), 1, true),
('Sal mineral', 'Minerales SA', 180.00, 'kg', 'Sales esenciales', NOW(), NOW(), 1, true)
ON CONFLICT (item_name) DO NOTHING;

-- ============================================================================
-- MEZCLAS DE ALIMENTO
-- ============================================================================

INSERT INTO feed_mix (mix_date, description, total_weight_kg, notes, created_at, updated_at, created_by, is_active) VALUES
('2024-11-01', 'Mezcla estándar para ponedoras', 1000.00, 'Preparada en la mañana', NOW(), NOW(), 1, true),
('2024-11-04', 'Mezcla estándar para ponedoras', 1000.00, 'Preparada en la mañana', NOW(), NOW(), 1, true),
('2024-11-07', 'Mezcla estándar para ponedoras', 1000.00, 'Preparada en la mañana', NOW(), NOW(), 1, true)
ON CONFLICT (mix_date) DO NOTHING;

-- ============================================================================
-- ITEMS DE MEZCLA DE ALIMENTO
-- ============================================================================

-- Mezcla del 2024-11-01
INSERT INTO feed_mix_item (feed_mix_id, feed_item_id, proportion_pct, weight_kg, notes, created_at, updated_at, created_by, is_active)
SELECT 
    (SELECT id FROM feed_mix WHERE mix_date = '2024-11-01'),
    (SELECT id FROM feed_item WHERE item_name = 'Maíz molido'),
    50.00, 500.00, 'Base energética', NOW(), NOW(), 1, true
WHERE NOT EXISTS (
    SELECT 1 FROM feed_mix_item 
    WHERE feed_mix_id = (SELECT id FROM feed_mix WHERE mix_date = '2024-11-01')
    AND feed_item_id = (SELECT id FROM feed_item WHERE item_name = 'Maíz molido')
);

INSERT INTO feed_mix_item (feed_mix_id, feed_item_id, proportion_pct, weight_kg, notes, created_at, updated_at, created_by, is_active)
SELECT 
    (SELECT id FROM feed_mix WHERE mix_date = '2024-11-01'),
    (SELECT id FROM feed_item WHERE item_name = 'Soya procesada'),
    25.00, 250.00, 'Proteína principal', NOW(), NOW(), 1, true
WHERE NOT EXISTS (
    SELECT 1 FROM feed_mix_item 
    WHERE feed_mix_id = (SELECT id FROM feed_mix WHERE mix_date = '2024-11-01')
    AND feed_item_id = (SELECT id FROM feed_item WHERE item_name = 'Soya procesada')
);

INSERT INTO feed_mix_item (feed_mix_id, feed_item_id, proportion_pct, weight_kg, notes, created_at, updated_at, created_by, is_active)
SELECT 
    (SELECT id FROM feed_mix WHERE mix_date = '2024-11-01'),
    (SELECT id FROM feed_item WHERE item_name = 'Trigo integral'),
    15.00, 150.00, 'Fibra', NOW(), NOW(), 1, true
WHERE NOT EXISTS (
    SELECT 1 FROM feed_mix_item 
    WHERE feed_mix_id = (SELECT id FROM feed_mix WHERE mix_date = '2024-11-01')
    AND feed_item_id = (SELECT id FROM feed_item WHERE item_name = 'Trigo integral')
);

INSERT INTO feed_mix_item (feed_mix_id, feed_item_id, proportion_pct, weight_kg, notes, created_at, updated_at, created_by, is_active)
SELECT 
    (SELECT id FROM feed_mix WHERE mix_date = '2024-11-01'),
    (SELECT id FROM feed_item WHERE item_name = 'Carbonato de calcio'),
    8.00, 80.00, 'Calcio para cáscara', NOW(), NOW(), 1, true
WHERE NOT EXISTS (
    SELECT 1 FROM feed_mix_item 
    WHERE feed_mix_id = (SELECT id FROM feed_mix WHERE mix_date = '2024-11-01')
    AND feed_item_id = (SELECT id FROM feed_item WHERE item_name = 'Carbonato de calcio')
);

INSERT INTO feed_mix_item (feed_mix_id, feed_item_id, proportion_pct, weight_kg, notes, created_at, updated_at, created_by, is_active)
SELECT 
    (SELECT id FROM feed_mix WHERE mix_date = '2024-11-01'),
    (SELECT id FROM feed_item WHERE item_name = 'Premezcla vitamínica'),
    1.50, 15.00, 'Vitaminas', NOW(), NOW(), 1, true
WHERE NOT EXISTS (
    SELECT 1 FROM feed_mix_item 
    WHERE feed_mix_id = (SELECT id FROM feed_mix WHERE mix_date = '2024-11-01')
    AND feed_item_id = (SELECT id FROM feed_item WHERE item_name = 'Premezcla vitamínica')
);

INSERT INTO feed_mix_item (feed_mix_id, feed_item_id, proportion_pct, weight_kg, notes, created_at, updated_at, created_by, is_active)
SELECT 
    (SELECT id FROM feed_mix WHERE mix_date = '2024-11-01'),
    (SELECT id FROM feed_item WHERE item_name = 'Sal mineral'),
    0.50, 5.00, 'Minerales', NOW(), NOW(), 1, true
WHERE NOT EXISTS (
    SELECT 1 FROM feed_mix_item 
    WHERE feed_mix_id = (SELECT id FROM feed_mix WHERE mix_date = '2024-11-01')
    AND feed_item_id = (SELECT id FROM feed_item WHERE item_name = 'Sal mineral')
);

-- Repetir para otras mezclas (2024-11-04 y 2024-11-07) con la misma composición

-- ============================================================================
-- CONSUMO DE ALIMENTO
-- ============================================================================

INSERT INTO feed_consumption (consumption_date, feed_mix_id, total_consumed_kg, notes, created_at, updated_at, created_by, is_active)
SELECT '2024-11-01', id, 85.50, 'Consumo normal', NOW(), NOW(), 1, true
FROM feed_mix WHERE mix_date = '2024-11-01'
ON CONFLICT (consumption_date) DO NOTHING;

INSERT INTO feed_consumption (consumption_date, feed_mix_id, total_consumed_kg, notes, created_at, updated_at, created_by, is_active)
SELECT '2024-11-02', id, 84.20, 'Consumo normal', NOW(), NOW(), 1, true
FROM feed_mix WHERE mix_date = '2024-11-01'
ON CONFLICT (consumption_date) DO NOTHING;

INSERT INTO feed_consumption (consumption_date, feed_mix_id, total_consumed_kg, notes, created_at, updated_at, created_by, is_active)
SELECT '2024-11-03', id, 83.80, 'Consumo ligeramente bajo', NOW(), NOW(), 1, true
FROM feed_mix WHERE mix_date = '2024-11-01'
ON CONFLICT (consumption_date) DO NOTHING;

INSERT INTO feed_consumption (consumption_date, feed_mix_id, total_consumed_kg, notes, created_at, updated_at, created_by, is_active)
SELECT '2024-11-04', id, 84.50, 'Consumo normal', NOW(), NOW(), 1, true
FROM feed_mix WHERE mix_date = '2024-11-04'
ON CONFLICT (consumption_date) DO NOTHING;

INSERT INTO feed_consumption (consumption_date, feed_mix_id, total_consumed_kg, notes, created_at, updated_at, created_by, is_active)
SELECT '2024-11-05', id, 85.00, 'Consumo normal', NOW(), NOW(), 1, true
FROM feed_mix WHERE mix_date = '2024-11-04'
ON CONFLICT (consumption_date) DO NOTHING;

INSERT INTO feed_consumption (consumption_date, feed_mix_id, total_consumed_kg, notes, created_at, updated_at, created_by, is_active)
SELECT '2024-11-06', id, 84.80, 'Consumo normal', NOW(), NOW(), 1, true
FROM feed_mix WHERE mix_date = '2024-11-04'
ON CONFLICT (consumption_date) DO NOTHING;

INSERT INTO feed_consumption (consumption_date, feed_mix_id, total_consumed_kg, notes, created_at, updated_at, created_by, is_active)
SELECT '2024-11-07', id, 85.20, 'Consumo normal', NOW(), NOW(), 1, true
FROM feed_mix WHERE mix_date = '2024-11-07'
ON CONFLICT (consumption_date) DO NOTHING;

INSERT INTO feed_consumption (consumption_date, feed_mix_id, total_consumed_kg, notes, created_at, updated_at, created_by, is_active)
SELECT '2024-11-08', id, 84.90, 'Consumo normal', NOW(), NOW(), 1, true
FROM feed_mix WHERE mix_date = '2024-11-07'
ON CONFLICT (consumption_date) DO NOTHING;

-- ============================================================================
-- CATEGORÍAS FINANCIERAS
-- ============================================================================

INSERT INTO finance_category (category_name, type, description, created_at, updated_at, created_by, is_active) VALUES
-- Ingresos
('Venta de Huevos', 'income', 'Ingresos por venta de huevos', NOW(), NOW(), 1, true),
('Venta de Aves', 'income', 'Ingresos por venta de aves', NOW(), NOW(), 1, true),
('Otros Ingresos', 'income', 'Otros ingresos diversos', NOW(), NOW(), 1, true),
-- Gastos
('Compra de Alimento', 'expense', 'Gastos en alimento para aves', NOW(), NOW(), 1, true),
('Medicamentos', 'expense', 'Gastos en medicamentos y vacunas', NOW(), NOW(), 1, true),
('Mantenimiento', 'expense', 'Gastos en mantenimiento de instalaciones', NOW(), NOW(), 1, true),
('Servicios Básicos', 'expense', 'Agua, luz, gas', NOW(), NOW(), 1, true),
('Salarios', 'expense', 'Pago de salarios', NOW(), NOW(), 1, true),
('Otros Gastos', 'expense', 'Otros gastos diversos', NOW(), NOW(), 1, true);

-- ============================================================================
-- TRANSACCIONES FINANCIERAS
-- ============================================================================

INSERT INTO finance_transaction (transaction_date, category_id, amount_clp, payment_method, reference_doc, description, created_at, updated_at, created_by, is_active)
SELECT '2024-11-01', id, 125000.00, 'Transferencia', 'FACT-001', 'Venta semanal de huevos', NOW(), NOW(), 1, true
FROM finance_category WHERE category_name = 'Venta de Huevos' AND type = 'income';

INSERT INTO finance_transaction (transaction_date, category_id, amount_clp, payment_method, reference_doc, description, created_at, updated_at, created_by, is_active)
SELECT '2024-11-02', id, 85000.00, 'Efectivo', 'FACT-002', 'Venta local de huevos', NOW(), NOW(), 1, true
FROM finance_category WHERE category_name = 'Venta de Huevos' AND type = 'income';

INSERT INTO finance_transaction (transaction_date, category_id, amount_clp, payment_method, reference_doc, description, created_at, updated_at, created_by, is_active)
SELECT '2024-11-03', id, 450000.00, 'Transferencia', 'FC-101', 'Compra de alimento - 1 tonelada', NOW(), NOW(), 1, true
FROM finance_category WHERE category_name = 'Compra de Alimento' AND type = 'expense';

INSERT INTO finance_transaction (transaction_date, category_id, amount_clp, payment_method, reference_doc, description, created_at, updated_at, created_by, is_active)
SELECT '2024-11-04', id, 95000.00, 'Transferencia', 'FACT-003', 'Venta de huevos', NOW(), NOW(), 1, true
FROM finance_category WHERE category_name = 'Venta de Huevos' AND type = 'income';

INSERT INTO finance_transaction (transaction_date, category_id, amount_clp, payment_method, reference_doc, description, created_at, updated_at, created_by, is_active)
SELECT '2024-11-05', id, 35000.00, 'Efectivo', 'REC-001', 'Medicamentos preventivos', NOW(), NOW(), 1, true
FROM finance_category WHERE category_name = 'Medicamentos' AND type = 'expense';

INSERT INTO finance_transaction (transaction_date, category_id, amount_clp, payment_method, reference_doc, description, created_at, updated_at, created_by, is_active)
SELECT '2024-11-06', id, 110000.00, 'Transferencia', 'FACT-004', 'Venta de huevos', NOW(), NOW(), 1, true
FROM finance_category WHERE category_name = 'Venta de Huevos' AND type = 'income';

INSERT INTO finance_transaction (transaction_date, category_id, amount_clp, payment_method, reference_doc, description, created_at, updated_at, created_by, is_active)
SELECT '2024-11-07', id, 45000.00, 'Efectivo', 'REC-002', 'Reparación de bebederos', NOW(), NOW(), 1, true
FROM finance_category WHERE category_name = 'Mantenimiento' AND type = 'expense';

INSERT INTO finance_transaction (transaction_date, category_id, amount_clp, payment_method, reference_doc, description, created_at, updated_at, created_by, is_active)
SELECT '2024-11-08', id, 98000.00, 'Transferencia', 'FACT-005', 'Venta de huevos', NOW(), NOW(), 1, true
FROM finance_category WHERE category_name = 'Venta de Huevos' AND type = 'income';

-- ============================================================================
-- REPORTES (ejemplos)
-- ============================================================================

INSERT INTO report_export (report_type, period_start, period_end, file_format, file_path, file_size_bytes, created_at, updated_at, created_by, is_active) VALUES
('production_monthly', '2024-10-01', '2024-10-31', 'pdf', '/reports/production_2024_10.pdf', 524288, NOW(), NOW(), 1, true),
('finance_monthly', '2024-10-01', '2024-10-31', 'xlsx', '/reports/finance_2024_10.xlsx', 102400, NOW(), NOW(), 1, true),
('eggs_daily', '2024-11-01', '2024-11-07', 'csv', '/reports/eggs_2024_11_week1.csv', 8192, NOW(), NOW(), 1, true);

-- ============================================================================
-- Fin del script
-- ============================================================================

SELECT 'Datos de prueba insertados exitosamente!' AS mensaje;
