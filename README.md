# Crypto Trading Strategy Tester

A command-line tool for testing various cryptocurrency trading strategies using historical data. The tool supports multiple strategies and provides performance metrics for strategy evaluation.

## Features

- 📈 Multiple trading strategies support
  - Bollinger Bands Strategy
  - MACD (Moving Average Convergence Divergence) Strategy
  - Moving Average Crossover Strategy
  - RSI (Relative Strength Index) Strategy
- 💹 Real-time and historical data from multiple exchanges
- 📊 Performance metrics calculation
- ⚙️ Configurable strategy parameters
- 💾 Data caching for faster backtesting

## Installation

### Clone the repository

```bash
git clone https://github.com/syrokomskyi/trading-strategy.git
cd trading-strategy
```

### Install dependencies

```bash
pip install -r requirements.txt
```

## Command Line Interface

Test trading strategies using the CLI:

### Basic usage

```bash
# Test MA Crossover strategy
trading-strategy run --strategy ma-cross --symbol BTC/USDT --timeframe 1h

# Test MACD strategy
trading-strategy run --strategy macd --symbol BTC/USDT --timeframe 4h --fast-period 12 --slow-period 26 --signal-period 9

# Test RSI strategy with custom parameters
trading-strategy run --strategy rsi --symbol ETH/USDT --timeframe 4h --rsi-period 14 --rsi-overbought 70 --rsi-oversold 30

# Test Bollinger Bands strategy
trading-strategy run --strategy bb --symbol BTC/USDT --timeframe 1h --bb-period 20 --bb-std 2.0

# Backtest with specific date range
trading-strategy run --strategy ma-cross --symbol BTC/USDT --timeframe 1d --start-date 2023-01-01 --end-date 2100-12-31
```

### Available options

- `--strategy`: Trading strategy to test (ma-cross, rsi, bb, macd)
- `--symbol`: Trading pair (e.g., BTC/USDT, ETH/USDT)
- `--timeframe`: Candle timeframe (1m, 5m, 15m, 1h, 4h, 1d)
- `--start-date`: Start date for backtesting (YYYY-MM-DD)
- `--end-date`: End date for backtesting (YYYY-MM-DD)

Strategy-specific options:

- Bollinger Bands:

  - `--bb-period`: Period for moving average calculation (default: 20)
  - `--bb-std`: Number of standard deviations for bands (default: 2.0)

- MA Crossover:

  - `--fast-period`: Fast moving average period (default: 10)
  - `--slow-period`: Slow moving average period (default: 20)

- MACD:

  - `--fast-period`: Fast EMA period (default: 12)
  - `--slow-period`: Slow EMA period (default: 26)
  - `--signal-period`: Signal line period (default: 9)

- RSI:
  - `--rsi-period`: RSI calculation period (default: 14)
  - `--rsi-overbought`: Overbought threshold (default: 70)
  - `--rsi-oversold`: Oversold threshold (default: 30)

## Implemented Strategies

### Bollinger Bands

This strategy uses Bollinger Bands to identify overbought and oversold conditions:

- Buy when price crosses below the lower band (oversold)
- Sell when price crosses above the upper band (overbought)

### Moving Average Crossover

This strategy generates signals based on the crossing of two moving averages:

- Buy when fast MA crosses above slow MA
- Sell when fast MA crosses below slow MA

### RSI (Relative Strength Index)

This strategy uses the RSI indicator to identify overbought and oversold conditions:

- Buy when RSI crosses below oversold threshold
- Sell when RSI crosses above overbought threshold

### MACD (Moving Average Convergence Divergence)

This strategy uses the MACD indicator to identify trend changes and momentum shifts:

- Buy when MACD line crosses above the signal line
- Sell when MACD line crosses below the signal line

The MACD is calculated using three moving averages:

- Fast EMA (default: 12 periods)
- Slow EMA (default: 26 periods)
- Signal line (default: 9 periods)

This strategy is particularly effective for identifying trend changes and momentum shifts in the market.

## Contributing

Feel free to contribute by adding new strategies or improving existing ones. Please follow the project's coding standards and include tests for new features.

## License

MIT License
