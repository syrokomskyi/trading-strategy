from dotenv import load_dotenv
import click
from datetime import datetime
from typing import Optional

from ..client.binance import BinanceClient
from ..client.ccxt import CcxtClient
from ..strategy.factory import StrategyFactory

load_dotenv()


@click.command()
@click.option(
    "--strategy",
    type=click.Choice(["bollinger-bands", "ichimoku", "ma-cross", "macd", "rsi"]),
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
@click.option(
    "--bollinger-bands-period", type=int, default=20, help="Bollinger Bands period"
)
@click.option(
    "--bollinger-bands-std",
    type=float,
    default=2.0,
    help="Number of standard deviations",
)

# Ichimoku specific options
@click.option("--ichimoku-tenkan-period", type=int, default=9, help="Tenkan-sen period")
@click.option("--ichimoku-kijun-period", type=int, default=26, help="Kijun-sen period")
@click.option(
    "--ichimoku-senkou-span-b-period", type=int, default=52, help="Senkou Span B period"
)
@click.option(
    "--ichimoku_displacement", type=int, default=26, help="Displacement period"
)

# MA Crossover specific options
@click.option(
    "--ma-cross-fast-period", type=int, default=12, help="Fast EMA period for MA-Cross"
)
@click.option(
    "--ma-cross-slow-period", type=int, default=26, help="Slow EMA period for MA-Cross"
)

# MACD specific options
@click.option(
    "--macd-fast-period", type=int, default=12, help="Fast EMA period for MACD"
)
@click.option(
    "--macd-slow-period", type=int, default=26, help="Slow EMA period for MACD"
)
@click.option(
    "--macd-signal-period", type=int, default=9, help="Signal line period for MACD"
)

# RSI specific options
@click.option("--rsi-period", type=int, default=14, help="RSI calculation period")
@click.option(
    "--rsi-overbought", type=float, default=70, help="RSI overbought threshold"
)
@click.option("--rsi-oversold", type=float, default=30, help="RSI oversold threshold")
def run(
    strategy: str,
    symbol: str,
    timeframe: str,
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    # Bollinger Bands
    bollinger_bands_period: int,
    bollinger_bands_std: float,
    # MA Crossover
    ma_cross_fast_period: int,
    ma_cross_slow_period: int,
    # MACD
    macd_fast_period: int,
    macd_slow_period: int,
    macd_signal_period: int,
    # RSI
    rsi_period: int,
    rsi_overbought: float,
    rsi_oversold: float,
    # Ichimoku
    ichimoku_tenkan_period: int,
    ichimoku_kijun_period: int,
    ichimoku_senkou_span_b_period: int,
    ichimoku_displacement: int,
):
    """Test a trading strategy with historical data"""

    # Fetch historical data
    client = CcxtClient()
    # client = BinanceClient(
    #     api_key=os.getenv("BINANCE_API_KEY"),
    #     api_secret=os.getenv("BINANCE_API_SECRET"),
    # )
    # print(client.fetch_balance())
    data = client.fetch_retry(
        symbol=symbol, timeframe=timeframe, start_date=start_date, end_date=end_date
    )

    # Initialize strategy
    st = StrategyFactory.build(
        strategy=strategy,
        data=data,
        symbol=symbol,
        timeframe=timeframe,
        # Bollinger Bands
        bollinger_bands_period=bollinger_bands_period,
        bollinger_bands_std=bollinger_bands_std,
        # Ichimoku
        ichimoku_tenkan_period=ichimoku_tenkan_period,
        ichimoku_kijun_period=ichimoku_kijun_period,
        ichimoku_senkou_span_b_period=ichimoku_senkou_span_b_period,
        ichimoku_displacement=ichimoku_displacement,
        # MA-Cross
        ma_cross_fast_period=ma_cross_fast_period,
        ma_cross_slow_period=ma_cross_slow_period,
        # MACD
        macd_fast_period=macd_fast_period,
        macd_slow_period=macd_slow_period,
        macd_signal_period=macd_signal_period,
        # RSI
        rsi_period=rsi_period,
        rsi_overbought=rsi_overbought,
        rsi_oversold=rsi_oversold,
    )

    metrics = st.get_performance_metrics()

    # Print results
    click.echo(f"\nStrategy: {strategy.upper()}")
    click.echo(f"Symbol: {symbol}")
    click.echo(f"Timeframe: {timeframe}")
    click.echo(f"Count signals: {metrics['count_signals']}")

    click.echo("\nPerformance metrics")
    click.echo(f"  Total profit: {metrics['total_profit']:.2%}")
    click.echo(
        f"  Profitable / Total trades: {metrics['profitable_trades']} / {metrics['total_trades']}"
    )
    click.echo(f"  Win rate: {metrics['win_rate']:.2%}")
    click.echo(f"  Max drawdown: {metrics['max_drawdown']:.2%}")
