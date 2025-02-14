import pandas as pd
from ta.trend import SMAIndicator

from .strategy import Strategy


class MaCross(Strategy):
    def __init__(
        self,
        data: pd.DataFrame,
        symbol: str,
        timeframe: str,
        fast_period: int = 10,
        slow_period: int = 20,
    ):
        super().__init__(data, symbol, timeframe)
        self.fast_period = fast_period
        self.slow_period = slow_period

    def generate_signals(self) -> pd.DataFrame:

        # Calculate moving averages
        fast_ma = SMAIndicator(
            close=self.data["close"], window=self.fast_period
        ).sma_indicator()
        slow_ma = SMAIndicator(
            close=self.data["close"], window=self.slow_period
        ).sma_indicator()

        # Generate signals
        signals = pd.DataFrame(index=self.data.index)
        signals["price"] = self.data["close"]
        signals["signal"] = 0

        # Buy signal when fast MA crosses above slow MA
        signals.loc[fast_ma > slow_ma, "signal"] = 1
        # Sell signal when fast MA crosses below slow MA
        signals.loc[fast_ma < slow_ma, "signal"] = -1

        # Calculate profit/loss for each signal
        signals["profit"] = signals["signal"] * signals["price"].pct_change()

        return signals
