from typing_extensions import Literal
import pandas as pd

from src.strategy.bollinger import Bollinger
from src.strategy.ichimoku import Ichimoku
from src.strategy.ma_cross import MaCross
from src.strategy.macd import Macd
from src.strategy.rsi import Rsi


StrategyType = Literal["bb", "ichimoku", "ma-cross", "macd", "rsi"]


class StrategyFactory:
    @staticmethod
    def build(
        strategy: StrategyType,
        data: pd.DataFrame,
        symbol: str,
        timeframe: str,
        # bb
        bb_period: int,
        bb_std: float,
        # ma-cross, macd
        fast_period: int,
        slow_period: int,
        signal_period: int,
        # rsi
        rsi_period: int,
        rsi_overbought: int,
        rsi_oversold: int,
        # ichimoku
        tenkan_period: int,
        kijun_period: int,
        senkou_span_b_period: int,
        displacement: int,
    ):
        if strategy == "bb":
            return Bollinger(
                data=data,
                symbol=symbol,
                timeframe=timeframe,
                period=bb_period,
                num_std=bb_std,
            )

        if strategy == "ichimoku":
            return Ichimoku(
                data=data,
                symbol=symbol,
                timeframe=timeframe,
                tenkan_period=tenkan_period,
                kijun_period=kijun_period,
                senkou_span_b_period=senkou_span_b_period,
                displacement=displacement,
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
