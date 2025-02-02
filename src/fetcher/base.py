from abc import ABC, abstractmethod
from datetime import datetime
import pandas as pd
import ccxt
from typing import Optional
import time
import pickle
from pathlib import Path
from slugify import slugify


class Client(ABC):
    def __init__(self, exchange_id: str = "binance", cache_dir: str = ".cache"):
        # Cache settings
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def fetch_balance(self):
        raise NotImplementedError()

    def fetch_retry(
        self,
        symbol: str,
        timeframe: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        max_retries: int = 3,
        retry_delay: int = 5,
        use_cache: bool = True,
    ) -> pd.DataFrame:
        """Fetch data with retrying and caching support"""

        if use_cache:
            cache_key = self._get_cache_key(symbol, timeframe, start_date, end_date)
            cached_data = self._load_from_cache(cache_key)
            if cached_data is not None:
                return cached_data

        # retry logic
        for attempt in range(max_retries):
            try:
                df = self.fetch_once(symbol, timeframe, start_date, end_date)

                # Convert timestamp to datetime
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
                df.set_index("timestamp", inplace=True)

                # Filter by date range if provided
                if start_date:
                    df = df[df.index >= pd.Timestamp(start_date)]
                if end_date:
                    df = df[df.index <= pd.Timestamp(end_date)]

                if use_cache:
                    cache_key = self._get_cache_key(
                        symbol, timeframe, start_date, end_date
                    )
                    self._save_to_cache(df, cache_key)

                return df

            except (ccxt.NetworkError, ccxt.RequestTimeout) as e:
                if attempt == max_retries - 1:  # Last attempt
                    raise  # Re-raise the last exception

                print(
                    f"Attempt {attempt + 1} failed. Retrying in {retry_delay} seconds..."
                )
                time.sleep(retry_delay)

    @abstractmethod
    def fetch_once(
        self,
        symbol: str,
        timeframe: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """Fetch data"""
        pass

    def _get_cache_key(
        self,
        symbol: str,
        timeframe: str,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
    ) -> str:
        """Generate a unique cache key for the given parameters"""
        keys = [
            symbol,
            timeframe,
            # ! Keeps the cache by hours.
            start_date.strftime("%Y%m%d%H") if start_date else "none",
            end_date.strftime("%Y%m%d%H") if end_date else "none",
        ]
        return slugify("-".join(keys), separator="_")

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get the full path for a cache file"""
        return self.cache_dir / f"{cache_key}.pkl"

    def _save_to_cache(self, df: pd.DataFrame, cache_key: str):
        """Save DataFrame to cache"""
        cache_path = self._get_cache_path(cache_key)
        with open(cache_path, "wb") as f:
            pickle.dump(df, f)
            df.to_csv(self._get_cache_path(cache_key + ".csv"), index=False)

    def _load_from_cache(self, cache_key: str) -> Optional[pd.DataFrame]:
        """Load DataFrame from cache if it exists"""
        cache_path = self._get_cache_path(cache_key)
        if cache_path.exists():
            try:
                with open(cache_path, "rb") as f:
                    return pickle.load(f)
            except (pickle.UnpicklingError, EOFError):
                return None
        return None
