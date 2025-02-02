from typing import Literal
from datetime import datetime
import pandas as pd
import ccxt
from typing import Optional
from .base import Client


class BinanceClient(Client):
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        market_type: Literal["spot", "futures"] = "futures",
        sandbox_mode: bool = True,
        cache_dir: str = ".cache",
    ):
        super().__init__("binance", cache_dir)

        # Initialize clients
        self.exchange = ccxt.binance(
            {
                "apiKey": api_key,
                "secret": api_secret,
                "options": {"defaultType": market_type},
            }
        )
        if sandbox_mode:
            self.exchange.set_sandbox_mode(True)

    def fetch_balance(self):
        return self.exchange.fetch_balance()

    def fetch_once(
        self,
        symbol: str,
        timeframe: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """Fetch OHLCV data from Binance"""

        # Convert timeframe to Binance format (e.g., '1h' -> '1h', '1d' -> '1d')
        interval = timeframe

        # Convert dates to timestamps in milliseconds
        start_ts = int(start_date.timestamp() * 1000) if start_date else None
        end_ts = int(end_date.timestamp() * 1000) if end_date else None

        # Fetch klines data
        klines = self.client.klines(
            symbol=symbol,
            interval=interval,
            startTime=start_ts,
            endTime=end_ts,
            limit=1000,
        )

        # Convert to DataFrame
        df = pd.DataFrame(
            klines,
            columns=[
                "timestamp",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "close_time",
                "quote_volume",
                "trades",
                "taker_buy_base",
                "taker_buy_quote",
                "ignore",
            ],
        )

        # Keep only the OHLCV columns
        df = df[["timestamp", "open", "high", "low", "close", "volume"]]

        # Convert string values to float
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = df[col].astype(float)

        return df

    def get_latest_price(self, symbol: str) -> float:
        """Get the latest price for a symbol"""
        ticker = self.client.ticker_price(symbol=symbol)
        return float(ticker["price"])

    def get_orderbook(self, symbol: str, limit: int = 100) -> dict:
        """Get the current orderbook for a symbol"""
        return self.client.depth(symbol=symbol, limit=limit)
