import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

# 加载项目根目录下的 .env 文件（不入 git）
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_PROJECT_ROOT / ".env")


def _require_env(name: str) -> str:
    """读取必填环境变量，缺失时给出明确报错。"""
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"环境变量 {name} 未设置。请在项目根目录的 .env 文件中配置后重试。"
        )
    return value


MINIMAX_MODEL_NAME = os.environ.get("MINIMAX_MODEL_NAME", "MiniMaxi-M3")
MINIMAX_API_URL = os.environ.get("MINIMAX_API_URL", "https://api.minimaxi.com/anthropic")
MINIMAX_API_KEY = _require_env("MINIMAX_API_KEY")


config_chat_model = ChatAnthropic(
    model=MINIMAX_MODEL_NAME,                    # 或 MiniMax-M2.7 / M2.5 / M2-her 等
    base_url=MINIMAX_API_URL,
    api_key=MINIMAX_API_KEY,
    max_tokens=1024,
)
