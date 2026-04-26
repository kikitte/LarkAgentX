import os

from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings"""

    DATA_DIR = os.getenv("DATA_DIR", "").strip()
    if not DATA_DIR:
        raise ValueError("DATA_DIR 未设置，请在 .env 中配置 DATA_DIR")
    os.makedirs(DATA_DIR, exist_ok=True)
    DB_PATH = os.path.join(DATA_DIR, os.getenv("DB_PATH", "lark_messages.db"))
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"

    LARK_COOKIE = os.getenv("LARK_COOKIE", "")
    LARK_BASE_URL = "https://internal-api-lark-api.feishu.cn/im/gateway/"
    LARK_CSRF_TOKEN_URL = "https://internal-api-lark-api.feishu.cn/accounts/csrf"
    LARK_USER_INFO_URL = "https://internal-api-lark-api.feishu.cn/accounts/web/user"
    LARK_WS_URL = "wss://msg-frontier.feishu.cn/ws/v2"
    
    FUNCTION_TRIGGER_FLAG = os.getenv("FUNCTION_TRIGGER_FLAG", "/run")

    AI_BOT_PREFIX = os.getenv("AI_BOT_PREFIX", "AI Bot:")

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_API_BASE_URL = os.getenv("OPENAI_API_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    OPENAI_API_MODEL = os.getenv("OPENAI_API_MODEL", "qwen-plus")
    # ENVIRON = {}
    # for i in os.getenv("ENVIRON", "").split(";"):
    #     if '=' not in i:
    #         continue
    #     ENVIRON.update({i.split("=")[0]: i.split("=")[1]})


settings = Settings()
