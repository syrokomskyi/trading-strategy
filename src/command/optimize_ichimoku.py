import click
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from concurrent.futures import ProcessPoolExecutor
import itertools
from tqdm import tqdm

from ..client.ccxt import CcxtClient
from ..strategy.ichimoku import Ichimoku


def test_parameter_combination(
    args: Tuple[Dict[str, Any], Dict[str, Any]]
) -> Tuple[float, Dict[str, int]]:
    """Worker function to test a single parameter combination."""
    params, setup = args
    tenkan = params["tenkan"]
    kijun = params["kijun"]
    senkou_span_b = params["senkou_span_b"]
    ichimoku_displacement = params["ichimoku_displacement"]

    # Skip invalid combinations where periods overlap incorrectly
    if (
        tenkan >= kijun
        or kijun >= senkou_span_b
        or tenkan < 5  # Too small for meaningful averages
        or kijun < 2 * tenkan  # Kijun should be notably larger than Tenkan
        or senkou_span_b < 2 * kijun  # Senkou B should be notably larger than Kijun
        or ichimoku_displacement
        < kijun * 0.5  # ichimoku_displacement shouldn't be too small
        or ichimoku_displacement > kijun * 1.5  # or too large relative to Kijun
    ):
        return float("-inf"), params

    # Create and test strategy with current parameters
    strategy = Ichimoku(
        data=setup["data"],
        symbol=setup["symbol"],
        timeframe=setup["timeframe"],
        tenkan_period=tenkan,
        kijun_period=kijun,
        senkou_span_b_period=senkou_span_b,
        displacement=ichimoku_displacement,
    )

    metrics = strategy.get_performance_metrics()

    return metrics["total_profit"], params


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
@click.option(
    "--workers",
    type=int,
    default=None,
    help="Number of worker processes (defaults to CPU count)",
)
def optimize_ichimoku(
    symbol: str,
    timeframe: str,
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    workers: Optional[int],
):
    """Optimize Ichimoku Strategy parameters using parallel grid search."""
    click.echo("Starting Ichimoku Strategy optimization...")

    # Parameter ranges to test with steps to reduce iterations
    ichimoku_tenkan_periods = range(5, 30 + 2, 2)
    ichimoku_kijun_periods = range(20, 60 + 2, 2)
    ichimoku_senkou_span_b_periods = range(40, 120 + 2, 2)
    ichimoku_displacement_periods = range(20, 45 + 5, 5)

    # Fetch historical data
    client = CcxtClient()
    data = client.fetch_retry(
        symbol=symbol, timeframe=timeframe, start_date=start_date, end_date=end_date
    )

    # Create parameter combinations
    param_combinations = [
        {
            "tenkan": t,
            "kijun": k,
            "senkou_span_b": s,
            "ichimoku_displacement": d,
        }
        for t, k, s, d in itertools.product(
            ichimoku_tenkan_periods,
            ichimoku_kijun_periods,
            ichimoku_senkou_span_b_periods,
            ichimoku_displacement_periods,
        )
    ]

    # Setup data that will be shared across processes
    setup_data = {
        "data": data,
        "symbol": symbol,
        "timeframe": timeframe,
    }

    # Create argument tuples for the worker function
    work_items = [(params, setup_data) for params in param_combinations]

    best_profit = float("-inf")
    best_params = None

    # Use ProcessPoolExecutor for parallel execution
    with ProcessPoolExecutor(max_workers=workers) as executor:
        # Use tqdm for progress tracking
        results = list(
            tqdm(
                executor.map(test_parameter_combination, work_items),
                total=len(work_items),
                desc="Testing combinations",
            )
        )

        # Find the best result
        for profit, params in results:
            if profit > best_profit:
                best_profit = profit
                best_params = params

    click.echo("\nOptimization complete!")

    click.echo(f"\nTotal profit: {best_profit:.2%}")

    click.echo("\nBest parameters found")
    click.echo(f"  Tenkan period: {best_params['tenkan']}")
    click.echo(f"  Kijun period: {best_params['kijun']}")
    click.echo(f"  Senkou Span B period: {best_params['senkou_span_b']}")
    click.echo(f"  ichimoku_displacement: {best_params['ichimoku_displacement']}")
