import os
import ccxt
import pandas as pd
import logging
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv

import config
from trading_env import KrakenMarginEnv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("model_trainer")

def fetch_historical_data(symbol, timeframe="15m", limit=1000):
    logger.info(f"Fetching historical data for {symbol}...")
    exchange = ccxt.kraken({'enableRateLimit': True})
    
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        from ta import add_all_ta_features
        df = add_all_ta_features(df, open="open", high="high", low="low", close="close", volume="volume", fillna=True)
        
        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {e}")
        return None

def train_model():
    logger.info(f"Starting Multi-Asset PPO Training...")
    
    # Train on the specifically targeted margin pair
    symbol = config.TARGET_PAIR
    df = fetch_historical_data(symbol)
    
    if df is None or len(df) < 100:
        logger.error("Not enough data to train model.")
        return

    # Exclude timestamp from observations
    features = df.drop(columns=['timestamp'])
    
    env = DummyVecEnv([lambda: KrakenMarginEnv(features, max_leverage=config.MAX_LEVERAGE)])
    
    logger.info("Initializing PPO Neural Network...")
    model = PPO("MlpPolicy", env, verbose=1, learning_rate=0.0003)
    
    logger.info("Training Model (this may take a while depending on steps)...")
    model.learn(total_timesteps=10000)
    
    model_path = os.path.join(os.path.dirname(__file__), "ppo_trading_model")
    model.save(model_path)
    logger.info(f"✅ Model trained and saved to {model_path}.zip")

if __name__ == "__main__":
    train_model()
