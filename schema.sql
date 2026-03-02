-- Partner-Evolution 数据库表结构
-- PostgreSQL + pgvector

-- 启用pgvector扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 记忆表
CREATE TABLE IF NOT EXISTS memories (
    id VARCHAR(100) PRIMARY KEY,
    tier VARCHAR(20) NOT NULL CHECK (tier IN ('core', 'recall', 'archival')),
    memory_type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(1024),
    confidence FLOAT DEFAULT 1.0 CHECK (confidence >= 0 AND confidence <= 1),
    importance FLOAT DEFAULT 0.5 CHECK (importance >= 0 AND importance <= 1),
    created_at TIMESTAMP DEFAULT NOW(),
    last_accessed TIMESTAMP DEFAULT NOW(),
    last_edited TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    CONSTRAINT embedding_dim CHECK (vector_dims(embedding) = 1024)
);

-- 创建HNSW向量索引
CREATE INDEX IF NOT EXISTS memory_embedding_idx ON memories 
USING hnsw (embedding vector_cosine_ops) 
WITH (m = 16, ef_construction = 64);

-- 创建tier索引
CREATE INDEX IF NOT EXISTS memory_tier_idx ON memories (tier);

-- 创建时间索引
CREATE INDEX IF NOT EXISTS memory_created_idx ON memories (created_at DESC);

-- 创建最后访问索引
CREATE INDEX IF NOT EXISTS memory_accessed_idx ON memories (last_accessed DESC);

-- 关系表
CREATE TABLE IF NOT EXISTS memory_relations (
    id SERIAL PRIMARY KEY,
    from_id VARCHAR(100) NOT NULL REFERENCES memories(id) ON DELETE CASCADE,
    to_id VARCHAR(100) NOT NULL REFERENCES memories(id) ON DELETE CASCADE,
    relation_type VARCHAR(50) NOT NULL,
    strength FLOAT DEFAULT 0.5 CHECK (strength >= 0 AND strength <= 1),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(from_id, to_id, relation_type)
);

CREATE INDEX IF NOT EXISTS relation_from_idx ON memory_relations (from_id);
CREATE INDEX IF NOT EXISTS relation_to_idx ON memory_relations (to_id);

-- 指标表
CREATE TABLE IF NOT EXISTS memory_metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    metric_type VARCHAR(50) NOT NULL,
    value FLOAT NOT NULL,
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS metrics_timestamp_idx ON memory_metrics (timestamp DESC);
CREATE INDEX IF NOT EXISTS metrics_type_idx ON memory_metrics (metric_type);

-- 思考记录表
CREATE TABLE IF NOT EXISTS thinking_records (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    mode VARCHAR(50) NOT NULL,
    context JSONB DEFAULT '{}',
    result JSONB DEFAULT '{}',
    confidence FLOAT DEFAULT 0.5,
    insights_count INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS thinking_timestamp_idx ON thinking_records (timestamp DESC);
CREATE INDEX IF NOT EXISTS thinking_mode_idx ON thinking_records (mode);

-- 工作流记录表
CREATE TABLE IF NOT EXISTS workflow_records (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    task_description TEXT NOT NULL,
    analysis JSONB DEFAULT '{}',
    routes JSONB DEFAULT '[]',
    results JSONB DEFAULT '{}',
    final_result JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'pending',
    error TEXT
);

CREATE INDEX IF NOT EXISTS workflow_timestamp_idx ON workflow_records (timestamp DESC);
CREATE INDEX IF NOT EXISTS workflow_status_idx ON workflow_records (status);

-- 告警表
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    alert_type VARCHAR(50) NOT NULL,
    level VARCHAR(10) NOT NULL CHECK (level IN ('P0', 'P1', 'P2', 'P3')),
    message TEXT NOT NULL,
    data JSONB DEFAULT '{}',
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_at TIMESTAMP,
    acknowledged_by VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS alerts_timestamp_idx ON alerts (timestamp DESC);
CREATE INDEX IF NOT EXISTS alerts_level_idx ON alerts (level);
CREATE INDEX IF NOT EXISTS alerts_ack_idx ON alerts (acknowledged);

-- 审计日志表
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    user_id VARCHAR(100),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(100),
    details JSONB DEFAULT '{}',
    ip_address VARCHAR(45)
);

CREATE INDEX IF NOT EXISTS audit_timestamp_idx ON audit_logs (timestamp DESC);
CREATE INDEX IF NOT EXISTS audit_user_idx ON audit_logs (user_id);
CREATE INDEX IF NOT EXISTS audit_action_idx ON audit_logs (action);

-- 视图：活跃告警
CREATE OR REPLACE VIEW active_alerts AS
SELECT * FROM alerts 
WHERE acknowledged = FALSE 
ORDER BY 
    CASE level 
        WHEN 'P0' THEN 1 
        WHEN 'P1' THEN 2 
        WHEN 'P2' THEN 3 
        ELSE 4 
    END,
    timestamp DESC;

-- 视图：记忆统计
CREATE OR REPLACE VIEW memory_stats AS
SELECT 
    tier,
    memory_type,
    COUNT(*) as count,
    AVG(confidence) as avg_confidence,
    MIN(created_at) as oldest,
    MAX(created_at) as newest
