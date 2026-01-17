# BTST Strategy Bot

A trading bot that detects **BTST (Bollinger Trigger Swing Trade)** reversal setups across multiple timeframes for both crypto and equity markets.

## Strategy Overview

The BTST strategy identifies high-probability trend reversals using:

### Core Components
1. **Two-Candle Reversal Pattern**
   - **Buy Setup**: Red candle → Green candle (makes new low, closes above)
   - **Sell Setup**: Green candle → Red candle (makes new high, closes below)

2. **Bollinger Bands Positioning**
   - Buy setups near lower band
   - Sell setups near upper band

3. **Volume Confirmation** (context-dependent)
   - Buy setups: Volume required on ALL timeframes
   - Sell setups (1H/1D): Volume optional
   - Sell setups (15M): Volume required

4. **BB "Fake Head"** (bonus confirmation)
   - Price punctures BB but closes back inside
   - Indicates trapped traders

5. **RSI Divergence** (optional enhancement)
   - Bullish/Bearish divergence for extra confirmation

### Timeframes
- **1 Day** - Swing trading setups
- **1 Hour** - Intraday/swing setups
- **15 Minutes** - Intraday scalping setups

### Markets
- **Crypto**: BTC/ETH via Delta Exchange
- **Equity**: Nifty/FNO via Angel One (during market hours)

## Setup Instructions

### 1. Install Dependencies
```bash
cd btst-strategy
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy the `.env` file and ensure it contains:

```env
# Angel One API
ANGEL_API_KEY=your_api_key
ANGEL_CLIENT_ID=your_client_id
ANGEL_PASSWORD=your_password
ANGEL_TOTP_KEY=your_totp_key

# Telegram - Crypto Channel
TELEGRAM_BOT_TOKEN_CRYPTO=your_crypto_bot_token
TELEGRAM_CHAT_ID_CRYPTO=your_crypto_chat_id

# Telegram - Equity Channel
TELEGRAM_BOT_TOKEN_EQUITY=your_equity_bot_token
TELEGRAM_CHAT_ID_EQUITY=your_equity_chat_id

# Delta Exchange (Optional)
DELTA_API_KEY=your_delta_key
DELTA_API_SECRET=your_delta_secret
```

### 3. Run the Bot
```bash
python bot.py
```

## Configuration

Edit `config.py` to customize:

```python
# Strategy Parameters
BB_PERIOD = 20              # Bollinger Bands period
BB_STD_DEV = 2              # Standard deviation
RSI_PERIOD = 14             # RSI period
VOLUME_MULTIPLIER = 1.5     # Volume threshold
BB_PROXIMITY_THRESHOLD = 0.02  # 2% from band

# Scan Settings
SCAN_INTERVAL_MINUTES = 15  # How often to scan
ALERT_COOLDOWN_MINUTES = 60 # Deduplication window
```

## Alert Format

When a setup is detected, you'll receive a Telegram alert with:

```
🟢 BTST BUY SETUP DETECTED

Symbol: BTCUSD
Timeframe: One Hour
Current Price: 45000.00

📊 Reversal Pattern:
• Candle 1 (Red): Close 44800.00
• Candle 2 (Green): Low 44600.00 → Close 45000.00
• New Low Made: 44600.00 < 44700.00 ✅
• Closed Above: 45000.00 > 44800.00 ✅

✨ Confirmations:
• ✅ Volume: 2.3x avg
• ✅ BB Fake Head detected (punctured lower band)
• ✅ Bullish RSI Divergence detected
• RSI: 42.50

📈 Trade Levels:
• Entry: 45100.00 (break above)
• Stop Loss: 44600.00
• Target 1: 46100.00 (1:2 R/R or 20 SMA)
• Target 2: 46600.00 (1:3 R/R)
• Target 3: 47200.00 (Swing level)

📉 Bollinger Bands:
• Upper: 46500.00
• Middle (20 SMA): 45500.00
• Lower: 44500.00
```

## File Structure

```
btst-strategy/
├── bot.py                  # Main orchestration logic
├── config.py               # Configuration
├── strategy_btst.py        # Core BTST strategy
├── smart_api_helper.py     # Angel One API integration
├── delta_api_helper.py     # Delta Exchange API integration
├── notifier.py             # Telegram notifications
├── token_loader.py         # FNO token loader
├── requirements.txt        # Dependencies
├── .env                    # Environment variables
└── README.md              # This file
```

## How It Works

1. **Initialization**: Bot loads API credentials and initializes helpers
2. **Scanning Loop**: Every 15 minutes (configurable):
   - Fetches historical data for each symbol/timeframe
   - Calculates Bollinger Bands and RSI
   - Checks for two-candle reversal patterns
   - Validates volume, BB Fake Head, RSI divergence
   - Calculates entry/stop/targets
3. **Alerting**: Sends formatted alerts to appropriate Telegram channels
4. **Deduplication**: Prevents spam by tracking recent alerts

## Market Hours

- **Crypto**: 24/7 scanning
- **Equity**: Only during Indian market hours (9:15 AM - 3:30 PM IST, Mon-Fri)

## Deployment

### Local
```bash
python bot.py
```

### Render (Cloud)
1. Create `Procfile`:
   ```
   worker: python bot.py
   ```

2. Deploy to Render as a Background Worker

3. Set environment variables in Render dashboard

## Troubleshooting

### No alerts received
- Check Telegram credentials in `.env`
- Verify bot has permission to send messages to chat
- Check logs for errors

### Insufficient data errors
- Increase `duration_days` in `scan_symbol()` function
- Ensure API credentials are valid

### Angel One login failures
- Verify TOTP key is correct
- Check API key permissions

## Strategy Reference

Based on the BTST (Bollinger Trigger Swing Trade) strategy documented in:
`DOCS/Understanding the Bollinger Trigger Swing Trade (BTST) Strategy.pdf`

## License

MIT
