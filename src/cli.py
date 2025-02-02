import click
from datetime import datetime
from typing import Optional

from .data.fetcher import DataFetcher

from .strategy.bollinger import BollingerBandsStrategy
from .strategy.ma_cross import MovingAverageCrossStrategy
from .strategy.rsi import RSIStrategy
from .strategy.macd import MACDStrategy
from .strategy.ichimoku import IchimokuStrategy


@click.group()
def cli():
    """Crypto Trading Strategy Tester CLI"""
    pass


@cli.command()
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
    fetcher = DataFetcher()

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
    elif strategy == "ichimoku":
        s = IchimokuStrategy(
            symbol=symbol,
            timeframe=timeframe,
            tenkan_period=tenkan_period,
            kijun_period=kijun_period,
            senkou_span_b_period=senkou_span_b_period,
            displacement=displacement,
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


@cli.command()
@click.option("--symbol", required=True, help="Trading pair (e.g., BTC/USDT)")
@click.option(
    "--timeframe", required=True, help="Candle timeframe (1m, 5m, 15m, 1h, 4h, 1d)"
)
@click.option(
    "--start-date",
    type=click.DateTime(),
    help="Start date for optimization (YYYY-MM-DD)",
)
@click.option(
    "--end-date", type=click.DateTime(), help="End date for optimization (YYYY-MM-DD)"
)
def optimize_ichimoku(
    symbol: str,
    timeframe: str,
    start_date: Optional[datetime],
    end_date: Optional[datetime],
):
    """Optimize Ichimoku Strategy parameters using grid search."""
    click.echo("Starting Ichimoku Strategy optimization...")

    # Parameter ranges to test
    tenkan_periods = range(7, 12)  # Default is 9
    kijun_periods = range(22, 30)  # Default is 26
    senkou_span_b_periods = range(48, 56)  # Default is 52

    # Initialize data fetcher
    fetcher = DataFetcher()

    # Fetch historical data
    data = fetcher.fetch_ohlcv(
        symbol=symbol, timeframe=timeframe, start_date=start_date, end_date=end_date
    )

    best_profit = float("-inf")
    best_params = None

    total_combinations = (
        len(tenkan_periods) * len(kijun_periods) * len(senkou_span_b_periods)
    )
    with click.progressbar(
        length=total_combinations, label="Testing combinations"
    ) as bar:
        # Grid search through parameter combinations
        for tenkan in tenkan_periods:
            for kijun in kijun_periods:
                for senkou_span_b in senkou_span_b_periods:
                    # Skip invalid combinations where periods overlap incorrectly
                    if tenkan >= kijun or kijun >= senkou_span_b:
                        bar.update(1)
                        continue

                    # Create and test strategy with current parameters
                    strategy = IchimokuStrategy(
                        symbol=symbol,
                        timeframe=timeframe,
                        tenkan_period=tenkan,
                        kijun_period=kijun,
                        senkou_span_b_period=senkou_span_b,
                    )
                    strategy.set_data(data)

                    # Generate signals and calculate total profit
                    signals = strategy.generate_signals()
                    total_profit = signals["profit"].sum()

                    # Update best parameters if current combination is better
                    if total_profit > best_profit:
                        best_profit = total_profit
                        best_params = {
                            "tenkan_period": tenkan,
                            "kijun_period": kijun,
                            "senkou_span_b_period": senkou_span_b,
                        }

                    bar.update(1)

    click.echo("\nOptimization complete!")
    click.echo("\nBest parameters found:")
    click.echo(f"Tenkan period: {best_params['tenkan_period']}")
    click.echo(f"Kijun period: {best_params['kijun_period']}")
    click.echo(f"Senkou Span B period: {best_params['senkou_span_b_period']}")
    click.echo(f"Total profit: {best_profit:.4f}")


def main():
    cli()


if __name__ == "__main__":
    main()
