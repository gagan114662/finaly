import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import os
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Backtester:
    def __init__(self, data_dir: str = "OpenAlpha_Evolve/quant_strategy/data"):
        self.data_dir = data_dir
        self.data_cache = {}
        
    def load_market_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Load market data for backtesting"""
        cache_key = f"{symbol}_{start_date}_{end_date}"
        if cache_key in self.data_cache:
            return self.data_cache[cache_key]
            
        # Find matching data files
        data_path = os.path.join(self.data_dir, "future")
        exchanges = [d for d in os.listdir(data_path) 
                   if os.path.isdir(os.path.join(data_path, d))]
        
        df = None
        for exchange in exchanges:
            try:
                # Load daily data
                daily_path = os.path.join(data_path, exchange, "daily")
                files = [f for f in os.listdir(daily_path) 
                        if f.startswith(symbol.lower()) and f.endswith("_trade.zip")]
                
                if files:
                    file_path = os.path.join(daily_path, files[0])
                    df = pd.read_csv(file_path, compression='zip')
                    df['date'] = pd.to_datetime(df['date'])
                    df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
                    break
                    
            except Exception as e:
                logger.warning(f"Error loading data for {symbol} from {exchange}: {e}")
        
        if df is None:
            raise ValueError(f"No market data found for {symbol} between {start_date} and {end_date}")
            
        self.data_cache[cache_key] = df
        return df
        
    def run_backtest(self, strategy_func, symbol: str, 
                    start_date: str, end_date: str,
                    initial_capital: float = 100000) -> Dict:
        """Run backtest on historical data"""
        data = self.load_market_data(symbol, start_date, end_date)
        
        # Prepare strategy context
        context = {
            'positions': [],
            'trades': [],
            'portfolio_value': initial_capital,
            'cash': initial_capital,
            'current_date': None,
            'data': data
        }
        
        # Run strategy on each day
        for idx, row in data.iterrows():
            context['current_date'] = row['date']
            try:
                strategy_func(context, row)
            except Exception as e:
                logger.error(f"Strategy error on {row['date']}: {e}")
                
        # Calculate performance metrics
        return self.calculate_performance(context)
        
    def calculate_performance(self, context: Dict) -> Dict:
        """Calculate key performance metrics"""
        trades = pd.DataFrame(context['trades'])
        if trades.empty:
            return {
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'total_return': 0,
                'win_rate': 0,
                'profit_factor': 1
            }
            
        # Calculate returns
        trades['return'] = trades['exit_price'] / trades['entry_price'] - 1
        trades['win'] = trades['return'] > 0
        
        # Portfolio metrics
        sharpe = trades['return'].mean() / trades['return'].std() * np.sqrt(252)
        max_dd = self.calculate_max_drawdown(trades['return'])
        total_return = context['portfolio_value'] / context['initial_capital'] - 1
        win_rate = trades['win'].mean()
        profit_factor = trades[trades['win']]['return'].sum() / abs(trades[~trades['win']]['return'].sum())
        
        return {
            'sharpe_ratio': sharpe,
            'max_drawdown': max_dd,
            'total_return': total_return,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'num_trades': len(trades)
        }
        
    def calculate_max_drawdown(self, returns: List[float]) -> float:
        """Calculate maximum drawdown"""
        cumulative = np.cumprod(1 + np.array(returns))
        peak = np.maximum.accumulate(cumulative)
        drawdown = (peak - cumulative) / peak
        return np.max(drawdown)