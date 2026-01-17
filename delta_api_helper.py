
import requests
import pandas as pd
from datetime import datetime, timedelta
from logzero import logger


class DeltaApiHelper:
    def __init__(self, api_key=None, api_secret=None):
        self.base_url = "https://api.india.delta.exchange"
        self.api_key = api_key
        self.api_secret = api_secret

    def get_timeframe_code(self, timeframe):
        """Map bot timeframes to Delta resolution codes"""
        mapping = {
            "ONE_HOUR": "1h",
            "FIFTEEN_MINUTE": "15m",
            "FIVE_MINUTE": "5m",
            "ONE_DAY": "1d"
        }
        return mapping.get(timeframe, "5m")

    def get_historical_data(self, symbol, exchange="DELTA", timeframe="FIVE_MINUTE", duration_days=5):
        """
        Fetches historical candle data from Delta Exchange India.
        Returns DataFrame with columns: date, open, high, low, close, volume
        """
        resolution = self.get_timeframe_code(timeframe)
        
        # Calculate start/end timestamps
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=duration_days)
        
        start_ts = int(start_dt.timestamp())
        end_ts = int(end_dt.timestamp())
        
        url = f"{self.base_url}/v2/history/candles"
        params = {
            "resolution": resolution,
            "symbol": symbol,  # e.g., BTCUSD, ETHUSD
            "start": start_ts,
            "end": end_ts
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"Delta API Error ({symbol}): Status {response.status_code} - {response.text}")
                return None
                
            data = response.json()
            if "result" not in data or not data["result"]:
                logger.warning(f"No result data for {symbol} {timeframe}")
                return None
            
            candles = data["result"]
            
            # Delta returns: [timestamp, open, high, low, close, volume]
            df = pd.DataFrame(candles, columns=["time", "open", "high", "low", "close", "volume"])
            
            # Convert timestamp to datetime
            df['date'] = pd.to_datetime(df['time'], unit='s')
            
            # Sort ascending (oldest first) for indicator calculation
            df = df.sort_values('date').reset_index(drop=True)
            
            # Ensure numeric types
            cols = ['open', 'high', 'low', 'close', 'volume']
            df[cols] = df[cols].apply(pd.to_numeric)
            
            logger.info(f"Fetched {len(df)} candles for {symbol} {timeframe}")
            
            return df[['date', 'open', 'high', 'low', 'close', 'volume']]
            
        except Exception as e:
            logger.error(f"Delta Fetch Exception ({symbol} {timeframe}): {e}")
            return None
