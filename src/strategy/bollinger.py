import pandas as pd

from .strategy import Strategy


class Bollinger(Strategy):
    """
    Bollinger Bands trading strategy.
    Generates signals based on price movements relative to the bands:
    - Buy when price crosses below lower band (oversold)
    - Sell when price crosses above upper band (overbought)
    """

    def __init__(
        self,
        data: pd.DataFrame,
        symbol: str,
        timeframe: str,
        period: int = 20,
        num_std: float = 2.0,
    ):
        """
        Initialize the strategy.

        Args:
            symbol: Trading pair symbol
            timeframe: Candle timeframe
            period: Period for moving average calculation
            num_std: Number of standard deviations for bands
        """
        super().__init__(data, symbol, timeframe)
        self.period = period
        self.num_std = num_std

    def generate_signals(self) -> pd.DataFrame:
        """Generate trading signals based on Bollinger Bands."""

        # Calculate Bollinger Bands
        df = self.data.copy()
        df["MA"] = df["close"].rolling(window=self.period).mean()
        df["STD"] = df["close"].rolling(window=self.period).std()
        df["Upper"] = df["MA"] + (df["STD"] * self.num_std)
        df["Lower"] = df["MA"] - (df["STD"] * self.num_std)

        # Generate signals
        # 1 for buy (price crosses below lower band)
        # -1 for sell (price crosses above upper band)
        # 0 for hold
        df["signal"] = 0
        df.loc[df["close"] < df["Lower"], "signal"] = 1
        df.loc[df["close"] > df["Upper"], "signal"] = -1

        # Calculate profits
        df["price"] = df["close"]
        df["profit"] = df["close"].pct_change() * df["signal"].shift(1)

        # Keep only required columns
        return df[["price", "signal", "profit"]]
