import pandas as pd
from ta.trend import IchimokuIndicator
from .base import Strategy


class IchimokuStrategy(Strategy):
    """
    Tenkan-sen (Conversion Line):
    Default: 9 periods
    Common Range: 7-30 periods
    For more volatile markets: shorter periods (5-15)
    For less volatile markets: longer periods (20-30)

    Kijun-sen (Base Line):
    Default: 26 periods
    Common Range: 20-60 periods
    For more volatile markets: shorter periods (20-40)
    For less volatile markets: longer periods (40-60)

    Senkou Span B (Leading Span B):
    Default: 52 periods
    Common Range: 40-120 periods
    For more volatile markets: shorter periods (40-80)
    For less volatile markets: longer periods (80-120)

    Displacement:
    Default: 26 periods
    Common Range: 20-45 periods

    This is typically set equal to the Kijun-sen period,
    but can be adjusted based on the timeframe.
    """

    def __init__(
        self,
        symbol: str,
        timeframe: str,
        tenkan_period: int = 9,
        kijun_period: int = 26,
        senkou_b_period: int = 52,
        displacement: int = 26,
    ):
        super().__init__(symbol, timeframe)
        self.tenkan_period = tenkan_period
        self.kijun_period = kijun_period
        self.senkou_b_period = senkou_b_period
        self.displacement = displacement

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("No data available. Call set_data() first.")

        # Calculate Ichimoku indicators
        ichimoku = IchimokuIndicator(
            high=self.data["high"],
            low=self.data["low"],
            window1=self.tenkan_period,
            window2=self.kijun_period,
            window3=self.senkou_b_period,
        )

        tenkan_sen = ichimoku.ichimoku_conversion_line()
        kijun_sen = ichimoku.ichimoku_base_line()
        senkou_span_a = ichimoku.ichimoku_a()
        senkou_span_b = ichimoku.ichimoku_b()
        chikou_span = self.data["close"].shift(-self.displacement)

        # Generate signals DataFrame
        signals = pd.DataFrame(index=self.data.index)
        signals["price"] = self.data["close"]
        signals["signal"] = 0

        # Trading Rules:
        # 1. Price above Kumo (Senkou Span A & B)
        # 2. Tenkan-sen crosses above Kijun-sen
        # 3. Chikou Span above price from 26 periods ago

        # Bullish conditions
        bullish = (
            (self.data["close"] > senkou_span_a)  # Price above Kumo
            & (self.data["close"] > senkou_span_b)
            & (tenkan_sen > kijun_sen)  # Tenkan-sen above Kijun-sen
            & (chikou_span > self.data["close"])  # Chikou Span above price
        )

        # Bearish conditions
        bearish = (
            (self.data["close"] < senkou_span_a)  # Price below Kumo
            & (self.data["close"] < senkou_span_b)
            & (tenkan_sen < kijun_sen)  # Tenkan-sen below Kijun-sen
            & (chikou_span < self.data["close"])  # Chikou Span below price
        )

        # Set signals
        signals.loc[bullish, "signal"] = 1
        signals.loc[bearish, "signal"] = -1

        # Calculate profit/loss for each signal
        signals["profit"] = signals["signal"] * signals["price"].pct_change()

        return signals
