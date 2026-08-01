import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class KrakenMarginEnv(gym.Env):
    """
    Custom Environment that follows gym interface for Margin Trading on Kraken.
    """
    metadata = {'render.modes': ['human']}

    def __init__(self, df: pd.DataFrame, max_leverage: int = 5):
        super(KrakenMarginEnv, self).__init__()
        
        self.df = df
        self.max_leverage = max_leverage
        
        # Actions: 0 = Hold/Close, 1 = Long, 2 = Short
        self.action_space = spaces.Discrete(3)
        
        # Observation space: OHLCV + some basic TA indicators (will be added in trainer)
        # We assume df has at least 10 columns of features
        self.obs_shape = len(self.df.columns)
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(self.obs_shape,), dtype=np.float32
        )
        
        self.current_step = 0
        self.current_position = 0 # 0=flat, 1=long, -1=short
        self.entry_price = 0.0
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = 0
        self.current_position = 0
        self.entry_price = 0.0
        return self._next_observation(), {}

    def _next_observation(self):
        obs = self.df.iloc[self.current_step].values
        return obs.astype(np.float32)

    def step(self, action):
        self.current_step += 1
        
        done = self.current_step >= len(self.df) - 1
        reward = 0
        
        current_price = self.df.iloc[self.current_step]['close']
        
        # Action Logic
        if action == 1: # Long
            if self.current_position == -1:
                # Close short, open long
                profit_pct = (self.entry_price - current_price) / self.entry_price
                reward = profit_pct * self.max_leverage
            elif self.current_position == 0:
                self.entry_price = current_price
            self.current_position = 1
            
        elif action == 2: # Short
            if self.current_position == 1:
                # Close long, open short
                profit_pct = (current_price - self.entry_price) / self.entry_price
                reward = profit_pct * self.max_leverage
            elif self.current_position == 0:
                self.entry_price = current_price
            self.current_position = -1
            
        elif action == 0: # Hold / Close
            if self.current_position == 1:
                profit_pct = (current_price - self.entry_price) / self.entry_price
                reward = profit_pct * self.max_leverage
                self.current_position = 0
            elif self.current_position == -1:
                profit_pct = (self.entry_price - current_price) / self.entry_price
                reward = profit_pct * self.max_leverage
                self.current_position = 0

        # Holding reward (unrealized PNL step by step) to guide the agent
        if self.current_position == 1:
            step_reward = (current_price - self.df.iloc[self.current_step-1]['close']) / self.df.iloc[self.current_step-1]['close']
            reward += step_reward * self.max_leverage
        elif self.current_position == -1:
            step_reward = (self.df.iloc[self.current_step-1]['close'] - current_price) / self.df.iloc[self.current_step-1]['close']
            reward += step_reward * self.max_leverage
            
        obs = self._next_observation()
        info = {'position': self.current_position, 'price': current_price}
        
        return obs, reward, done, False, info

    def render(self, mode='human'):
        pass
