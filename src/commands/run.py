import click
from datetime import datetime
from typing import Optional

from ..fetcher.fetcher import Fetcher
from ..strategy.bollinger import BollingerBandsStrategy
from ..strategy.ma_cross import MovingAverageCrossStrategy
from ..strategy.rsi import RSIStrategy
from ..strategy.macd import MACDStrategy
from ..strategy.ichimoku import IchimokuStrategy


@click.command()
@click.option(
    "--strategy",
    type=click.Choice(["bb", "ma-cross", "rsi", "macd", "ichimoku"]),
    required=True,
    help="Trading strategy to test",
)
@click.option("--symbol", required=True, help="Trading pair (e.g., BTC/USDT)")
@click.option(
    "--timeframe", required=True, help="Candle timeframe (1m, 5m, 15m, 1h, 4h, 1d)"
)
@click.option(
    "--start-date",
    type=click.DateTime(),
    help="Start date for backtesting (YYYY-MM-DD)",
)
@click.option(
    "--end-date", type=click.DateTime(), help="End date for backtesting (YYYY-MM-DD)"
)
# Bollinger Bands specific options
@click.option("--bb-period", type=int, default=20, help="Bollinger Bands period")
@click.option("--bb-std", type=float, default=2.0, help="Number of standard deviations")
# MA Crossover and MACD specific options
@click.option(
    "--fast-period", type=int, default=12, help="Fast EMA period for MACD/MA-Cross"
)
@click.option(
    "--slow-period", type=int, default=26, help="Slow EMA period for MACD/MA-Cross"
)
@click.option(
    "--signal-period", type=int, default=9, help="Signal line period for MACD"
)
# RSI specific options
@click.option("--rsi-period", type=int, default=14, help="RSI calculation period")
@click.option(
    "--rsi-overbought", type=float, default=70, help="RSI overbought threshold"
)
@click.option("--rsi-oversold", type=float, default=30, help="RSI oversold threshold")
# Ichimoku specific options
@click.option("--tenkan-period", type=int, default=9, help="Tenkan-sen period")
@click.option("--kijun-period", type=int, default=26, help="Kijun-sen period")
@click.option(
    "--senkou-span-b-period", type=int, default=52, help="Senkou Span B period"
)
@click.option("--displacement", type=int, default=26, help="Displacement period")
def run(
    strategy: str,
    symbol: str,
    timeframe: str,
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    bb_period: int,
    bb_std: float,
    fast_period: int,
    slow_period: int,
    signal_period: int,
    rsi_period: int,
    rsi_overbought: float,
    rsi_oversold: float,
    tenkan_period: int,
    kijun_period: int,
    senkou_span_b_period: int,
    displacement: int,
):
    """Test a trading strategy with historical data"""
    # Initialize data fetcher
    fetcher = Fetcher()

    # Fetch historical data
    data = fetcher.fetch_ohlcv(
        symbol=symbol, timeframe=timeframe, start_date=start_date, end_date=end_date
    )

    # Initialize strategy
    if strategy == "bb":
        s = BollingerBandsStrategy(
            symbol=symbol,
            timeframe=timeframe,
            period=bb_period,
            num_std=bb_std,
        )
    elif strategy == "ichimoku":
        s = IchimokuStrategy(
            symbol=symbol,
            timeframe=timeframe,
            tenkan_period=tenkan_period,
            kijun_period=kijun_period,
            senkou_span_b_period=senkou_span_b_period,
            displacement=displacement,
        )
    elif strategy == "ma-cross":
        s = MovingAverageCrossStrategy(
            symbol=symbol,
            timeframe=timeframe,
            fast_period=fast_period,
            slow_period=slow_period,
        )
    elif strategy == "macd":
        s = MACDStrategy(
            symbol=symbol,
            timeframe=timeframe,
            fast_period=fast_period,
            slow_period=slow_period,
            signal_period=signal_period,
        )
    else:
        s = RSIStrategy(
            symbol=symbol,
            timeframe=timeframe,
            period=rsi_period,
            overbought=rsi_overbought,
            oversold=rsi_oversold,
        )

    # Set data and generate signals
    s.set_data(data)
    signals = s.generate_signals()
    metrics = s.get_performance_metrics()

    # Print results
    click.echo(f"\nStrategy: {strategy.upper()}")
    click.echo(f"Symbol: {symbol}")
    click.echo(f"Timeframe: {timeframe}")
    click.echo(f"\nSignals:\n{signals}")
    click.echo("\nPerformance metrics:")
    click.echo(f"Total profit: {metrics['total_profit']:.2%}")
    click.echo(
        f"Profitable / Total trades: {metrics['profitable_trades']} / {metrics['total_trades']}"
    )
    click.echo(f"Win rate: {metrics['win_rate']:.2%}")
    click.echo(f"Max drawdown: {metrics['max_drawdown']:.2%}")
