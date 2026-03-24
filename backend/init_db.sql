-- ============================================================
-- 对话式数据报表系统 — PostgreSQL 15 数据库初始化脚本
-- 基于 7 大领域模块的 SQLAlchemy 模型定义
-- ============================================================

-- 1. Auth 模块：用户表
CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    username        VARCHAR(100) NOT NULL UNIQUE,
    email           VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    is_active       BOOLEAN DEFAULT TRUE,
    role            VARCHAR(50) DEFAULT 'user',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- 2. Chat 模块：会话表 + 消息表
CREATE TABLE IF NOT EXISTS conversations (
    id          SERIAL PRIMARY KEY,
    title       VARCHAR(255),
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS messages (
    id                SERIAL PRIMARY KEY,
    conversation_id   INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role              VARCHAR(50) NOT NULL,
    content           TEXT NOT NULL,
    created_at        TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_messages_conv_id ON messages(conversation_id);

-- 3. DataSource 模块：数据源表
CREATE TABLE IF NOT EXISTS datasources (
    id                  SERIAL PRIMARY KEY,
    name                VARCHAR(100) NOT NULL UNIQUE,
    db_type             VARCHAR(50) NOT NULL,
    connection_string   VARCHAR(500) NOT NULL,
    description         VARCHAR(500),
    is_active           BOOLEAN DEFAULT TRUE,
    created_by          INTEGER REFERENCES users(id),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ
);

-- 4. Query 模块：查询记录表
CREATE TABLE IF NOT EXISTS query_records (
    id                SERIAL PRIMARY KEY,
    datasource_id     INTEGER NOT NULL REFERENCES datasources(id),
    natural_language  TEXT NOT NULL,
    generated_sql     TEXT,
    result_summary    TEXT,
    status            VARCHAR(50) DEFAULT 'pending',
    created_by        INTEGER REFERENCES users(id),
    created_at        TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_query_records_ds_id ON query_records(datasource_id);
CREATE INDEX IF NOT EXISTS idx_query_records_status ON query_records(status);

-- 5. Chart 模块：图表配置表
CREATE TABLE IF NOT EXISTS chart_configs (
    id          SERIAL PRIMARY KEY,
    query_id    INTEGER REFERENCES query_records(id),
    chart_type  VARCHAR(50) NOT NULL,
    title       VARCHAR(255),
    config_json JSONB NOT NULL,
    created_by  INTEGER REFERENCES users(id),
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_chart_configs_query_id ON chart_configs(query_id);

-- 6. Insight 模块：数据洞察表
CREATE TABLE IF NOT EXISTS insights (
    id            SERIAL PRIMARY KEY,
    query_id      INTEGER REFERENCES query_records(id),
    summary       TEXT NOT NULL,
    key_findings  JSONB,
    suggestions   JSONB,
    created_by    INTEGER REFERENCES users(id),
    created_at    TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_insights_query_id ON insights(query_id);

-- 7. Report 模块：报表表 + 报表组件项表
CREATE TABLE IF NOT EXISTS reports (
    id              SERIAL PRIMARY KEY,
    title           VARCHAR(255) NOT NULL,
    description     TEXT,
    layout_config   JSONB,
    is_published    BOOLEAN DEFAULT FALSE,
    created_by      INTEGER REFERENCES users(id),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS report_items (
    id            SERIAL PRIMARY KEY,
    report_id     INTEGER NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    item_type     VARCHAR(50) NOT NULL,
    reference_id  INTEGER,
    position      INTEGER DEFAULT 0,
    config_json   JSONB,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_report_items_report_id ON report_items(report_id);
