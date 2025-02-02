from datetime import datetime
import pandas as pd
import ccxt
from typing import Optional
from .base import Fetcher


class CcxtFetcher(Fetcher):
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

        # Convert dates to timestamps
        since = int(start_date.timestamp() * 1000) if start_date else None

        ohlcv = self.exchange.fetch_ohlcv(
            symbol,
            timeframe,
            since=since,
            limit=1000,  # Adjust based on exchange limits
        )

        # Convert to DataFrame
        return pd.DataFrame(
            ohlcv,
            columns=["timestamp", "open", "high", "low", "close", "volume"],
        )
