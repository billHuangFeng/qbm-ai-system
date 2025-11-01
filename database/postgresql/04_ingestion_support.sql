-- Ingestion Support DDL (batches/logs/quality/rules/dictionary)
-- Safe to run multiple times

BEGIN;

CREATE TABLE IF NOT EXISTS ingestion_batches (
    batch_id            VARCHAR(64) PRIMARY KEY,
    source_system       VARCHAR(64) NOT NULL,
    window_start_ts     TIMESTAMP NULL,
    window_end_ts       TIMESTAMP NULL,
    file_list           JSONB NULL,
    started_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at        TIMESTAMP NULL,
    status              VARCHAR(24) NOT NULL DEFAULT 'started',
    notes               TEXT NULL
);

CREATE INDEX IF NOT EXISTS idx_ingestion_batches_status ON ingestion_batches(status);
CREATE INDEX IF NOT EXISTS idx_ingestion_batches_started ON ingestion_batches(started_at);

CREATE TABLE IF NOT EXISTS ingestion_logs (
    id                  BIGSERIAL PRIMARY KEY,
    batch_id            VARCHAR(64) NOT NULL REFERENCES ingestion_batches(batch_id) ON DELETE CASCADE,
    table_name          VARCHAR(128) NOT NULL,
    row_cnt             BIGINT NOT NULL DEFAULT 0,
    checksum            VARCHAR(64) NULL,
    error_cnt           BIGINT NOT NULL DEFAULT 0,
    sample_errors       JSONB NULL,
    created_at          TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ingestion_logs_batch ON ingestion_logs(batch_id);

CREATE TABLE IF NOT EXISTS data_quality_checks (
    id                  BIGSERIAL PRIMARY KEY,
    batch_id            VARCHAR(64) NOT NULL REFERENCES ingestion_batches(batch_id) ON DELETE CASCADE,
    rule_id             VARCHAR(64) NOT NULL,
    passed              BOOLEAN NOT NULL,
    failed_cnt          BIGINT NOT NULL DEFAULT 0,
    sample_refs         JSONB NULL,
    created_at          TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_quality_checks_batch ON data_quality_checks(batch_id);
CREATE INDEX IF NOT EXISTS idx_quality_checks_rule  ON data_quality_checks(rule_id);

CREATE TABLE IF NOT EXISTS transform_rules (
    rule_id             VARCHAR(64) PRIMARY KEY,
    rule_name           VARCHAR(128) NOT NULL,
    rule_sql            TEXT NULL,
    params              JSONB NULL,
    version             INT NOT NULL DEFAULT 1,
    checksum            VARCHAR(64) NULL,
    enabled             BOOLEAN NOT NULL DEFAULT TRUE,
    updated_at          TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS alias_dictionary (
    id                  BIGSERIAL PRIMARY KEY,
    dict_type           VARCHAR(64) NOT NULL,
    src_value           VARCHAR(256) NOT NULL,
    std_value           VARCHAR(256) NOT NULL,
    confidence          NUMERIC(5,4) NOT NULL DEFAULT 0.9500,
    updated_by          VARCHAR(64) NULL,
    updated_at          TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alias_dict_type   ON alias_dictionary(dict_type);
CREATE INDEX IF NOT EXISTS idx_alias_src_value   ON alias_dictionary(src_value);

COMMIT;

-- Rollback helper (manual)
-- BEGIN;
-- DROP TABLE IF EXISTS alias_dictionary;
-- DROP TABLE IF EXISTS transform_rules;
-- DROP TABLE IF EXISTS data_quality_checks;
-- DROP TABLE IF EXISTS ingestion_logs;
-- DROP TABLE IF EXISTS ingestion_batches;
-- COMMIT;



