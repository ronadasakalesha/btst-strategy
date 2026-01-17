import time
import schedule
from logzero import logger
import config
from datetime import datetime, timedelta
from notifier import TelegramNotifier
from smart_api_helper import SmartApiHelper
from delta_api_helper import DeltaApiHelper
from strategy_btst import BTSTStrategy
from token_loader import load_fno_tokens
import pandas as pd


# Alert tracking to prevent spam
alert_history = {}


def is_angel_market_open():
    """Check if Angel One market is open (9:15 AM - 3:30 PM IST, Mon-Fri)"""
    now = datetime.now()
    
    # Check if weekend
    if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False
    
    # Check market hours (9:15 AM - 3:30 PM)
    market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
    
    return market_open <= now <= market_close


def should_send_alert(symbol, timeframe, setup_type):
    """
    Check if we should send an alert (deduplication)
    Returns True if alert should be sent, False if it's a duplicate
    """
    key = f"{symbol}_{timeframe}_{setup_type}"
    current_time = datetime.now()
    
    if key in alert_history:
        last_alert_time = alert_history[key]
        time_diff = (current_time - last_alert_time).total_seconds() / 60
        
        if time_diff < config.ALERT_COOLDOWN_MINUTES:
            logger.info(f"Skipping duplicate alert for {key} (sent {time_diff:.1f} min ago)")
            return False
    
    # Update alert history
    alert_history[key] = current_time
    return True


def format_alert_message(symbol, timeframe, setup):
    """
    Format rich Telegram alert message
    """
    setup_type = setup['type']
    emoji = "🟢" if setup_type == "BUY" else "🔴"
    
    # Header
    msg = f"{emoji} **BTST {setup_type} SETUP DETECTED**\n\n"
    msg += f"**Symbol**: {symbol}\n"
    msg += f"**Timeframe**: {timeframe.replace('_', ' ').title()}\n"
    msg += f"**Current Price**: {setup['current_price']:.2f}\n\n"
    
    # Reversal Pattern Details
    msg += f"📊 **Reversal Pattern**:\n"
    candle1 = setup['candle1']
    candle2 = setup['reversal_candle']
    
    if setup_type == 'BUY':
        msg += f"• Candle 1 (Red): Close {candle1['close']:.2f}\n"
        msg += f"• Candle 2 (Green): Low {candle2['low']:.2f} → Close {candle2['close']:.2f}\n"
        msg += f"• New Low Made: {candle2['low']:.2f} < {candle1['low']:.2f} ✅\n"
        msg += f"• Closed Above: {candle2['close']:.2f} > {candle1['close']:.2f} ✅\n"
    else:
        msg += f"• Candle 1 (Green): Close {candle1['close']:.2f}\n"
        msg += f"• Candle 2 (Red): High {candle2['high']:.2f} → Close {candle2['close']:.2f}\n"
        msg += f"• New High Made: {candle2['high']:.2f} > {candle1['high']:.2f} ✅\n"
        msg += f"• Closed Below: {candle2['close']:.2f} < {candle1['close']:.2f} ✅\n"
    
    msg += "\n"
    
    # Confirmations
    msg += f"✨ **Confirmations**:\n"
    
    # Volume
    if setup['volume_required']:
        if setup['has_volume']:
            msg += f"• {setup['volume_msg']}\n"
        else:
            msg += f"• ⚠️ {setup['volume_msg']} (REQUIRED)\n"
    else:
        msg += f"• {setup['volume_msg']}\n"
    
    # BB Fake Head
    if setup['has_fake_head']:
        msg += f"• {setup['fake_head_msg']}\n"
    
    # RSI Divergence
    if setup['has_rsi_divergence']:
        msg += f"• {setup['rsi_divergence_msg']}\n"
    
    # RSI Value
    if setup['current_rsi']:
        msg += f"• RSI: {setup['current_rsi']:.2f}\n"
    
    msg += "\n"
    
    # Trade Levels
    msg += f"📈 **Trade Levels**:\n"
    msg += f"• **Entry**: {setup['entry_trigger']:.2f} (break {'above' if setup_type == 'BUY' else 'below'})\n"
    msg += f"• **Stop Loss**: {setup['stop_loss']:.2f}\n"
    msg += f"• **Target 1**: {setup['targets']['target1']:.2f} (1:2 R/R or 20 SMA)\n"
    msg += f"• **Target 2**: {setup['targets']['target2']:.2f} (1:3 R/R)\n"
    msg += f"• **Target 3**: {setup['targets']['target3']:.2f} (Swing level)\n"
    
    msg += "\n"
    
    # Bollinger Bands
    msg += f"📉 **Bollinger Bands**:\n"
    msg += f"• Upper: {setup['bb_upper']:.2f}\n"
    msg += f"• Middle (20 SMA): {setup['bb_middle']:.2f}\n"
    msg += f"• Lower: {setup['bb_lower']:.2f}\n"
    
    # Warning if volume is missing but required
    if setup['volume_required'] and not setup['has_volume']:
        msg += f"\n⚠️ **Note**: This setup lacks required volume confirmation. Trade with caution!"
    
    return msg


