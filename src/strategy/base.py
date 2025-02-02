from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
import pandas as pd


class Strategy(ABC):
    def __init__(self, symbol: str, timeframe: str):
        self.symbol = symbol
        self.timeframe = timeframe
        self.data: Optional[pd.DataFrame] = None

    @abstractmethod
    def generate_signals(self) -> pd.DataFrame:
        """Generate buy/sell signals based on the strategy logic"""
        pass

    def set_data(self, data: pd.DataFrame):
        """Set the price data for analysis"""
        self.data = data

    def get_performance_metrics(self) -> Dict[str, float]:
        """Calculate strategy performance metrics"""
        if self.data is None:
            raise ValueError("No data available. Call set_data() first.")

        signals = self.generate_signals()

        # Calculate basic metrics
        total_trades = len(signals[signals["signal"] != 0])
        profitable_trades = len(signals[signals["profit"] > 0])
        win_rate = profitable_trades / total_trades if total_trades > 0 else 0
        total_profit = signals["profit"].sum()
        max_drawdown = self._calculate_max_drawdown(signals)

        return {
            "total_trades": total_trades,
            "profitable_trades": profitable_trades,
            "win_rate": win_rate,
            "total_profit": total_profit,
            "max_drawdown": max_drawdown,
        }

    def _calculate_max_drawdown(self, signals: pd.DataFrame) -> float:
        """Calculate maximum drawdown from equity curve"""
        cumulative = (1 + signals["profit"]).cumprod()
        rolling_max = cumulative.expanding().max()
        drawdowns = cumulative / rolling_max - 1
        return abs(drawdowns.min())
