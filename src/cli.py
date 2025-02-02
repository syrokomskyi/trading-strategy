import click
from datetime import datetime
from pathlib import Path
from typing import Optional

from .data.fetcher import DataFetcher
from .strategies.ma_cross import MovingAverageCrossStrategy
from .strategies.rsi import RSIStrategy


@click.group()
def cli():
    """Crypto Trading Strategy Tester CLI"""
    pass


@cli.command()
@click.option('--strategy', type=click.Choice(['ma-cross', 'rsi']), required=True,
              help='Trading strategy to test')
@click.option('--symbol', required=True, help='Trading pair (e.g., BTC/USDT)')
@click.option('--timeframe', required=True,
              help='Candle timeframe (1m, 5m, 15m, 1h, 4h, 1d)')
@click.option('--start-date', type=click.DateTime(),
              help='Start date for backtesting (YYYY-MM-DD)')
@click.option('--end-date', type=click.DateTime(),
              help='End date for backtesting (YYYY-MM-DD)')
# MA Crossover specific options
@click.option('--fast-period', type=int, default=10,
              help='Fast moving average period')
@click.option('--slow-period', type=int, default=20,
              help='Slow moving average period')
# RSI specific options
@click.option('--rsi-period', type=int, default=14,
              help='RSI calculation period')
@click.option('--rsi-overbought', type=float, default=70,
              help='RSI overbought threshold')
@click.option('--rsi-oversold', type=float, default=30,
              help='RSI oversold threshold')
def test(strategy: str, symbol: str, timeframe: str,
         start_date: Optional[datetime], end_date: Optional[datetime],
         fast_period: int, slow_period: int,
         rsi_period: int, rsi_overbought: float, rsi_oversold: float):
    """Test a trading strategy with historical data"""
    
    # Initialize data fetcher
    fetcher = DataFetcher()
    
    # Fetch historical data
    data = fetcher.fetch_ohlcv(
        symbol=symbol,
        timeframe=timeframe,
        start_date=start_date,
        end_date=end_date
    )
    
    # Initialize strategy
    if strategy == 'ma-cross':
        strat = MovingAverageCrossStrategy(
            symbol=symbol,
            timeframe=timeframe,
            fast_period=fast_period,
            slow_period=slow_period
        )
    else:  # RSI strategy
        strat = RSIStrategy(
            symbol=symbol,
            timeframe=timeframe,
            period=rsi_period,
            overbought=rsi_overbought,
            oversold=rsi_oversold
        )
    
    # Set data and generate signals
    strat.set_data(data)
    signals = strat.generate_signals()
    metrics = strat.get_performance_metrics()
    
    # Print results
    click.echo(f"\nStrategy: {strategy.upper()}")
    click.echo(f"Symbol: {symbol}")
    click.echo(f"Timeframe: {timeframe}")
    click.echo("\nPerformance Metrics:")
    click.echo(f"Total Trades: {metrics['total_trades']}")
    click.echo(f"Profitable Trades: {metrics['profitable_trades']}")
    click.echo(f"Win Rate: {metrics['win_rate']:.2%}")
    click.echo(f"Total Profit: {metrics['total_profit']:.2%}")
    click.echo(f"Max Drawdown: {metrics['max_drawdown']:.2%}")


def main():
    cli()


if __name__ == "__main__":
    main()
