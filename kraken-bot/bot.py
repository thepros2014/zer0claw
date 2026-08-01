import os
import asyncio
import ccxt.async_support as ccxt
import pandas as pd
import numpy as np
from collections import deque
import logging
from stable_baselines3 import PPO

import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("kraken-bot")

# Global observation buffer for frame stacking
obs_buffer = {}

async def fetch_portfolio_state(exchange, symbol):
    # Fetch actual balance and open positions from Kraken
    try:
        balance_info = await exchange.fetch_balance()
        # Kraken USD balance might be under 'ZUSD' or 'USD'
        usd_balance = balance_info.get('USD', {}).get('free', 0.0)
        if usd_balance == 0.0:
            usd_balance = balance_info.get('ZUSD', {}).get('free', 0.0)
            
        # Try to get open positions (margin) or base asset balance (spot)
        base_asset = symbol.split('/')[0]
        base_balance = balance_info.get(base_asset, {}).get('free', 0.0)
        
        # We will simplify unrealized PnL to 0.0 for now in this wrapper
        # unless we fetch real trades/orders.
        unrealized_pnl = 0.0
        position_size = 0.0
        
        current_price = 0.0
        ticker = await exchange.fetch_ticker(symbol)
        if ticker and 'last' in ticker:
            current_price = ticker['last']
            
        base_value_usd = base_balance * current_price
        total_portfolio_value = usd_balance + base_value_usd
        
        if total_portfolio_value > 0:
            position_size = base_value_usd / total_portfolio_value
            
        return total_portfolio_value, unrealized_pnl, position_size, current_price
    except Exception as e:
        logger.error(f"Error fetching portfolio state: {e}")
        return 1000.0, 0.0, 0.0, 0.0 # fallback

async def get_latest_observation(exchange, symbol, portfolio_state):
    try:
        portfolio_value, unrealized_pnl, position_size, _ = portfolio_state
        ohlcv = await exchange.fetch_ohlcv(symbol, timeframe=config.TIMEFRAME, limit=50)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        from ta import add_all_ta_features
        df = add_all_ta_features(df, open="open", high="high", low="low", close="close", volume="volume", fillna=True)
        
        df.dropna(inplace=True)
        
        if len(df) == 0:
            return None, None
            
        # Get raw TA features
        ta_features = df.drop(columns=['timestamp']).iloc[-1].values
        
        # Inject portfolio metrics (MUST MATCH trading_env.py obs space exactly)
        portfolio_metrics = np.array([portfolio_value, unrealized_pnl, position_size])
        
        # Final combined observation for this single step
        single_obs = np.concatenate([ta_features, portfolio_metrics]).astype(np.float32)
        current_price = df['close'].iloc[-1]
        
        # Manage the 5-frame stack
        if symbol not in obs_buffer:
            # Initialize buffer with copies of the first observation
            obs_buffer[symbol] = deque([single_obs for _ in range(5)], maxlen=5)
        else:
            obs_buffer[symbol].append(single_obs)
            
        # Stack into a single 1D array of shape (5 * obs_shape,)
        # Note: SB3 VecFrameStack stacks along the last dimension for 1D obs
        # or flat concatenation if expected. For a Box environment, PPO flatten might expect (1, stacked_dim)
        stacked_obs = np.concatenate(list(obs_buffer[symbol]))
        
        return stacked_obs, current_price
    except Exception as e:
        logger.error(f"Error getting observation for {symbol}: {e}")
        return None, None

