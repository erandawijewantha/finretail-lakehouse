CREATE TABLE IF NOT EXISTS control.pipeline_run (
    run_id BIGSERIAL PRIMARY KEY,
    pipeline_name VARCHAR(150) NOT NULL,
    dag_id VARCHAR(150),
    task_id VARCHAR(150),
    run_reference VARCHAR(255),
    status VARCHAR(30) NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS control.file_registry (
    file_id BIGSERIAL PRIMARY KEY,
    source_system VARCHAR(100) NOT NULL,
    entity_name VARCHAR(100) NOT NULL,
    object_key TEXT NOT NULL,
    file_checksum VARCHAR(128) NOT NULL,
    file_size_bytes BIGINT,
    row_count BIGINT,
    landed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    status VARCHAR(30) DEFAULT 'LANDED',
    UNIQUE (object_key, file_checksum)
);

CREATE TABLE IF NOT EXISTS control.watermark (
    entity_name VARCHAR(100) PRIMARY KEY,
    watermark_column VARCHAR(100) NOT NULL,
    last_watermark_value TIMESTAMP,
    last_successful_run_id BIGINT,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit.data_quality_result (
    dq_result_id BIGSERIAL PRIMARY KEY,
    run_id BIGINT,
    layer_name VARCHAR(50),
    table_name VARCHAR(150),
    check_name VARCHAR(150),
    check_status VARCHAR(30),
    failed_count BIGINT,
    checked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    details TEXT
);