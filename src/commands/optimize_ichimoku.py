import click
from datetime import datetime
from typing import Optional
import itertools
from tqdm import tqdm

from ..fetcher.fetcher import Fetcher
from ..strategy.ichimoku import IchimokuStrategy


@click.command()
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

    # Parameter ranges to test with steps to reduce iterations
    tenkan_periods = range(5, 30 + 2, 2)
    kijun_periods = range(20, 60 + 2, 2)
    senkou_span_b_periods = range(40, 120 + 2, 2)
    displacement_periods = range(20, 45 + 5, 5)

    # Initialize data fetcher
    fetcher = Fetcher()

    # Fetch historical data
    data = fetcher.fetch_ohlcv(
        symbol=symbol, timeframe=timeframe, start_date=start_date, end_date=end_date
    )

    best_profit = float("-inf")
    best_params = None

    total_combinations = (
        len(tenkan_periods)
        * len(kijun_periods)
        * len(senkou_span_b_periods)
        * len(displacement_periods)
    )

    # Create a progress bar
    progress_bar = tqdm(
        total=total_combinations, desc="Testing combinations", unit="combination"
    )

    # Grid search through all parameter combinations
    for tenkan, kijun, senkou_b, disp in itertools.product(
        tenkan_periods, kijun_periods, senkou_span_b_periods, displacement_periods
    ):
        # Skip invalid combinations
        if tenkan >= kijun or kijun >= senkou_b:
            progress_bar.update(1)
            continue

        strategy = IchimokuStrategy(
            symbol=symbol,
            timeframe=timeframe,
            tenkan_period=tenkan,
            kijun_period=kijun,
            senkou_span_b_period=senkou_b,
            displacement=disp,
        )

        strategy.set_data(data)
        strategy.generate_signals()
        metrics = strategy.get_performance_metrics()
        profit = metrics["total_profit"]

        if profit > best_profit:
            best_profit = profit
            best_params = {
                "tenkan_period": tenkan,
                "kijun_period": kijun,
                "senkou_span_b_period": senkou_b,
                "displacement": disp,
                "metrics": metrics,
            }

        progress_bar.update(1)

    progress_bar.close()

    # Print results
    click.echo("\nOptimization complete!")
    click.echo("\nBest parameters found:")
    click.echo(f"Tenkan period: {best_params['tenkan_period']}")
    click.echo(f"Kijun period: {best_params['kijun_period']}")
    click.echo(f"Senkou Span B period: {best_params['senkou_span_b_period']}")
    click.echo(f"Displacement: {best_params['displacement']}")
    click.echo("\nPerformance metrics:")
    click.echo(f"Total profit: {best_params['metrics']['total_profit']:.2%}")
    click.echo(
        f"Profitable / Total trades: {best_params['metrics']['profitable_trades']} / {best_params['metrics']['total_trades']}"
    )
    click.echo(f"Win rate: {best_params['metrics']['win_rate']:.2%}")
    click.echo(f"Max drawdown: {best_params['metrics']['max_drawdown']:.2%}")
