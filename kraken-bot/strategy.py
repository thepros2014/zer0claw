import pandas as pd
import logging

logger = logging.getLogger(__name__)

class SMACrossoverStrategy:
    def __init__(self, short_window: int = 10, long_window: int = 20):
        """
        Initializes the Simple Moving Average (SMA) crossover strategy.
        """
        self.short_window = short_window
        self.long_window = long_window

    def generate_signal(self, df: pd.DataFrame) -> str:
        """
        Analyzes historical OHLCV data to generate a BUY, SELL, or HOLD signal.
        Requires a DataFrame with at least 'close' column.
        """
        if len(df) < self.long_window:
            logger.warning(f"Not enough data to calculate {self.long_window}-period SMA.")
            return "HOLD"

        # Calculate Short and Long Simple Moving Averages
        df["sma_short"] = df["close"].rolling(window=self.short_window).mean()
        df["sma_long"] = df["close"].rolling(window=self.long_window).mean()

        # Get the two most recent periods
        current_short = df["sma_short"].iloc[-1]
        current_long = df["sma_long"].iloc[-1]
        previous_short = df["sma_short"].iloc[-2]
        previous_long = df["sma_long"].iloc[-2]

        logger.debug(f"Current SMA({self.short_window}): {current_short:.4f} | SMA({self.long_window}): {current_long:.4f}")

        # Golden Cross (Short SMA crosses above Long SMA) -> BUY
        if previous_short <= previous_long and current_short > current_long:
            return "BUY"

        # Death Cross (Short SMA crosses below Long SMA) -> SELL
        elif previous_short >= previous_long and current_short < current_long:
            return "SELL"

        # No crossover -> HOLD
        return "HOLD"
