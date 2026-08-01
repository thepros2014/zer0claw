import os
import asyncio
import ccxt.async_support as ccxt
import pandas as pd
import logging
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecFrameStack

import config
from trading_env import KrakenMarginEnv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("model_trainer")

async def fetch_historical_data(symbol, timeframe="15m", limit=1000):
    logger.info(f"Fetching historical data for {symbol}...")
    exchange = ccxt.kraken({'enableRateLimit': True})
    
    try:
        ohlcv = await exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        await exchange.close()
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        from ta import add_all_ta_features
        df = add_all_ta_features(df, open="open", high="high", low="low", close="close", volume="volume", fillna=True)
        
        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df
    except Exception as e:
        await exchange.close()
        logger.error(f"Error fetching data for {symbol}: {e}")
        return None

async def train_model():
    logger.info(f"Starting Multi-Asset PPO Training on Generalized Market Data...")
    
    logger.info(f"Using Watchlist: {', '.join(config.WATCHLIST)}")
    
    all_features = []
    total_memory_bytes = 0
    max_memory_bytes = config.MEMORY_BANK_LIMIT_GB * 1024 * 1024 * 1024
    
    for symbol in config.WATCHLIST:
        # Check if we've hit the 2GB memory bank limit
        if total_memory_bytes >= max_memory_bytes:
            logger.warning(f"Reached {config.MEMORY_BANK_LIMIT_GB}GB Memory Bank Limit. Stopping data fetch.")
            break
            
        df = await fetch_historical_data(symbol)
        if df is not None and len(df) >= 100:
            # Exclude timestamp from observations
            features = df.drop(columns=['timestamp'])
            all_features.append(features)
            total_memory_bytes += features.memory_usage(deep=True).sum()
        else:
            logger.warning(f"Skipping {symbol} due to insufficient data.")
            
    if not all_features:
        logger.error("No data fetched. Aborting training.")
        return
        
    logger.info(f"Data Fetch Complete. Current Memory Bank Usage: {total_memory_bytes / (1024*1024):.2f} MB")
        
    # Combine all historical datasets into one massive environment sequence
    combined_features = pd.concat(all_features, ignore_index=True)
    
    env = DummyVecEnv([lambda: KrakenMarginEnv(combined_features, max_leverage=config.MAX_LEVERAGE)])
    env = VecFrameStack(env, n_stack=5)
    
    logger.info("Initializing PPO Neural Network...")
    model = PPO("MlpPolicy", env, verbose=1, learning_rate=0.0003)
    
    logger.info("Training Model (this may take a while depending on steps)...")
    model.learn(total_timesteps=10000)
    
    model_path = os.path.join(os.path.dirname(__file__), "ppo_trading_model")
    model.save(model_path)
    logger.info(f"✅ Model trained and saved to {model_path}.zip")

if __name__ == "__main__":
    asyncio.run(train_model())
