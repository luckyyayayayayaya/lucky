import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
if not ANTHROPIC_API_KEY:
    raise RuntimeError("请在 .env 文件中设置 ANTHROPIC_API_KEY")

DATABASE_PATH = BASE_DIR / "data" / "goodluck_tooth.db"

CLAUDE_MODEL = "claude-sonnet-4-20250514"

MORNING_START = 5
MORNING_END = 12
EVENING_START = 17
EVENING_END = 23

MAX_THOUGHTS_PER_DAY = 50
MAX_TOKENS_ANALYSIS = 300
MAX_TOKENS_DAILY = 250
TEMPERATURE_WARM = 0.9
TEMPERATURE_VARIED = 1.0
