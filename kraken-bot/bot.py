import os
import time
import ccxt
import pandas as pd
import pandas_ta as ta
import logging
from stable_baselines3 import PPO

import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("kraken-bot")

def fetch_active_margin_pairs(exchange):
    try:
        markets = exchange.load_markets()
        margin_pairs = []
        for symbol, market in markets.items():
            if market.get('margin', False) and market.get('active', True):
                # Optionally filter for USD base pairs to keep it manageable
                if '/USD' in symbol:
                    margin_pairs.append(symbol)
        
        # Limit to max pairs setting
        return margin_pairs[:config.MAX_PAIRS]
    except Exception as e:
        logger.error(f"Failed to fetch margin pairs: {e}")
        return []

def get_latest_observation(exchange, symbol):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=config.TIMEFRAME, limit=50)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        df.ta.rsi(length=14, append=True)
        df.ta.macd(append=True)
        df.ta.bbands(append=True)
        df.ta.atr(append=True)
        
        df.dropna(inplace=True)
        
        if len(df) == 0:
            return None, None
            
        latest_features = df.drop(columns=['timestamp']).iloc[-1].values
        current_price = df['close'].iloc[-1]
        
        return latest_features, current_price
    except Exception as e:
        logger.error(f"Error getting observation for {symbol}: {e}")
        return None, None

def main():
    if not config.KRAKEN_ENABLED:
        logger.info("Kraken AI Margin Bot is disabled in setup config. Exiting.")
        return

    logger.info("Starting ZeroClaw Kraken AI Margin Engine...")
    logger.info(f"Max Leverage Allowed: {config.MAX_LEVERAGE}x")
    logger.info(f"Max Pairs Limit: {config.MAX_PAIRS}")
    logger.info(f"Dry Run Mode: {config.DRY_RUN}")

    exchange_args = {
        'apiKey': config.KRAKEN_API_KEY,
        'secret': config.KRAKEN_API_SECRET,
        'enableRateLimit': True,
    }
    exchange = ccxt.kraken(exchange_args)

    model_path = os.path.join(os.path.dirname(__file__), "ppo_trading_model.zip")
    if not os.path.exists(model_path):
        logger.warning(f"AI Model not found at {model_path}.")
        logger.warning("Please run model_trainer.py first to train the AI before starting the bot.")
        return
        
    logger.info("Loading Neural Network AI Brain...")
    model = PPO.load(model_path)

    margin_pairs = fetch_active_margin_pairs(exchange)
    logger.info(f"Scanning {len(margin_pairs)} margin pairs: {', '.join(margin_pairs[:5])}...")

    # State tracking: symbol -> position (1 for long, -1 for short, 0 for flat)
    positions = {symbol: 0 for symbol in margin_pairs}

    while True:
        try:
            logger.info("--- Starting market scan loop ---")
            for symbol in margin_pairs:
                obs, current_price = get_latest_observation(exchange, symbol)
                if obs is None:
                    continue
                    
                # AI makes a prediction
                action, _states = model.predict(obs, deterministic=True)
                
                # 0 = Hold/Close, 1 = Long, 2 = Short
                current_pos = positions[symbol]
                
                if action == 1 and current_pos != 1:
                    logger.info(f"🤖 [AI SIGNAL] {symbol} -> OPEN LONG at {current_price} (Leverage: {config.MAX_LEVERAGE}x)")
                    positions[symbol] = 1
                    if not config.DRY_RUN:
                        try:
                            # Close short if exists
                            if current_pos == -1:
                                exchange.create_market_buy_order(symbol, config.TRADE_AMOUNT_USD / current_price, params={'leverage': config.MAX_LEVERAGE})
                            # Open long
                            exchange.create_market_buy_order(symbol, config.TRADE_AMOUNT_USD / current_price, params={'leverage': config.MAX_LEVERAGE})
                        except Exception as e:
                            logger.error(f"Live trade failed: {e}")
                            
                elif action == 2 and current_pos != -1:
                    logger.info(f"🤖 [AI SIGNAL] {symbol} -> OPEN SHORT at {current_price} (Leverage: {config.MAX_LEVERAGE}x)")
                    positions[symbol] = -1
                    if not config.DRY_RUN:
                        try:
                            # Close long if exists
                            if current_pos == 1:
                                exchange.create_market_sell_order(symbol, config.TRADE_AMOUNT_USD / current_price, params={'leverage': config.MAX_LEVERAGE})
                            # Open short
                            exchange.create_market_sell_order(symbol, config.TRADE_AMOUNT_USD / current_price, params={'leverage': config.MAX_LEVERAGE})
                        except Exception as e:
                            logger.error(f"Live trade failed: {e}")
                            
                elif action == 0 and current_pos != 0:
                    logger.info(f"🤖 [AI SIGNAL] {symbol} -> CLOSE POSITION at {current_price}")
                    if not config.DRY_RUN:
                        try:
                            if current_pos == 1:
                                exchange.create_market_sell_order(symbol, config.TRADE_AMOUNT_USD / current_price, params={'leverage': config.MAX_LEVERAGE})
                            elif current_pos == -1:
                                exchange.create_market_buy_order(symbol, config.TRADE_AMOUNT_USD / current_price, params={'leverage': config.MAX_LEVERAGE})
                        except Exception as e:
                            logger.error(f"Live trade failed: {e}")
                    positions[symbol] = 0

            logger.info(f"Sleeping for {config.POLL_INTERVAL} seconds...")
            time.sleep(config.POLL_INTERVAL)
            
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
