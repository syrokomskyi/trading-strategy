import click
from datetime import datetime
from typing import Optional

from ..fetcher.ccxt import CcxtFetcher
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

    # Fetch historical data
    fetcher = CcxtFetcher()
    data = fetcher.fetch_retry(
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
    with click.progressbar(
        length=total_combinations, label="Testing combinations"
    ) as bar:
        # Grid search through parameter combinations
        for tenkan in tenkan_periods:
            for kijun in kijun_periods:
                for senkou_span_b in senkou_span_b_periods:
                    for displacement in displacement_periods:
                        # Skip invalid combinations where periods overlap incorrectly
                        if (
                            tenkan >= kijun
                            or kijun >= senkou_span_b
                            or tenkan < 5  # Too small for meaningful averages
                            or kijun
                            < 2 * tenkan  # Kijun should be notably larger than Tenkan
                            or senkou_span_b
                            < 2 * kijun  # Senkou B should be notably larger than Kijun
                            or displacement
                            < kijun * 0.5  # Displacement shouldn't be too small
                            or displacement > kijun * 1.5
                        ):  # or too large relative to Kijun
                            bar.update(1)
                            continue

                        # Create and test strategy with current parameters
                        strategy = IchimokuStrategy(
                            data=data,
                            symbol=symbol,
                            timeframe=timeframe,
                            tenkan_period=tenkan,
                            kijun_period=kijun,
                            senkou_span_b_period=senkou_span_b,
                            displacement=displacement,
                        )

                        metrics = strategy.get_performance_metrics()
                        total_profit = metrics["total_profit"]

                        # Update best parameters if current combination is better
                        if total_profit > best_profit:
                            best_profit = total_profit
                            best_params = {
                                "tenkan_period": tenkan,
                                "kijun_period": kijun,
                                "senkou_span_b_period": senkou_span_b,
                                "displacement": displacement,
                            }

                        bar.update(1)

    click.echo("\nOptimization complete!")

    click.echo(f"\nTotal profit: {best_profit:.2%}")

    click.echo("\nBest parameters found:")
    click.echo(f"Tenkan period: {best_params['tenkan_period']}")
    click.echo(f"Kijun period: {best_params['kijun_period']}")
    click.echo(f"Senkou Span B period: {best_params['senkou_span_b_period']}")
    click.echo(f"Displacement: {best_params['displacement']}")