def scan_symbol(symbol, identifier, exchange, timeframe, helper, strategy, notifier):
    """
    Scan a single symbol on a specific timeframe
    Returns setup dict if found, None otherwise
    """
    try:
        # Determine duration based on timeframe
        if timeframe == "ONE_DAY":
            duration_days = 60  # Need ~50 candles
        elif timeframe == "ONE_HOUR":
            duration_days = 10
        else:  # FIFTEEN_MINUTE
            duration_days = 5
        
        # Fetch historical data
        if exchange == "DELTA":
            df = helper.get_historical_data(symbol, exchange, timeframe, duration_days)
        else:
            # Angel One
            df = helper.get_historical_data(identifier, exchange, timeframe, duration_days)
        
        if df is None or len(df) < 50:
            logger.warning(f"Insufficient data for {symbol} {timeframe}")
            return None
        
        # Analyze for BTST setup
        setup = strategy.analyze(df, timeframe)
        
        if setup:
            logger.info(f"✅ BTST {setup['type']} setup found: {symbol} {timeframe}")
            
            # Check if we should send alert (deduplication)
            if should_send_alert(symbol, timeframe, setup['type']):
                # Format and send alert
                message = format_alert_message(symbol, timeframe, setup)
                notifier.send_message(message)
                logger.info(f"Alert sent for {symbol} {timeframe}")
            
            return setup
        
        return None
        
    except Exception as e:
        logger.error(f"Error scanning {symbol} {timeframe}: {e}")
        return None


def run_scan():
    """Main scan function - scans all symbols across all timeframes"""
    logger.info("=" * 60)
    logger.info(f"Starting BTST scan at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    # Initialize helpers
    try:
        # Angel One Helper
        angel_helper = SmartApiHelper(
            config.API_KEY,
            config.CLIENT_ID,
            config.PASSWORD,
            config.TOTP_KEY
        )
        
        # Delta Exchange Helper
        delta_helper = DeltaApiHelper(
            config.DELTA_API_KEY,
            config.DELTA_API_SECRET
        )
        
        # Telegram Notifiers
        notifier_crypto = TelegramNotifier(
            config.TELEGRAM_BOT_TOKEN_CRYPTO,
            config.TELEGRAM_CHAT_ID_CRYPTO
        )
        
        notifier_equity = TelegramNotifier(
            config.TELEGRAM_BOT_TOKEN_EQUITY,
            config.TELEGRAM_CHAT_ID_EQUITY
        )
        
        # BTST Strategy
        strategy = BTSTStrategy(
            bb_period=config.BB_PERIOD,
            bb_std_dev=config.BB_STD_DEV,
            rsi_period=config.RSI_PERIOD,
            volume_multiplier=config.VOLUME_MULTIPLIER,
            bb_proximity=config.BB_PROXIMITY_THRESHOLD
        )
        
    except Exception as e:
        logger.error(f"Failed to initialize helpers: {e}")
        return
    
    # Scan Crypto Symbols (Delta Exchange)
    logger.info("Scanning Crypto symbols...")
    for symbol in config.CRYPTO_SYMBOLS:
        for timeframe in config.TIMEFRAMES:
            scan_symbol(
                symbol=symbol,
                identifier=symbol,
                exchange="DELTA",
                timeframe=timeframe,
                helper=delta_helper,
                strategy=strategy,
                notifier=notifier_crypto
            )
            time.sleep(1)  # Rate limiting
    
    
    # Equity scanning disabled - only scanning crypto
    # Uncomment below to enable FNO stock scanning
    
    # # Scan Equity Symbols (Angel One) - only during market hours
    # if is_angel_market_open():
    #     logger.info("Scanning Equity symbols...")
    #     
    #     # Load FNO tokens
    #     try:
    #         equity_symbols = load_fno_tokens()
    #         logger.info(f"Loaded {len(equity_symbols)} equity symbols")
    #     except Exception as e:
    #         logger.error(f"Failed to load equity symbols: {e}")
    #         equity_symbols = []
    #     
    #     for symbol_data in equity_symbols:
    #         symbol = symbol_data['symbol']
    #         token = symbol_data['token']
    #         exchange = symbol_data['exchange']
    #         
    #         for timeframe in config.TIMEFRAMES:
    #             scan_symbol(
    #                 symbol=symbol,
    #                 identifier=token,
    #                 exchange=exchange,
    #                 timeframe=timeframe,
    #                 helper=angel_helper,
    #                 strategy=strategy,
    #                 notifier=notifier_equity
    #             )
    #             time.sleep(1)  # Rate limiting
    # else:
    #     logger.info("Angel One market closed - skipping equity symbols")
    
    logger.info("=" * 60)
    logger.info(f"Scan completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)


def main():
    """Main entry point"""
    logger.info("🚀 BTST Strategy Bot Starting...")
    logger.info(f"Scan interval: {config.SCAN_INTERVAL_MINUTES} minutes")
    logger.info(f"Timeframes: {', '.join(config.TIMEFRAMES)}")
    logger.info(f"Crypto symbols: {', '.join(config.CRYPTO_SYMBOLS)}")
    
    # Run initial scan
    run_scan()
    
    # Schedule periodic scans
    schedule.every(config.SCAN_INTERVAL_MINUTES).minutes.do(run_scan)
    
    logger.info(f"Scheduler started - scanning every {config.SCAN_INTERVAL_MINUTES} minutes")
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
