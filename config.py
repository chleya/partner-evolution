"""
配置管理模块
"""
import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 数据存储目录
DATA_DIR = PROJECT_ROOT / "data"
MEMORY_DIR = DATA_DIR / "memory"
LOGS_DIR = DATA_DIR / "logs"

# 创建必要目录
MEMORY_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# 数据库配置
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "user": os.getenv("DB_USER", "ai_partner"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_DB", "ai_partner_db"),
}

# Redis配置
REDIS_CONFIG = {
    "host": os.getenv("REDIS_HOST", "localhost"),
    "port": int(os.getenv("REDIS_PORT", "6379")),
    "password": os.getenv("REDIS_PASSWORD", ""),
}

# LLM配置
LLM_CONFIG = {
    "provider": os.getenv("LLM_PROVIDER", "minimax"),
    "api_key": os.getenv("LLM_API_KEY", ""),
    "model": os.getenv("LLM_MODEL", "MiniMax-M2.5"),
    "base_url": os.getenv("LLM_BASE_URL", "https://api.minimax.chat/v1"),
}

# 嵌入模型配置
EMBEDDING_CONFIG = {
    "provider": os.getenv("EMBEDDING_PROVIDER", "sentence-transformers"),
    "model": os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
    "dimension": int(os.getenv("EMBEDDING_DIMENSION", "384")),
}

# 记忆系统配置
MEMORY_CONFIG = {
    "max_context_tokens": int(os.getenv("MAX_CONTEXT_TOKENS", "8000")),
    "forget_threshold": float(os.getenv("FORGET_THRESHOLD", "0.2")),
    "decay_rate": float(os.getenv("DECAY_RATE", "0.05")),
    "vector_top_k": int(os.getenv("VECTOR_TOP_K", "20")),
    "similarity_threshold": float(os.getenv("SIMILARITY_THRESHOLD", "0.5")),
}

# 思考引擎配置
THINKING_CONFIG = {
    "target_daily_thinks": int(os.getenv("TARGET_DAILY_THINKS", "3")),
    "active_hours": os.getenv("ACTIVE_HOURS", "09:00-18:00"),
    "mar_judge_threshold": float(os.getenv("MAR_JUDGE_THRESHOLD", "0.7")),
}

# 服务配置
SERVICE_CONFIG = {
    "api_host": os.getenv("API_HOST", "0.0.0.0"),
    "api_port": int(os.getenv("API_PORT", "5000")),
    "heartbeat_interval": int(os.getenv("HEARTBEAT_INTERVAL", "3600")),
    "alert_retry_count": int(os.getenv("ALERT_RETRY_COUNT", "3")),
}

# 日志配置
LOG_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": str(LOGS_DIR / "agent.log"),
}

# 项目联动配置
PROJECT_CONFIG = {
    "neuralsite": {
        "location": r"F:\drawing_3d",
        "api_port": 5001,
        "role": "executor",
    },
    "evo_swarm": {
        "location": r"F:\skill\evo_swarm",
        "github": "https://github.com/chleya/Evo-Swarm",
        "role": "planner",
    },
    "visual_cot": {
        "location": r"F:\skill\evo_swarm\visual_chain_of_thought.py",
        "role": "perceiver",
    },
}
