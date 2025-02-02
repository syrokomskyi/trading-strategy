from datetime import datetime
import pandas as pd
import ccxt
from typing import Optional
import time


class DataFetcher:
    def __init__(self, exchange_id: str = "binance"):
        self.exchange = getattr(ccxt, exchange_id)()
        # Increase timeout values
        self.exchange.timeout = 30000  # 30 seconds
        self.exchange.enableRateLimit = True

        # Configure exchange-specific options
        if exchange_id == "binance":
            self.exchange.options.update(
                {
                    "adjustForTimeDifference": True,
                    "recvWindow": 60000,
                    "defaultType": "future",  # Since we're using dapi
                    "defaultNetwork": "BSC",
                }
            )

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        max_retries: int = 3,
        retry_delay: int = 5,
    ) -> pd.DataFrame:
        """Fetch OHLCV data from the exchange"""
        # Convert timeframe to milliseconds for the exchange API
        timeframe_ms = self._timeframe_to_ms(timeframe)

        # Convert dates to timestamps
        since = int(start_date.timestamp() * 1000) if start_date else None
        until = int(end_date.timestamp() * 1000) if end_date else None

        # Add retry logic
        for attempt in range(max_retries):
            try:
                # Fetch data
                ohlcv = self.exchange.fetch_ohlcv(
                    symbol,
                    timeframe,
                    since=since,
                    limit=1000,  # Adjust based on exchange limits
                )

                # Convert to DataFrame
                df = pd.DataFrame(
                    ohlcv,
                    columns=["timestamp", "open", "high", "low", "close", "volume"],
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

            except (ccxt.NetworkError, ccxt.RequestTimeout) as e:
                if attempt == max_retries - 1:  # Last attempt
                    raise  # Re-raise the last exception
                print(
                    f"Attempt {attempt + 1} failed. Retrying in {retry_delay} seconds..."
                )
                time.sleep(retry_delay)

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
