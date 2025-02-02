from datetime import datetime
import pandas as pd
import ccxt
from typing import Optional


class DataFetcher:
    def __init__(self, exchange_id: str = "binance"):
        self.exchange = getattr(ccxt, exchange_id)()

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """Fetch OHLCV data from the exchange"""
        # Convert timeframe to milliseconds for the exchange API
        timeframe_ms = self._timeframe_to_ms(timeframe)

        # Convert dates to timestamps
        since = int(start_date.timestamp() * 1000) if start_date else None
        until = int(end_date.timestamp() * 1000) if end_date else None

        # Fetch data
        ohlcv = self.exchange.fetch_ohlcv(
            symbol,
            timeframe,
            since=since,
            limit=1000,  # Adjust based on exchange limits
        )

        # Convert to DataFrame
        df = pd.DataFrame(
            ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"]
        )

        # Convert timestamp to datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)

        # Filter by date range if provided
        if start_date:
            df = df[df.index >= pd.Timestamp(start_date)]
        if end_date:
            df = df[df.index <= pd.Timestamp(end_date)]

        return df

    def _timeframe_to_ms(self, timeframe: str) -> int:
        """Convert timeframe string to milliseconds"""
        units = {
            "m": 60 * 1000,
            "h": 60 * 60 * 1000,
            "d": 24 * 60 * 60 * 1000,
        }
        unit = timeframe[-1]
        value = int(timeframe[:-1])

        return value * units[unit]
