from datetime import datetime
import pandas as pd
import ccxt
from typing import Optional

from .client import Client


class CcxtClient(Client):
    def __init__(self, exchange_id: str = "binance", cache_dir: str = ".cache"):
        super().__init__(exchange_id, cache_dir)

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

    def fetch_once(
        self,
        symbol: str,
        timeframe: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """Fetch OHLCV data from the exchange"""

        # Convert dates to timestamps in milliseconds
        start_ts = int(start_date.timestamp() * 1000) if start_date else None
        end_ts = int(end_date.timestamp() * 1000) if end_date else None
        # We have a limit of 1000 klines per request
        # Use pagination to fetch all data between startTime and endTime
        klines = []
        limit = 1000
        while True:
            fetched_klines = self.exchange.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                since=start_ts,
                limit=limit,
            )
            klines.extend(fetched_klines)
            if len(fetched_klines) < limit:
                break
            start_ts = fetched_klines[-1][0]

        # Convert to DataFrame
        return pd.DataFrame(
            klines,
            columns=["timestamp", "open", "high", "low", "close", "volume"],
        )
