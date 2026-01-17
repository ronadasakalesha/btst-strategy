import pandas as pd
import pandas_ta as ta
from logzero import logger
import numpy as np


class BTSTStrategy:
    """
    BTST (Bollinger Trigger Swing Trade) Strategy
    
    Detects high-probability reversal patterns using:
    - Two-candle reversal patterns
    - Bollinger Bands positioning
    - Volume confirmation (context-dependent)
    - BB "Fake Head" detection
    - Optional RSI divergence
    """
    
    def __init__(self, bb_period=20, bb_std_dev=2, rsi_period=14, 
                 volume_multiplier=1.5, bb_proximity=0.02):
        self.bb_period = bb_period
        self.bb_std_dev = bb_std_dev
        self.rsi_period = rsi_period
        self.volume_multiplier = volume_multiplier
        self.bb_proximity = bb_proximity
    
    def calculate_bollinger_bands(self, df):
        """Calculate Bollinger Bands (20 SMA ± 2 std dev)"""
        if df is None or len(df) < self.bb_period:
            return None
        
        df = df.copy()
        df['bb_middle'] = df['close'].rolling(window=self.bb_period).mean()
        df['bb_std'] = df['close'].rolling(window=self.bb_period).std()
        df['bb_upper'] = df['bb_middle'] + (self.bb_std_dev * df['bb_std'])
        df['bb_lower'] = df['bb_middle'] - (self.bb_std_dev * df['bb_std'])
        
        return df
    
    def calculate_rsi(self, df):
        """Calculate RSI for divergence detection"""
        if df is None or len(df) < self.rsi_period:
            return None
        
        df = df.copy()
        df['rsi'] = ta.rsi(df['close'], length=self.rsi_period)
        return df
    
    def detect_buy_setup(self, df):
        """
        Detect BUY reversal pattern at market bottom:
        - Candle 1: Red candle
        - Candle 2: Green candle that:
          * Makes a new low (low < Candle 1's low)
          * Closes above Candle 1's close
        - Location: Near lower Bollinger Band
        
        NOTE: Only analyzes CLOSED candles (excludes last candle which might be forming)
        
        Returns: (is_valid, setup_data) or (False, None)
        """
        if df is None or len(df) < 3:
            return False, None
        
        # Get last two CLOSED candles (exclude the last one which might be forming)
        candle1 = df.iloc[-3]
        candle2 = df.iloc[-2]
        
        # Check Candle 1: Red candle
        if candle1['close'] >= candle1['open']:
            return False, None
        
        # Check Candle 2: Green candle
        if candle2['close'] <= candle2['open']:
            return False, None
        
        # Check Candle 2 makes new low
        if candle2['low'] >= candle1['low']:
            return False, None
        
        # Check Candle 2 closes above Candle 1's close
        if candle2['close'] <= candle1['close']:
            return False, None
        
        # Check location: Near lower Bollinger Band
        if pd.isna(candle2['bb_lower']):
            return False, None
        
        distance_from_lower = abs(candle2['close'] - candle2['bb_lower']) / candle2['close']
        if distance_from_lower > self.bb_proximity:
            # Not near lower band
            return False, None
        
        # Valid buy setup found
        setup_data = {
            'type': 'BUY',
            'candle1': candle1,
            'candle2': candle2,
            'reversal_candle': candle2,
            'entry_trigger': candle2['high'],
            'stop_loss': candle2['low'],
            'bb_lower': candle2['bb_lower'],
            'bb_middle': candle2['bb_middle'],
            'bb_upper': candle2['bb_upper']
        }
        
        return True, setup_data
    
    def detect_sell_setup(self, df):
        """
        Detect SELL reversal pattern at market top:
        - Candle 1: Green candle
        - Candle 2: Red candle that:
          * Makes a new high (high > Candle 1's high)
          * Closes below Candle 1's close
        - Location: Near upper Bollinger Band
        
        NOTE: Only analyzes CLOSED candles (excludes last candle which might be forming)
        
        Returns: (is_valid, setup_data) or (False, None)
        """
        if df is None or len(df) < 3:
            return False, None
        
        # Get last two CLOSED candles (exclude the last one which might be forming)
        candle1 = df.iloc[-3]
        candle2 = df.iloc[-2]
        
        # Check Candle 1: Green candle
        if candle1['close'] <= candle1['open']:
            return False, None
        
        # Check Candle 2: Red candle
        if candle2['close'] >= candle2['open']:
            return False, None
        
        # Check Candle 2 makes new high
        if candle2['high'] <= candle1['high']:
            return False, None
        
        # Check Candle 2 closes below Candle 1's close
        if candle2['close'] >= candle1['close']:
            return False, None
        
        # Check location: Near upper Bollinger Band
        if pd.isna(candle2['bb_upper']):
            return False, None
        
        distance_from_upper = abs(candle2['close'] - candle2['bb_upper']) / candle2['close']
        if distance_from_upper > self.bb_proximity:
            # Not near upper band
            return False, None
        
        # Valid sell setup found
        setup_data = {
            'type': 'SELL',
            'candle1': candle1,
            'candle2': candle2,
            'reversal_candle': candle2,
            'entry_trigger': candle2['low'],
            'stop_loss': candle2['high'],
            'bb_lower': candle2['bb_lower'],
            'bb_middle': candle2['bb_middle'],
            'bb_upper': candle2['bb_upper']
        }
        
        return True, setup_data
    
    def check_volume_confirmation(self, setup_data, timeframe):
        """
        Check volume confirmation based on context:
        - BUY setups: Volume required on ALL timeframes
        - SELL setups on 1H/1D: Volume optional (bonus)
        - SELL setups on 15M: Volume required
        
        Returns: (has_volume_confirmation, volume_message)
        """
        candle = setup_data['reversal_candle']
        setup_type = setup_data['type']
        
        # Calculate average volume (last 20 candles excluding current)
        # We need the full dataframe for this - will be passed separately
        # For now, return placeholder
        
        # This will be enhanced when we have the full df
        return None, "Volume check pending"
    
    def check_bb_fake_head(self, setup_data):
        """
        Check if reversal candle is a "BB Fake Head":
        - Price temporarily punctures the BB
        - But closes back inside the band
        
        BUY setup: Low < lower BB, but close > lower BB
        SELL setup: High > upper BB, but close < upper BB
        
        Returns: (is_fake_head, message)
        """
        candle = setup_data['reversal_candle']
        setup_type = setup_data['type']
        
        if setup_type == 'BUY':
            # Check if low punctured lower band but closed inside
            if candle['low'] < candle['bb_lower'] and candle['close'] > candle['bb_lower']:
                return True, "✅ BB Fake Head detected (punctured lower band)"
            return False, None
        
        elif setup_type == 'SELL':
            # Check if high punctured upper band but closed inside
            if candle['high'] > candle['bb_upper'] and candle['close'] < candle['bb_upper']:
                return True, "✅ BB Fake Head detected (punctured upper band)"
            return False, None
        
        return False, None
    
    def check_rsi_divergence(self, df, setup_data, lookback=10):
        """
        Check for RSI divergence (optional enhancement):
        - Bullish divergence: Price makes lower low, RSI makes higher low
        - Bearish divergence: Price makes higher high, RSI makes lower high
        
        Returns: (has_divergence, message)
        """
        if df is None or 'rsi' not in df.columns or len(df) < lookback:
            return False, None
        
        setup_type = setup_data['type']
        recent_data = df.tail(lookback)
        
        if setup_type == 'BUY':
            # Look for bullish divergence
            price_lows = recent_data['low'].values
            rsi_values = recent_data['rsi'].values
            
            # Find if we have lower low in price but higher low in RSI
            # Simplified check: compare last low with previous lows
            current_price_low = price_lows[-1]
            current_rsi = rsi_values[-1]
            
            for i in range(len(price_lows) - 2, max(0, len(price_lows) - 6), -1):
                if price_lows[i] > current_price_low and rsi_values[i] < current_rsi:
                    return True, "✅ Bullish RSI Divergence detected"
            
            return False, None
        
        elif setup_type == 'SELL':
            # Look for bearish divergence
            price_highs = recent_data['high'].values
            rsi_values = recent_data['rsi'].values
            
            current_price_high = price_highs[-1]
            current_rsi = rsi_values[-1]
            
            for i in range(len(price_highs) - 2, max(0, len(price_highs) - 6), -1):
                if price_highs[i] < current_price_high and rsi_values[i] > current_rsi:
                    return True, "✅ Bearish RSI Divergence detected"
            
            return False, None
        
        return False, None
    
    def calculate_targets(self, setup_data, df):
        """
        Calculate profit targets:
        - Target 1: 1:2 R/R or middle BB (20 SMA)
        - Target 2: 1:3 R/R
        - Target 3: Nearest swing high/low
        
        Returns: dict with target levels
        """
        setup_type = setup_data['type']
        entry = setup_data['entry_trigger']
        stop = setup_data['stop_loss']
        bb_middle = setup_data['bb_middle']
        
        risk = abs(entry - stop)
        
        if setup_type == 'BUY':
            target1_rr = entry + (2 * risk)
            target1 = min(target1_rr, bb_middle) if bb_middle > entry else target1_rr
            target2 = entry + (3 * risk)
            
            # Find nearest swing high (simplified: highest high in last 20 candles)
            if df is not None and len(df) >= 20:
                swing_high = df.tail(20)['high'].max()
                target3 = swing_high if swing_high > entry else target2
            else:
                target3 = target2
        
        else:  # SELL
            target1_rr = entry - (2 * risk)
            target1 = max(target1_rr, bb_middle) if bb_middle < entry else target1_rr
            target2 = entry - (3 * risk)
            
            # Find nearest swing low (simplified: lowest low in last 20 candles)
            if df is not None and len(df) >= 20:
                swing_low = df.tail(20)['low'].min()
                target3 = swing_low if swing_low < entry else target2
            else:
                target3 = target2
        
        return {
            'target1': target1,
            'target2': target2,
            'target3': target3,
            'risk_reward_1': 2.0,
            'risk_reward_2': 3.0
        }
    
    def analyze(self, df, timeframe):
        """
        Main analysis function - checks for BTST setups
        
        Returns: dict with setup details or None
        """
        if df is None or len(df) < max(self.bb_period, 50):
            logger.warning(f"Insufficient data for BTST analysis (need {max(self.bb_period, 50)} candles)")
            return None
        
        # Calculate indicators
        df = self.calculate_bollinger_bands(df)
        df = self.calculate_rsi(df)
        
        if df is None:
            return None
        
        # Check for buy setup
        is_buy, buy_setup = self.detect_buy_setup(df)
        if is_buy:
            setup = buy_setup
        else:
            # Check for sell setup
            is_sell, sell_setup = self.detect_sell_setup(df)
            if is_sell:
                setup = sell_setup
            else:
                return None
        
        # Setup found - add confirmations
        setup['timeframe'] = timeframe
        
        # Check BB Fake Head
        has_fake_head, fake_head_msg = self.check_bb_fake_head(setup)
        setup['has_fake_head'] = has_fake_head
        setup['fake_head_msg'] = fake_head_msg
        
        # Check RSI Divergence
        has_divergence, divergence_msg = self.check_rsi_divergence(df, setup)
        setup['has_rsi_divergence'] = has_divergence
        setup['rsi_divergence_msg'] = divergence_msg
        
        # Check Volume (enhanced version - calculate avg volume)
        # Exclude last candle (forming) and the reversal candle from average calculation
        recent_volumes = df.tail(22)['volume'].iloc[:-2]  # Last 20 excluding reversal and forming candles
        avg_volume = recent_volumes.mean()
        current_volume = setup['reversal_candle']['volume']
        
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
        has_volume = volume_ratio >= self.volume_multiplier
        
        # Apply context-dependent volume rules
        setup_type = setup['type']
        if setup_type == 'BUY':
            # Volume required on all timeframes
            setup['volume_required'] = True
            setup['has_volume'] = has_volume
            setup['volume_msg'] = f"✅ Volume: {volume_ratio:.2f}x avg" if has_volume else f"⚠️ Low Volume: {volume_ratio:.2f}x avg"
        elif setup_type == 'SELL':
            if timeframe == 'FIFTEEN_MINUTE':
                # Volume required for 15M sell setups
                setup['volume_required'] = True
                setup['has_volume'] = has_volume
                setup['volume_msg'] = f"✅ Volume: {volume_ratio:.2f}x avg" if has_volume else f"⚠️ Low Volume: {volume_ratio:.2f}x avg"
            else:
                # Volume optional for 1H/1D sell setups
                setup['volume_required'] = False
                setup['has_volume'] = has_volume
                setup['volume_msg'] = f"✅ Bonus: High Volume ({volume_ratio:.2f}x avg)" if has_volume else f"⚪ Volume: {volume_ratio:.2f}x avg (optional)"
        
        # Calculate targets
        targets = self.calculate_targets(setup, df)
        setup['targets'] = targets
        
        # Add current price info (from last CLOSED candle, not forming candle)
        setup['current_price'] = df.iloc[-2]['close']
        setup['current_rsi'] = df.iloc[-2]['rsi'] if 'rsi' in df.columns else None
        
        return setup