async def main():
    if not config.KRAKEN_ENABLED:
        logger.info("Kraken AI Margin Bot is disabled in setup config. Exiting.")
        return

    logger.info("Starting ZeroClaw Kraken AI Margin Engine (Portfolio Aware)...")
    logger.info(f"Trade Mode: {config.TRADE_MODE.upper()}")
    
    exchange = ccxt.kraken({
        'apiKey': config.KRAKEN_API_KEY,
        'secret': config.KRAKEN_API_SECRET,
        'enableRateLimit': True,
    })

    model_path = os.path.join(os.path.dirname(__file__), "ppo_trading_model.zip")
    if not os.path.exists(model_path):
        logger.warning(f"AI Model not found at {model_path}.")
        logger.warning("Please run model_trainer.py first to train the AI before starting the bot.")
        return
        
    logger.info("Loading Neural Network AI Brain...")
    model = PPO.load(model_path)

    logger.info(f"Watchlist: {', '.join(config.WATCHLIST)}")
    order_params = {'leverage': config.MAX_LEVERAGE} if config.TRADE_MODE == "margin" else {}

    while True:
        try:
            logger.info(f"--- Synchronizing State with Kraken & Analyzing {len(config.WATCHLIST)} Pairs ---")
            
            for symbol in config.WATCHLIST:
                portfolio_state = await fetch_portfolio_state(exchange, symbol)
                total_val, pnl, pos_size, _ = portfolio_state
                
                obs, current_price = await get_latest_observation(exchange, symbol, portfolio_state)
                if obs is None: continue
                
                # Action space: 0=Hold, 1=Buy 50%, 2=Buy 100%, 3=Sell 50%, 4=Sell 100%
                action, _ = model.predict(obs, deterministic=True)
                action = int(action.item() if hasattr(action, 'item') else action)
                
                # Spot Mode overrides (Prevent selling naked shorts)
                if config.TRADE_MODE == "spot":
                    if action in [3, 4] and pos_size < 0.05:
                        action = 0 
                
                if action != 0:
                    action_name = {1: "BUY 50%", 2: "BUY 100%", 3: "SELL 50%", 4: "SELL 100%"}[action]
                    logger.info(f"🤖 [AI SIGNAL] {symbol} -> {action_name} at {current_price} | Portfolio Val: ${total_val:.2f} | Pos Size: {pos_size*100:.1f}%")
                    
                    if not config.DRY_RUN:
                        # True Dynamic Position Sizing Execution
                        try:
                            # We must load markets to use precision formatting
                            if not exchange.markets:
                                await exchange.load_markets()
                                
                            balance_info = await exchange.fetch_balance()
                            usd_balance = balance_info.get('USD', {}).get('free', 0.0)
                            if usd_balance == 0.0: usd_balance = balance_info.get('ZUSD', {}).get('free', 0.0)
                            base_asset = symbol.split('/')[0]
                            base_balance = balance_info.get(base_asset, {}).get('free', 0.0)

                            amount_to_trade = 0.0
                            if action == 1: # Buy 50% of available USD
                                spend_usd = usd_balance * 0.5
                                amount_to_trade = spend_usd / current_price
                            elif action == 2: # Buy 100% of available USD
                                spend_usd = usd_balance * 0.98 # Leave 2% for fees/slippage
                                amount_to_trade = spend_usd / current_price
                            elif action == 3: # Sell 50% of base asset
                                amount_to_trade = base_balance * 0.5
                            elif action == 4: # Sell 100% of base asset
                                amount_to_trade = base_balance

                            # Apply Kraken's strict lot size precision rules
                            amount_str = exchange.amount_to_precision(symbol, amount_to_trade)
                            amount_to_trade = float(amount_str)
                            
                            if amount_to_trade <= 0:
                                logger.warning(f"Calculated trade amount is 0 (Insufficient Balance). Skipping trade.")
                                continue

                            if action in [1, 2]:
                                await exchange.create_market_buy_order(symbol, amount_to_trade, params=order_params)
                            elif action in [3, 4]:
                                await exchange.create_market_sell_order(symbol, amount_to_trade, params=order_params)
                        except Exception as e:
                            logger.error(f"Live trade failed: {e}")

            logger.info(f"Sleeping for {config.POLL_INTERVAL} seconds...")
            await asyncio.sleep(config.POLL_INTERVAL)
            
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
