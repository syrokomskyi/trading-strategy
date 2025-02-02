import pandas as pd
from ta.momentum import RSIIndicator
from .base import Strategy

class RSIStrategy(Strategy):
    def __init__(self, symbol: str, timeframe: str, period: int = 14, 
                 overbought: float = 70, oversold: float = 30):
        super().__init__(symbol, timeframe)
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
    
    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("No data available. Call set_data() first.")
        
        # Calculate RSI
        rsi = RSIIndicator(close=self.data['close'], window=self.period).rsi()
        
        # Generate signals
        signals = pd.DataFrame(index=self.data.index)
        signals['price'] = self.data['close']
        signals['signal'] = 0
        
        # Buy signal when RSI crosses below oversold
        signals.loc[rsi < self.oversold, 'signal'] = 1
        # Sell signal when RSI crosses above overbought
        signals.loc[rsi > self.overbought, 'signal'] = -1
        
        # Calculate profit/loss for each signal
        signals['profit'] = signals['signal'] * signals['price'].pct_change()
        
        return signals
