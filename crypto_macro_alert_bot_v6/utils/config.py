import os
from dotenv import load_dotenv

# Tải biến môi trường từ file .env
load_dotenv()

# Cấu hình Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Cấu hình kiểm tra
CHECK_INTERVAL_MINUTES = 15  # Kiểm tra mỗi 5 phút

# Các cặp tiền và khung thời gian cần theo dõi
SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT"]
TIMEFRAMES = ["1h", "4h", "1d"]

# Ngưỡng RSI
RSI_OVERSOLD_THRESHOLD = 30
RSI_OVERBOUGHT_THRESHOLD = 70

# Cấu hình cho từng cặp tiền
SYMBOL_CONFIGS = {
    'BTCUSDT': {
        'rsi_oversold': 30,
        'rsi_overbought': 70,
        'macd_fast': 12,
        'macd_slow': 26,
        'macd_signal': 9,
        'rsi_period': 14,
        'stoch_k': 14,
        'stoch_d': 3,
        'bb_period': 20,
        'bb_std': 2
    },
    'ETHUSDT': {
        'rsi_oversold': 25,
        'rsi_overbought': 75,
        'macd_fast': 10,
        'macd_slow': 25,
        'macd_signal': 8,
        'rsi_period': 14,
        'stoch_k': 14,
        'stoch_d': 3,
        'bb_period': 20,
        'bb_std': 2
    },
    'BNBUSDT': {
        'rsi_oversold': 28,
        'rsi_overbought': 72,
        'macd_fast': 12,
        'macd_slow': 26,
        'macd_signal': 9,
        'rsi_period': 14,
        'stoch_k': 14,
        'stoch_d': 3,
        'bb_period': 20,
        'bb_std': 2
    },
    'ADAUSDT': {
        'rsi_oversold': 25,
        'rsi_overbought': 75,
        'macd_fast': 10,
        'macd_slow': 25,
        'macd_signal': 8,
        'rsi_period': 14,
        'stoch_k': 14,
        'stoch_d': 3,
        'bb_period': 20,
        'bb_std': 2
    },
    'SOLUSDT': {
        'rsi_oversold': 28,
        'rsi_overbought': 72,
        'macd_fast': 12,
        'macd_slow': 26,
        'macd_signal': 9,
        'rsi_period': 14,
        'stoch_k': 14,
        'stoch_d': 3,
        'bb_period': 20,
        'bb_std': 2
    },
    'DEFAULT': {
        'rsi_oversold': 30,
        'rsi_overbought': 70,
        'macd_fast': 12,
        'macd_slow': 26,
        'macd_signal': 9,
        'rsi_period': 14,
        'stoch_k': 14,
        'stoch_d': 3,
        'bb_period': 20,
        'bb_std': 2
    }
}

# Cấu hình hệ thống phân tích category
CATEGORY_REPORT_ENABLED = True
CATEGORY_REPORT_TIME = "09:00"  # Gửi vào 9h sáng hàng ngày

# Các category cần phân tích
CATEGORIES_CONFIG = {
    "L1": {
        "name": "L1 Blockchain",
        "subcategories": [
            {"name": "BNB Ecosystem", "symbol": "BNB"},
            {"name": "SOL Ecosystem", "symbol": "SOL"},
            {"name": "ETH Ecosystem", "symbol": "ETH"},
            {"name": "SUI Ecosystem", "symbol": "SUI"}
        ],
        "top_projects": 3
    },
    "AI": {
        "name": "AI & Big Data",
        "subcategories": [],
        "top_projects": 10
    },
    "RWA": {
        "name": "Real World Assets Protocols",
        "subcategories": [],
        "top_projects": 10
    },
    "DePin": {
        "name": "DePin",
        "subcategories": [],
        "top_projects": 10
    }
}

# Tạo class Config để đóng gói các biến
class Config:
    TELEGRAM_BOT_TOKEN = TELEGRAM_BOT_TOKEN
    TELEGRAM_CHAT_ID = TELEGRAM_CHAT_ID
    CHECK_INTERVAL_MINUTES = CHECK_INTERVAL_MINUTES
    SYMBOLS = SYMBOLS
    TIMEFRAMES = TIMEFRAMES
    RSI_OVERSOLD_THRESHOLD = RSI_OVERSOLD_THRESHOLD
    RSI_OVERBOUGHT_THRESHOLD = RSI_OVERBOUGHT_THRESHOLD
    SYMBOL_CONFIGS = SYMBOL_CONFIGS
    CATEGORY_REPORT_ENABLED = CATEGORY_REPORT_ENABLED
    CATEGORY_REPORT_TIME = CATEGORY_REPORT_TIME
    CATEGORIES_CONFIG = CATEGORIES_CONFIG
