from typing_extensions import Literal
import pandas as pd

from src.strategy.bollinger_bands import BollingerBands
from src.strategy.ichimoku import Ichimoku
from src.strategy.ma_cross import MaCross
from src.strategy.macd import Macd
from src.strategy.rsi import Rsi


StrategyType = Literal["bollinger-bands", "ichimoku", "ma-cross", "macd", "rsi"]


class StrategyFactory:
    @staticmethod
    def build(
        strategy: StrategyType,
        data: pd.DataFrame,
        symbol: str,
        timeframe: str,
        # Bollinger Bands
        bollinger_bands_period: int,
        bollinger_bands_std: float,
        # Ichimoku
        ichimoku_tenkan_period: int,
        ichimoku_kijun_period: int,
        ichimoku_senkou_span_b_period: int,
        ichimoku_displacement: int,
        # MA-Cross, MACD
        fast_period: int,
        slow_period: int,
        signal_period: int,
        # RSI
        rsi_period: int,
        rsi_overbought: int,
        rsi_oversold: int,
    ):
        if strategy == "bollinger-bands":
            return BollingerBands(
                data=data,
                symbol=symbol,
                timeframe=timeframe,
                period=bollinger_bands_period,
                num_std=bollinger_bands_std,
            )

        if strategy == "ichimoku":
            return Ichimoku(
                data=data,
                symbol=symbol,
                timeframe=timeframe,
                tenkan_period=ichimoku_tenkan_period,
                kijun_period=ichimoku_kijun_period,
                senkou_span_b_period=ichimoku_senkou_span_b_period,
                displacement=ichimoku_displacement,
            )

        if strategy == "ma-cross":
            return MaCross(
                data=data,
                symbol=symbol,
                timeframe=timeframe,
                fast_period=fast_period,
                slow_period=slow_period,
            )

        if strategy == "macd":
            return Macd(
                data=data,
                symbol=symbol,
                timeframe=timeframe,
                fast_period=fast_period,
                slow_period=slow_period,
                signal_period=signal_period,
            )

        if strategy == "rsi":
            return Rsi(
                data=data,
                symbol=symbol,
                timeframe=timeframe,
                period=rsi_period,
                overbought=rsi_overbought,
                oversold=rsi_oversold,
            )

        # raise ValueError(f"Unknown strategy '{strategy}'.")
