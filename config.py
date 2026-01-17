import os
from dotenv import load_dotenv

load_dotenv()

# Angel One Credentials
API_KEY = os.getenv("ANGEL_API_KEY")
CLIENT_ID = os.getenv("ANGEL_CLIENT_ID")
PASSWORD = os.getenv("ANGEL_PASSWORD")
TOTP_KEY = os.getenv("ANGEL_TOTP_KEY")

# Telegram Credentials - EQUITY (NIFTY/FNO)
TELEGRAM_BOT_TOKEN_EQUITY = os.getenv("TELEGRAM_BOT_TOKEN_EQUITY")
TELEGRAM_CHAT_ID_EQUITY = os.getenv("TELEGRAM_CHAT_ID_EQUITY")

# Telegram Credentials - CRYPTO (BTC/ETH)
TELEGRAM_BOT_TOKEN_CRYPTO = os.getenv("TELEGRAM_BOT_TOKEN_CRYPTO")
TELEGRAM_CHAT_ID_CRYPTO = os.getenv("TELEGRAM_CHAT_ID_CRYPTO")

# Delta Exchange Credentials (Optional for public data)
DELTA_API_KEY = os.getenv("DELTA_API_KEY")
DELTA_API_SECRET = os.getenv("DELTA_API_SECRET")

# Crypto Symbols (Delta Exchange)
CRYPTO_SYMBOLS = ["BTCUSD", "ETHUSD"]

# Equity Symbols
# Nifty 50 Token (Angel One)
NIFTY_SYMBOL = {
    "symbol": "NIFTY", 
    "token": "99926000", 
    "exchange": "NSE"
}
# FNO Stocks will be disabled, only using Nifty
EQUITY_SYMBOLS = [NIFTY_SYMBOL]

# Timeframes for BTST Strategy
TIMEFRAMES = ["ONE_DAY", "FOUR_HOUR", "ONE_HOUR", "FIFTEEN_MINUTE"]

# BTST Strategy Parameters
BB_PERIOD = 20              # Bollinger Bands period (20 SMA)
BB_STD_DEV = 2              # Standard deviation multiplier
RSI_PERIOD = 14             # RSI period for divergence detection
VOLUME_MULTIPLIER = 1.5     # Volume must be 1.5x average for confirmation
BB_PROXIMITY_THRESHOLD = 0.05  # 5% from band to be considered "near" (relaxed from 2%)

# Scan Interval (minutes)
SCAN_INTERVAL_MINUTES = 15

# Alert Deduplication Window (minutes)
ALERT_COOLDOWN_MINUTES = 60
