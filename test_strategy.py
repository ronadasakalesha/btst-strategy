"""
Test script for BTST Strategy
Tests the strategy logic with sample data
"""

import pandas as pd
import numpy as np
from strategy_btst import BTSTStrategy
from datetime import datetime, timedelta


def create_sample_buy_setup():
    """Create sample data with a valid buy setup"""
    dates = pd.date_range(end=datetime.now(), periods=50, freq='1H')
    
    # Create downtrend with reversal
    prices = []
    base_price = 100
    
    # Downtrend
    for i in range(48):
        prices.append(base_price - (i * 0.5))
    
    # Create reversal pattern
    # Candle 1 (Red): O:52, H:53, L:51, C:51.5
    # Candle 2 (Green): O:51.5, H:52.5, L:50.5, C:52.2
    
    data = []
    for i in range(48):
        price = prices[i]
        data.append({
            'date': dates[i],
            'open': price + np.random.uniform(-0.5, 0.5),
            'high': price + np.random.uniform(0, 1),
            'low': price - np.random.uniform(0, 1),
            'close': price + np.random.uniform(-0.3, 0.3),
            'volume': np.random.uniform(1000, 2000)
        })
    
    # Candle 1 (Red)
    data.append({
        'date': dates[48],
        'open': 52.0,
        'high': 53.0,
        'low': 51.0,
        'close': 51.5,
        'volume': 1500
    })
    
    # Candle 2 (Green) - makes new low, closes above
    data.append({
        'date': dates[49],
        'open': 51.5,
        'high': 52.5,
        'low': 50.5,  # New low
        'close': 52.2,  # Closes above candle 1
        'volume': 3000  # High volume
    })
    
    df = pd.DataFrame(data)
    return df


def create_sample_sell_setup():
    """Create sample data with a valid sell setup"""
    dates = pd.date_range(end=datetime.now(), periods=50, freq='1H')
    
    # Create uptrend with reversal
    prices = []
    base_price = 50
    
    # Uptrend
    for i in range(48):
        prices.append(base_price + (i * 0.5))
    
    data = []
    for i in range(48):
        price = prices[i]
        data.append({
            'date': dates[i],
            'open': price + np.random.uniform(-0.5, 0.5),
            'high': price + np.random.uniform(0, 1),
            'low': price - np.random.uniform(0, 1),
            'close': price + np.random.uniform(-0.3, 0.3),
            'volume': np.random.uniform(1000, 2000)
        })
    
    # Candle 1 (Green)
    data.append({
        'date': dates[48],
        'open': 73.0,
        'high': 74.0,
        'low': 72.5,
        'close': 73.8,
        'volume': 1500
    })
    
    # Candle 2 (Red) - makes new high, closes below
    data.append({
        'date': dates[49],
        'open': 73.8,
        'high': 74.5,  # New high
        'low': 73.0,
        'close': 73.2,  # Closes below candle 1
        'volume': 3000  # High volume
    })
    
    df = pd.DataFrame(data)
    return df


def test_bollinger_bands():
    """Test Bollinger Bands calculation"""
    print("\n" + "="*60)
    print("TEST 1: Bollinger Bands Calculation")
    print("="*60)
    
    strategy = BTSTStrategy()
    df = create_sample_buy_setup()
    
    df_with_bb = strategy.calculate_bollinger_bands(df)
    
    if df_with_bb is not None and 'bb_upper' in df_with_bb.columns:
        last_row = df_with_bb.iloc[-1]
        print(f"✅ Bollinger Bands calculated successfully")
        print(f"   Upper Band: {last_row['bb_upper']:.2f}")
        print(f"   Middle Band (20 SMA): {last_row['bb_middle']:.2f}")
        print(f"   Lower Band: {last_row['bb_lower']:.2f}")
        print(f"   Current Price: {last_row['close']:.2f}")
        return True
    else:
        print("❌ Bollinger Bands calculation failed")
        return False


def test_buy_setup_detection():
    """Test buy setup detection"""
    print("\n" + "="*60)
    print("TEST 2: Buy Setup Detection")
    print("="*60)
    
    strategy = BTSTStrategy()
    df = create_sample_buy_setup()
    
    # Calculate BB first
    df = strategy.calculate_bollinger_bands(df)
    
    is_valid, setup = strategy.detect_buy_setup(df)
    
    if is_valid:
        print(f"✅ Buy setup detected successfully")
        print(f"   Candle 1 (Red): Close {setup['candle1']['close']:.2f}")
        print(f"   Candle 2 (Green): Low {setup['candle2']['low']:.2f}, Close {setup['candle2']['close']:.2f}")
        print(f"   Entry Trigger: {setup['entry_trigger']:.2f}")
        print(f"   Stop Loss: {setup['stop_loss']:.2f}")
        return True
    else:
        print("❌ Buy setup detection failed")
        print("   Expected: Valid buy setup")
        print("   Got: No setup detected")
        return False


def test_sell_setup_detection():
    """Test sell setup detection"""
    print("\n" + "="*60)
    print("TEST 3: Sell Setup Detection")
    print("="*60)
    
    strategy = BTSTStrategy()
    df = create_sample_sell_setup()
    
    # Calculate BB first
    df = strategy.calculate_bollinger_bands(df)
    
    is_valid, setup = strategy.detect_sell_setup(df)
    
    if is_valid:
        print(f"✅ Sell setup detected successfully")
        print(f"   Candle 1 (Green): Close {setup['candle1']['close']:.2f}")
        print(f"   Candle 2 (Red): High {setup['candle2']['high']:.2f}, Close {setup['candle2']['close']:.2f}")
        print(f"   Entry Trigger: {setup['entry_trigger']:.2f}")
        print(f"   Stop Loss: {setup['stop_loss']:.2f}")
        return True
    else:
        print("❌ Sell setup detection failed")
        print("   Expected: Valid sell setup")
        print("   Got: No setup detected")
        return False


def test_full_analysis():
    """Test full analysis with all confirmations"""
    print("\n" + "="*60)
    print("TEST 4: Full Analysis (Buy Setup)")
    print("="*60)
    
    strategy = BTSTStrategy()
    df = create_sample_buy_setup()
    
    setup = strategy.analyze(df, "ONE_HOUR")
    
    if setup:
        print(f"✅ Full analysis completed successfully")
        print(f"\n   Setup Type: {setup['type']}")
        print(f"   Timeframe: {setup['timeframe']}")
        print(f"   Entry: {setup['entry_trigger']:.2f}")
        print(f"   Stop: {setup['stop_loss']:.2f}")
        print(f"   Target 1: {setup['targets']['target1']:.2f}")
        print(f"   Target 2: {setup['targets']['target2']:.2f}")
        print(f"   Target 3: {setup['targets']['target3']:.2f}")
        print(f"\n   Confirmations:")
        print(f"   - Volume: {setup['volume_msg']}")
        print(f"   - BB Fake Head: {'Yes' if setup['has_fake_head'] else 'No'}")
        print(f"   - RSI Divergence: {'Yes' if setup['has_rsi_divergence'] else 'No'}")
        return True
    else:
        print("❌ Full analysis failed")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("BTST STRATEGY TEST SUITE")
    print("="*70)
    
    results = []
    
    results.append(("Bollinger Bands Calculation", test_bollinger_bands()))
    results.append(("Buy Setup Detection", test_buy_setup_detection()))
    results.append(("Sell Setup Detection", test_sell_setup_detection()))
    results.append(("Full Analysis", test_full_analysis()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Strategy logic is working correctly.")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please review the output above.")


if __name__ == "__main__":
    run_all_tests()
