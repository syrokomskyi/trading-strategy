import pandas as pd
from ta.trend import MACD
from .base import Strategy


class MACDStrategy(Strategy):
    def __init__(
        self,
        data: pd.DataFrame,
        symbol: str,
        timeframe: str,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ):
        super().__init__(data, symbol, timeframe)
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

    def generate_signals(self) -> pd.DataFrame:

        # Calculate MACD
        macd_indicator = MACD(
            close=self.data["close"],
            window_slow=self.slow_period,
            window_fast=self.fast_period,
            window_sign=self.signal_period,
        )
        macd_line = macd_indicator.macd()
        signal_line = macd_indicator.macd_signal()

        # Generate signals
        signals = pd.DataFrame(index=self.data.index)
        signals["price"] = self.data["close"]
        signals["signal"] = 0

        # Buy signal when MACD line crosses above signal line
        signals.loc[
            (macd_line > signal_line) & (macd_line.shift(1) <= signal_line.shift(1)),
            "signal",
        ] = 1

        # Sell signal when MACD line crosses below signal line
        signals.loc[
            (macd_line < signal_line) & (macd_line.shift(1) >= signal_line.shift(1)),
            "signal",
        ] = -1

        # Calculate profit/loss for each signal
        signals["profit"] = signals["signal"] * signals["price"].pct_change()

        return signals
