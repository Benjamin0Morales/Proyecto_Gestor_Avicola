-- =========================
--  SCHEMA: users
-- =========================
CREATE TABLE IF NOT EXISTS users (
  id               BIGSERIAL PRIMARY KEY,
  email            VARCHAR(255)  NOT NULL,
  password_hash    TEXT          NOT NULL,  
  full_name        VARCHAR(150)  NOT NULL,
  rol             VARCHAR(20)   NOT NULL,
  
  CONSTRAINT users_role_ck
    CHECK (rol IN ('admin','worker','accountant')),
  
  -- Estado y actividad
  is_active        BOOLEAN       NOT NULL DEFAULT TRUE,
  last_login_at    TIMESTAMPTZ,

  -- Auditoría
  created_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  updated_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  created_by       BIGINT,
  updated_by       BIGINT,

  -- Reglas de formato mínimas
  CONSTRAINT users_email_format_ck
  CHECK (email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- Unicidad de email ignorando mayúsculas/minúsculas
CREATE UNIQUE INDEX IF NOT EXISTS users_email_lower_uidx
  ON users (LOWER(email));

-- FKs de auditoría (auto-referenciadas, diferibles para permitir bootstrap del primer admin)
ALTER TABLE users
  ADD CONSTRAINT users_created_by_fk
  FOREIGN KEY (created_by) REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE users
  ADD CONSTRAINT users_updated_by_fk
  FOREIGN KEY (updated_by) REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED;

-- Trigger para mantener updated_at
CREATE OR REPLACE FUNCTION trg_touch_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at := NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS users_touch_updated_at ON users;
CREATE TRIGGER users_touch_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION trg_touch_updated_at();

 -- =========================
--  SCHEMA: farm_status
-- =========================

CREATE TABLE IF NOT EXISTS farm_status (
  id                 BIGSERIAL PRIMARY KEY,
  status_date        DATE NOT NULL,          
  juveniles_count    INTEGER NOT NULL DEFAULT 0,
  males_count        INTEGER NOT NULL DEFAULT 0,
  hens_count         INTEGER NOT NULL DEFAULT 0,

  -- total generado = juveniles + machos + gallinas
  total_birds        INTEGER GENERATED ALWAYS AS
                      (GREATEST(0, juveniles_count) + GREATEST(0, males_count) + GREATEST(0, hens_count)) STORED,

  -- Auditoría
  is_active          BOOLEAN     NOT NULL DEFAULT TRUE,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_by         BIGINT REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED,
  updated_by         BIGINT REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED,

  -- Reglas/Checks
  CONSTRAINT farm_status_date_uk UNIQUE (status_date),
  CONSTRAINT farm_status_nonneg_ck
    CHECK (juveniles_count >= 0 AND males_count >= 0 AND hens_count >= 0)
);

-- Índice para consultas por fecha (descendente, útil para dashboards)
CREATE INDEX IF NOT EXISTS farm_status_date_desc_idx
  ON farm_status (status_date DESC);

-- Trigger para updated_at
DROP TRIGGER IF EXISTS farm_status_touch_updated_at ON farm_status;
CREATE TRIGGER farm_status_touch_updated_at
BEFORE UPDATE ON farm_status
FOR EACH ROW
EXECUTE FUNCTION trg_touch_updated_at();

-- =========================
--  SCHEMA: egg_production
-- =========================

CREATE TABLE IF NOT EXISTS egg_production (
  id               BIGSERIAL PRIMARY KEY,

  production_date  DATE        NOT NULL,
  size_code        VARCHAR(10) NOT NULL,   -- 'small' | 'medium' | 'large'
  quantity         INTEGER     NOT NULL DEFAULT 0,

  -- Estado de validación (conteo final mostrado en dashboard)
  source_method    VARCHAR(12) NOT NULL DEFAULT 'manual', -- 'manual' | 'vision'
  is_validated     BOOLEAN     NOT NULL DEFAULT TRUE,
  validated_at     TIMESTAMPTZ,
  validated_by     BIGINT REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED,

  -- Auditoría
  is_active        BOOLEAN     NOT NULL DEFAULT TRUE,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_by       BIGINT REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED,
  updated_by       BIGINT REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED,

  -- Reglas
  CONSTRAINT egg_production_size_ck
    CHECK (size_code IN ('small','medium','large')),
  CONSTRAINT egg_production_qty_nonneg_ck
    CHECK (quantity >= 0),

  -- Un único registro por día y tamaño
  CONSTRAINT egg_production_uk UNIQUE (production_date, size_code),

  -- Origen válido
  CONSTRAINT egg_production_source_ck
    CHECK (source_method IN ('manual','vision'))
);

-- Índices útiles
CREATE INDEX IF NOT EXISTS egg_production_date_desc_idx
  ON egg_production (production_date DESC);

CREATE INDEX IF NOT EXISTS egg_production_valid_idx
  ON egg_production (production_date, is_validated);

-- Trigger para updated_at (usa la función trg_touch_updated_at ya creada)
DROP TRIGGER IF EXISTS egg_production_touch_updated_at ON egg_production;
CREATE TRIGGER egg_production_touch_updated_at
BEFORE UPDATE ON egg_production
FOR EACH ROW
EXECUTE FUNCTION trg_touch_updated_at();

-- Vista de resumen diario (desglose por tamaño y total)
CREATE OR REPLACE VIEW v_egg_production_daily AS
SELECT
  production_date,
  SUM(quantity) FILTER (WHERE size_code = 'small'  AND is_validated) AS small_qty,
  SUM(quantity) FILTER (WHERE size_code = 'medium' AND is_validated) AS medium_qty,
  SUM(quantity) FILTER (WHERE size_code = 'large'  AND is_validated) AS large_qty,
  SUM(quantity) FILTER (WHERE is_validated)                           AS total_qty
FROM egg_production
GROUP BY production_date;

-- =========================
--  SCHEMA: feed_item
-- =========================
CREATE TABLE IF NOT EXISTS feed_item (
  id               BIGSERIAL PRIMARY KEY,
  item_name        VARCHAR(100) NOT NULL,
  supplier_name    VARCHAR(100),
  unit_cost_clp    NUMERIC(12,2) NOT NULL CHECK (unit_cost_clp >= 0),
  unit_type        VARCHAR(20) DEFAULT 'kg',  -- normalmente kg, pero se deja abierto

  -- Auditoría
  is_active        BOOLEAN NOT NULL DEFAULT TRUE,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_by       BIGINT REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED,
  updated_by       BIGINT REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED
);

CREATE UNIQUE INDEX IF NOT EXISTS feed_item_name_uk
  ON feed_item (LOWER(item_name));

DROP TRIGGER IF EXISTS feed_item_touch_updated_at ON feed_item;
CREATE TRIGGER feed_item_touch_updated_at
BEFORE UPDATE ON feed_item
FOR EACH ROW
EXECUTE FUNCTION trg_touch_updated_at();

-- =========================
--  SCHEMA: feed_inventory
-- =========================
CREATE TABLE IF NOT EXISTS feed_inventory (
  id               BIGSERIAL PRIMARY KEY,
  feed_item_id     BIGINT NOT NULL REFERENCES feed_item(id),
  quantity         NUMERIC(10,2) NOT NULL DEFAULT 0 CHECK (quantity >= 0),
  unit_type        VARCHAR(20) NOT NULL, -- debe coincidir con feed_item.unit_type
  last_updated     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  notes            TEXT,

  -- Auditoría
  is_active        BOOLEAN NOT NULL DEFAULT TRUE,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_by       BIGINT REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED,
  updated_by       BIGINT REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED,

  CONSTRAINT feed_inventory_item_uk UNIQUE (feed_item_id)
);

CREATE INDEX IF NOT EXISTS feed_inventory_item_fk_idx ON feed_inventory (feed_item_id);

DROP TRIGGER IF EXISTS feed_inventory_touch_updated_at ON feed_inventory;
CREATE TRIGGER feed_inventory_touch_updated_at
BEFORE UPDATE ON feed_inventory
FOR EACH ROW
EXECUTE FUNCTION trg_touch_updated_at();

-- =========================
--  SCHEMA: feed_inventory_movement
-- =========================
CREATE TABLE IF NOT EXISTS feed_inventory_movement (
  id               BIGSERIAL PRIMARY KEY,
  feed_item_id     BIGINT NOT NULL REFERENCES feed_item(id),
  movement_type    VARCHAR(20) NOT NULL CHECK (movement_type IN ('purchase', 'usage', 'waste')),
  quantity         NUMERIC(10,2) NOT NULL CHECK (quantity != 0),
  unit_type        VARCHAR(20) NOT NULL,
  movement_date    DATE NOT NULL DEFAULT CURRENT_DATE,
  reference        VARCHAR(100), -- ej: "Compra factura #123", "Mezcla del 2024-11-11"
  notes            TEXT,
  unit_cost_clp    NUMERIC(12,2), -- costo unitario en el momento del movimiento

  -- Auditoría
  is_active        BOOLEAN NOT NULL DEFAULT TRUE,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_by       BIGINT REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED,
  updated_by       BIGINT REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS feed_inventory_movement_item_fk_idx ON feed_inventory_movement (feed_item_id);
CREATE INDEX IF NOT EXISTS feed_inventory_movement_date_idx ON feed_inventory_movement (movement_date);
CREATE INDEX IF NOT EXISTS feed_inventory_movement_type_idx ON feed_inventory_movement (movement_type);

DROP TRIGGER IF EXISTS feed_inventory_movement_touch_updated_at ON feed_inventory_movement;
CREATE TRIGGER feed_inventory_movement_touch_updated_at
BEFORE UPDATE ON feed_inventory_movement
FOR EACH ROW
EXECUTE FUNCTION trg_touch_updated_at();

-- =========================
--  SCHEMA: feed_mix
-- =========================
CREATE TABLE IF NOT EXISTS feed_mix (
  id               BIGSERIAL PRIMARY KEY,
  mix_date         DATE NOT NULL,
  description      VARCHAR(200), -- opcional, ej. "mezcla 70/30 maíz/soya"
  total_weight_kg  NUMERIC(10,2) CHECK (total_weight_kg >= 0),

  -- Auditoría
  is_active        BOOLEAN NOT NULL DEFAULT TRUE,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_by       BIGINT REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED,
  updated_by       BIGINT REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED
);

DROP TRIGGER IF EXISTS feed_mix_touch_updated_at ON feed_mix;
CREATE TRIGGER feed_mix_touch_updated_at
BEFORE UPDATE ON feed_mix
FOR EACH ROW
EXECUTE FUNCTION trg_touch_updated_at();

-- =========================
--  SCHEMA: feed_mix_item (detalle)
-- =========================
CREATE TABLE IF NOT EXISTS feed_mix_item (
  id               BIGSERIAL PRIMARY KEY,
  feed_mix_id      BIGINT NOT NULL REFERENCES feed_mix(id) ON DELETE CASCADE,
  feed_item_id     BIGINT NOT NULL REFERENCES feed_item(id),
  proportion_pct   NUMERIC(5,2) NOT NULL CHECK (proportion_pct >= 0 AND proportion_pct <= 100),
  weight_kg        NUMERIC(10,2) CHECK (weight_kg >= 0),

  -- Auditoría
  is_active        BOOLEAN NOT NULL DEFAULT TRUE,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_by       BIGINT REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED,
  updated_by       BIGINT REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED
);

-- Índices
CREATE INDEX IF NOT EXISTS feed_mix_item_mix_fk_idx ON feed_mix_item (feed_mix_id);
CREATE INDEX IF NOT EXISTS feed_mix_item_feed_fk_idx ON feed_mix_item (feed_item_id);

DROP TRIGGER IF EXISTS feed_mix_item_touch_updated_at ON feed_mix_item;
CREATE TRIGGER feed_mix_item_touch_updated_at
BEFORE UPDATE ON feed_mix_item
FOR EACH ROW
EXECUTE FUNCTION trg_touch_updated_at();


-- =========================
--  SCHEMA: feed_consumption
-- =========================
CREATE TABLE IF NOT EXISTS feed_consumption (
  id               BIGSERIAL PRIMARY KEY,
  consumption_date DATE NOT NULL,
  feed_mix_id      BIGINT REFERENCES feed_mix(id) ON DELETE SET NULL,
  total_consumed_kg NUMERIC(10,2) NOT NULL CHECK (total_consumed_kg >= 0),

  -- Auditoría
  is_active        BOOLEAN NOT NULL DEFAULT TRUE,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_by       BIGINT REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED,
  updated_by       BIGINT REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED,

  CONSTRAINT feed_consumption_date_uk UNIQUE (consumption_date)
);

CREATE INDEX IF NOT EXISTS feed_consumption_date_idx
  ON feed_consumption (consumption_date DESC);

DROP TRIGGER IF EXISTS feed_consumption_touch_updated_at ON feed_consumption;
CREATE TRIGGER feed_consumption_touch_updated_at
BEFORE UPDATE ON feed_consumption
FOR EACH ROW
EXECUTE FUNCTION trg_touch_updated_at();

-- =========================
--  SCHEMA: mortality_event
-- =========================
CREATE TABLE IF NOT EXISTS mortality_event (
  id               BIGSERIAL PRIMARY KEY,

  event_date       DATE NOT NULL,
  bird_type        VARCHAR(15) NOT NULL,  -- 'juvenile' | 'male' | 'hen'
  quantity         INTEGER NOT NULL CHECK (quantity > 0),
  cause            VARCHAR(150) NOT NULL, -- texto breve, ej. "enfermedad respiratoria"
  notes            TEXT,                  -- detalles opcionales

  -- Auditoría
  is_active        BOOLEAN     NOT NULL DEFAULT TRUE,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_by       BIGINT REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED,
  updated_by       BIGINT REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED,

  CONSTRAINT mortality_event_type_ck
    CHECK (bird_type IN ('juvenile','male','hen'))
);

-- Índices para consultas rápidas
CREATE INDEX IF NOT EXISTS mortality_event_date_idx
  ON mortality_event (event_date DESC);

CREATE INDEX IF NOT EXISTS mortality_event_type_idx
  ON mortality_event (bird_type);

-- Trigger para mantener updated_at
DROP TRIGGER IF EXISTS mortality_event_touch_updated_at ON mortality_event;
CREATE TRIGGER mortality_event_touch_updated_at
BEFORE UPDATE ON mortality_event
FOR EACH ROW
EXECUTE FUNCTION trg_touch_updated_at();

-- =========================
--  SCHEMA: finance_category
-- =========================
CREATE TABLE IF NOT EXISTS finance_category (
  id               BIGSERIAL PRIMARY KEY,
  category_name    VARCHAR(100) NOT NULL,
  type             VARCHAR(10)  NOT NULL, -- 'income' | 'expense'
  description      TEXT,

  -- Auditoría
  is_active        BOOLEAN     NOT NULL DEFAULT TRUE,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_by       BIGINT REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED,
  updated_by       BIGINT REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED,

  CONSTRAINT finance_category_type_ck
    CHECK (type IN ('income','expense'))
);


CREATE UNIQUE INDEX IF NOT EXISTS finance_category_name_lower_uk
  ON finance_category (LOWER(category_name), type);

DROP TRIGGER IF EXISTS finance_category_touch_updated_at ON finance_category;
CREATE TRIGGER finance_category_touch_updated_at
BEFORE UPDATE ON finance_category
FOR EACH ROW
EXECUTE FUNCTION trg_touch_updated_at();

--Ejemplos iniciales (semilla)
INSERT INTO finance_category (category_name, type, description) VALUES
  ('Venta de huevos', 'income', 'Ingreso por venta de producción'),
  ('Compra de alimento', 'expense', 'Gasto en insumos de alimentación'),
  ('Medicamentos veterinarios', 'expense', 'Tratamientos sanitarios'),
  ('Transporte', 'expense', 'Traslado de productos y materiales');

-- =========================
--  SCHEMA: finance_transaction
-- =========================
CREATE TABLE IF NOT EXISTS finance_transaction (
  id                  BIGSERIAL PRIMARY KEY,
  transaction_date    DATE NOT NULL,
  category_id         BIGINT NOT NULL REFERENCES finance_category(id),
  description         TEXT,
  amount_clp          NUMERIC(14,2) NOT NULL CHECK (amount_clp >= 0),
  payment_method      VARCHAR(30) DEFAULT 'efectivo',  -- efectivo, transferencia, etc.
  reference_doc       VARCHAR(100),                    -- opcional: N° boleta, factura, etc.
  notes               TEXT,

  -- Auditoría
  is_active           BOOLEAN     NOT NULL DEFAULT TRUE,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_by          BIGINT REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED,
  updated_by          BIGINT REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS finance_transaction_date_idx
  ON finance_transaction (transaction_date DESC);

CREATE INDEX IF NOT EXISTS finance_transaction_cat_idx
  ON finance_transaction (category_id);

DROP TRIGGER IF EXISTS finance_transaction_touch_updated_at ON finance_transaction;
CREATE TRIGGER finance_transaction_touch_updated_at
BEFORE UPDATE ON finance_transaction
FOR EACH ROW
EXECUTE FUNCTION trg_touch_updated_at();


-- =========================
--  SCHEMA: finance_summary
-- =========================
CREATE TABLE IF NOT EXISTS finance_summary (
  id                 BIGSERIAL PRIMARY KEY,
  year_month         CHAR(7) NOT NULL,  -- formato 'YYYY-MM'
  total_income_clp   NUMERIC(14,2) NOT NULL DEFAULT 0,
  total_expense_clp  NUMERIC(14,2) NOT NULL DEFAULT 0,
  balance_clp        NUMERIC(14,2) GENERATED ALWAYS AS (total_income_clp - total_expense_clp) STORED,

  -- Auditoría
  generated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  generated_by       BIGINT REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED,
  is_active          BOOLEAN NOT NULL DEFAULT TRUE,

  CONSTRAINT finance_summary_month_uk UNIQUE (year_month)
);


-- =========================
--  SCHEMA: report_export
-- =========================
CREATE TABLE IF NOT EXISTS report_export (
  id               BIGSERIAL PRIMARY KEY,

  -- Identidad del reporte
  report_type      VARCHAR(50) NOT NULL,     -- p.ej. 'daily_summary', 'weekly_finance', 'kpi_dashboard'
  period_start     DATE,                     -- opcional (si corresponde)
  period_end       DATE,                     -- opcional (si corresponde)
  file_format      VARCHAR(10) NOT NULL,     -- 'pdf' | 'xlsx' | 'csv' | 'png'
  file_path        TEXT NOT NULL,            -- ruta/URL donde quedó almacenado
  file_size_bytes  BIGINT CHECK (file_size_bytes IS NULL OR file_size_bytes >= 0),

  -- Auditoría de creación/actualización
  is_active        BOOLEAN     NOT NULL DEFAULT TRUE,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_by       BIGINT REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED,
  updated_by       BIGINT REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED,

  -- Papelera (borrado lógico)
  deleted_at       TIMESTAMPTZ,
  deleted_by       BIGINT REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED,

  -- Reglas
  CONSTRAINT report_export_format_ck
    CHECK (file_format IN ('pdf','xlsx','csv','png'))
);

-- Índices útiles
CREATE INDEX IF NOT EXISTS report_export_type_idx      ON report_export (report_type);
CREATE INDEX IF NOT EXISTS report_export_created_desc  ON report_export (created_at DESC);
CREATE INDEX IF NOT EXISTS report_export_deleted_idx   ON report_export (deleted_at);

-- Trigger updated_at
DROP TRIGGER IF EXISTS report_export_touch_updated_at ON report_export;
CREATE TRIGGER report_export_touch_updated_at
BEFORE UPDATE ON report_export
FOR EACH ROW
EXECUTE FUNCTION trg_touch_updated_at();

