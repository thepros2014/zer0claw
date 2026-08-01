import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class KrakenMarginEnv(gym.Env):
    """
    Custom Environment that follows gym interface for Margin Trading on Kraken.
    Now equipped with Portfolio Awareness (balance, PnL, position sizing).
    """
    metadata = {'render.modes': ['human']}

    def __init__(self, df: pd.DataFrame, max_leverage: int = 5):
        super(KrakenMarginEnv, self).__init__()
        
        self.df = df
        self.max_leverage = max_leverage
        
        # Actions: 
        # 0 = Hold
        # 1 = Buy 50% 
        # 2 = Buy 100%
        # 3 = Sell 50%
        # 4 = Sell 100%
        self.action_space = spaces.Discrete(5)
        
        # Observation space: OHLCV + TA + [balance, unrealized_pnl, position_size]
        self.obs_shape = len(self.df.columns) + 3
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(self.obs_shape,), dtype=np.float32
        )
        
        self.initial_balance = 1000.0
        self.balance = self.initial_balance
        self.position_size = 0.0
        self.unrealized_pnl = 0.0
        self.entry_price = 0.0
        self.current_step = 0
        self.current_position = 0 # 0=flat, 1=long, -1=short
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.balance = self.initial_balance
        self.position_size = 0.0
        self.unrealized_pnl = 0.0
        self.entry_price = 0.0
        self.current_step = 0
        self.current_position = 0
        return self._next_observation(), {}

    def _next_observation(self):
        obs = self.df.iloc[self.current_step].values
        # Inject portfolio metrics into the AI's "senses"
        portfolio_metrics = np.array([self.balance, self.unrealized_pnl, self.position_size])
        obs = np.concatenate([obs, portfolio_metrics])
        return obs.astype(np.float32)

    def step(self, action):
        self.current_step += 1
        done = self.current_step >= len(self.df) - 1
        
        current_price = self.df.iloc[self.current_step]['close']
        prev_price = self.df.iloc[self.current_step-1]['close']
        
        # Calculate PnL from previous step to this step
        step_reward = 0.0
        if self.current_position == 1:
            step_reward = ((current_price - prev_price) / prev_price) * self.balance * self.position_size * self.max_leverage
        elif self.current_position == -1:
            step_reward = ((prev_price - current_price) / prev_price) * self.balance * self.position_size * self.max_leverage
            
        self.unrealized_pnl += step_reward
        self.balance += step_reward
        
        # Action Logic
        if action == 1: # Buy 50%
            if self.current_position == -1:
                self.position_size -= 0.5
                if self.position_size <= 0:
                    self.current_position = 0
                    self.position_size = 0.0
            else:
                self.current_position = 1
                self.position_size = min(1.0, self.position_size + 0.5)
                self.entry_price = current_price
                
        elif action == 2: # Buy 100%
            self.current_position = 1
            self.position_size = 1.0
            self.entry_price = current_price
            
        elif action == 3: # Sell 50%
            if self.current_position == 1:
                self.position_size -= 0.5
                if self.position_size <= 0:
                    self.current_position = 0
                    self.position_size = 0.0
            else:
                self.current_position = -1
                self.position_size = min(1.0, self.position_size + 0.5)
                self.entry_price = current_price
                
        elif action == 4: # Sell 100%
            self.current_position = -1
            self.position_size = 1.0
            self.entry_price = current_price
            
        elif action == 0: # Hold
            pass

        if self.balance <= 0:
            done = True
            step_reward -= 1000 # Penalty for bankruptcy

        obs = self._next_observation()
        info = {'position': self.current_position, 'price': current_price}
        
        return obs, step_reward, done, False, info

    def render(self, mode='human'):
        pass