FROM memories
GROUP BY tier, memory_type;

-- 函数：自动更新最后访问时间
CREATE OR REPLACE FUNCTION update_last_accessed()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_accessed = NOW();
    NEW.access_count = COALESCE(OLD.access_count, 0) + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 触发器：更新访问时间
CREATE TRIGGER memory_access_trigger
    BEFORE UPDATE ON memories
    FOR EACH ROW
    EXECUTE FUNCTION update_last_accessed();

-- 插入初始数据
INSERT INTO memories (id, tier, memory_type, content, confidence) VALUES
    ('sys_core_1', 'core', 'config', 'AI助手必须在每天9点主动签到', 0.95),
    ('sys_core_2', 'core', 'config', '70%真实大于100%幻觉是核心原则', 1.0)
ON CONFLICT (id) DO NOTHING;

-- 注释
COMMENT ON TABLE memories IS '统一记忆存储';
COMMENT ON TABLE memory_relations IS '记忆之间的关联关系';
COMMENT ON TABLE memory_metrics IS '系统运行指标';
COMMENT ON TABLE thinking_records IS '思考引擎执行记录';
COMMENT ON TABLE workflow_records IS '工作流执行记录';
COMMENT ON TABLE alerts IS '系统告警';
COMMENT ON TABLE audit_logs IS '操作审计日志';

-- =====================================================
-- v2.1/v2.2 新增表
-- =====================================================

-- 信念表（v2.2自主意识）
CREATE TABLE IF NOT EXISTS beliefs (
    id VARCHAR(100) PRIMARY KEY,
    content TEXT NOT NULL,
    belief_type VARCHAR(50) NOT NULL CHECK (belief_type IN ('factual', 'value', 'prediction', 'preference')),
    confidence FLOAT DEFAULT 0.5 CHECK (confidence >= 0 AND confidence <= 1),
    stance VARCHAR(32) DEFAULT 'neutral' CHECK (stance IN ('positive', 'negative', 'neutral', 'exploratory')),
    source_type VARCHAR(32) DEFAULT 'self_reflection' CHECK (source_type IN ('user_input', 'self_reflection', 'external_knowledge')),
    source_id TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    version INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'challenged', 'retired')),
    challenge_history JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS belief_status_idx ON beliefs (status);
CREATE INDEX IF NOT EXISTS belief_confidence_idx ON beliefs (confidence DESC);
CREATE INDEX IF NOT EXISTS belief_type_idx ON beliefs (belief_type);
CREATE INDEX IF NOT EXISTS belief_source_idx ON beliefs (source_type, source_id);

-- 自主目标表（v2.2目标引擎）
CREATE TABLE IF NOT EXISTS autonomous_goals (
    id VARCHAR(100) PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    goal_type VARCHAR(50) NOT NULL CHECK (goal_type IN ('exploration', 'optimization', 'defense')),
    priority INTEGER DEFAULT 3 CHECK (priority >= 1 AND priority <= 10),
    status VARCHAR(32) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'paused', 'cancelled', 'achieved', 'abandoned')),
    horizon VARCHAR(32) DEFAULT 'medium' CHECK (horizon IN ('short', 'medium', 'long')),
    owner_type VARCHAR(32) DEFAULT 'self' CHECK (owner_type IN ('self', 'user', 'joint')),
    created_from TEXT,
    deadline TIMESTAMP,
    progress FLOAT DEFAULT 0.0 CHECK (progress >= 0 AND progress <= 100),
    curiosity_score FLOAT DEFAULT 0.5,
    importance_score FLOAT DEFAULT 0.5,
    feasibility_score FLOAT DEFAULT 0.5,
    resource_estimate INTEGER DEFAULT 5,
    iterations INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS goal_status_idx ON autonomous_goals (status);
CREATE INDEX IF NOT EXISTS goal_priority_idx ON autonomous_goals (priority);
CREATE INDEX IF NOT EXISTS goal_type_idx ON autonomous_goals (goal_type);
CREATE INDEX IF NOT EXISTS goal_horizon_idx ON autonomous_goals (horizon);

-- 版本历史表（v3.0递归进化准备）
CREATE TABLE IF NOT EXISTS version_history (
    id VARCHAR(100) PRIMARY KEY,
    version VARCHAR(20) NOT NULL,
    parent_version VARCHAR(20),
    genome_id VARCHAR(100),
    changes JSONB DEFAULT '[]',
    message TEXT,
    author VARCHAR(100) DEFAULT 'Partner-Evolution',
    fitness_score FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS version_idx ON version_history (version);
CREATE INDEX IF NOT EXISTS version_parent_idx ON version_history (parent_version);

-- 交互日志表
CREATE TABLE IF NOT EXISTS interaction_logs (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100),
    user_id VARCHAR(100),
    message_type VARCHAR(20) NOT NULL,
    content TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS interaction_session_idx ON interaction_logs (session_id);
CREATE INDEX IF NOT EXISTS interaction_created_idx ON interaction_logs (created_at DESC);
