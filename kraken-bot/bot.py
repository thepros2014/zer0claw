import os
import asyncio
import ccxt.async_support as ccxt
import pandas as pd
import logging
from stable_baselines3 import PPO

import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("kraken-bot")


async def get_latest_observation(exchange, symbol):
    try:
        ohlcv = await exchange.fetch_ohlcv(symbol, timeframe=config.TIMEFRAME, limit=50)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        from ta import add_all_ta_features
        df = add_all_ta_features(df, open="open", high="high", low="low", close="close", volume="volume", fillna=True)
        
        df.dropna(inplace=True)
        
        if len(df) == 0:
            return None, None
            
        latest_features = df.drop(columns=['timestamp']).iloc[-1].values
        current_price = df['close'].iloc[-1]
        
        return latest_features, current_price
    except Exception as e:
        logger.error(f"Error getting observation for {symbol}: {e}")
        return None, None

async def main():
    if not config.KRAKEN_ENABLED:
        logger.info("Kraken AI Margin Bot is disabled in setup config. Exiting.")
        return

    logger.info("Starting ZeroClaw Kraken AI Margin Engine...")
    logger.info(f"Max Leverage Allowed: {config.MAX_LEVERAGE}x")
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

    logger.info(f"Watchlist: {', '.join(config.WATCHLIST)}")
    logger.info(f"Trade Mode: {config.TRADE_MODE.upper()}")
    
    order_params = {'leverage': config.MAX_LEVERAGE} if config.TRADE_MODE == "margin" else {}
    
    # State tracking: Stick to ONE active pair at a time
    active_trade = None
    entry_price = 0.0
    entry_direction = 0  # 1 for long, -1 for short

    while True:
        try:
            if active_trade is None:
                logger.info(f"--- Scanning {len(config.WATCHLIST)} Pairs for Opportunities ---")
                
                # Concurrently fetch observations for all margin pairs
                tasks = [get_latest_observation(exchange, symbol) for symbol in config.WATCHLIST]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for i, symbol in enumerate(config.WATCHLIST):
                    res = results[i]
                    if isinstance(res, Exception):
                        logger.error(f"Failed to fetch {symbol}: {res}")
                        continue
                        
                    obs, current_price = res
                    if obs is None: continue
                    
                    action, _ = model.predict(obs, deterministic=True)
                    
                    # Prevent naked shorting in Spot Mode
                    if config.TRADE_MODE == "spot" and action == 2:
                        continue # Ignore short signals in spot mode
                        
                    if action == 1:
                        if config.TRADE_MODE == "margin":
                            logger.info(f"🤖 [AI SIGNAL] {symbol} -> OPEN LONG at {current_price} (Leverage: {config.MAX_LEVERAGE}x)")
                        else:
                            logger.info(f"🤖 [AI SIGNAL] {symbol} -> BUY SPOT at {current_price}")
                            
                        active_trade = symbol
                        entry_price = current_price
                        entry_direction = 1
                        
                        if not config.DRY_RUN:
                            try:
                                await exchange.create_market_buy_order(symbol, config.TRADE_AMOUNT_USD / current_price, params=order_params)
                            except Exception as e:
                                logger.error(f"Live trade failed: {e}")
                                active_trade = None
                        break  # Stop scanning once we find a trade!
                        
                    elif action == 2:
                        logger.info(f"🤖 [AI SIGNAL] {symbol} -> OPEN SHORT at {current_price} (Leverage: {config.MAX_LEVERAGE}x)")
                        active_trade = symbol
                        entry_price = current_price
                        entry_direction = -1
                        
                        if not config.DRY_RUN:
                            try:
                                await exchange.create_market_sell_order(symbol, config.TRADE_AMOUNT_USD / current_price, params=order_params)
                            except Exception as e:
                                logger.error(f"Live trade failed: {e}")
                                active_trade = None
                        break  # Stop scanning once we find a trade!

            else:
                symbol = active_trade
                logger.info(f"--- Monitoring Active Trade: {symbol} ---")
                obs, current_price = await get_latest_observation(exchange, symbol)
                
                if obs is not None:
                    # 2% Stop Loss Logic
                    if entry_direction == 1 and current_price <= entry_price * (1 - config.STOP_LOSS_PCT):
                        logger.warning(f"🚨 [STOP LOSS] {symbol} Long hit {config.STOP_LOSS_PCT*100}% loss at {current_price}. CLOSING POSITION.")
                        action = 0
                        stop_loss_triggered = True
                    elif entry_direction == -1 and current_price >= entry_price * (1 + config.STOP_LOSS_PCT):
                        logger.warning(f"🚨 [STOP LOSS] {symbol} Short hit {config.STOP_LOSS_PCT*100}% loss at {current_price}. CLOSING POSITION.")
                        action = 0
                        stop_loss_triggered = True
                    else:
                        stop_loss_triggered = False
                        action, _ = model.predict(obs, deterministic=True)

                    # Override short signals in spot mode
                    if config.TRADE_MODE == "spot" and action == 2:
                        action = 0  # Treat short signal as close position if we are long

                    if action == 0 or stop_loss_triggered:
                        if not stop_loss_triggered:
                            logger.info(f"🤖 [AI SIGNAL] {symbol} -> CLOSE POSITION at {current_price}")
                        
                        if not config.DRY_RUN:
                            try:
                                if entry_direction == 1:
                                    await exchange.create_market_sell_order(symbol, config.TRADE_AMOUNT_USD / current_price, params=order_params)
                                elif entry_direction == -1:
                                    await exchange.create_market_buy_order(symbol, config.TRADE_AMOUNT_USD / current_price, params=order_params)
                            except Exception as e:
                                logger.error(f"Live trade failed: {e}")
                                
                        active_trade = None
                        entry_direction = 0
                        
                    elif action == 1 and entry_direction == -1:
                        logger.info(f"🤖 [AI REVERSAL] {symbol} -> CLOSE SHORT, OPEN LONG at {current_price}")
                        if not config.DRY_RUN:
                            try:
                                await exchange.create_market_buy_order(symbol, config.TRADE_AMOUNT_USD / current_price, params=order_params)
                                await exchange.create_market_buy_order(symbol, config.TRADE_AMOUNT_USD / current_price, params=order_params)
                            except Exception as e:
                                logger.error(f"Live trade failed: {e}")
                        entry_price = current_price
                        entry_direction = 1
                        
                    elif action == 2 and entry_direction == 1:
                        logger.info(f"🤖 [AI REVERSAL] {symbol} -> CLOSE LONG, OPEN SHORT at {current_price}")
                        if not config.DRY_RUN:
                            try:
                                await exchange.create_market_sell_order(symbol, config.TRADE_AMOUNT_USD / current_price, params=order_params)
                                await exchange.create_market_sell_order(symbol, config.TRADE_AMOUNT_USD / current_price, params=order_params)
                            except Exception as e:
                                logger.error(f"Live trade failed: {e}")
                        entry_price = current_price
                        entry_direction = -1

            logger.info(f"Sleeping for {config.POLL_INTERVAL} seconds...")
            await asyncio.sleep(config.POLL_INTERVAL)
            
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
