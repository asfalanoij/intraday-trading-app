import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualization
sns.set_style("darkgrid")

class EmergencyExitSimulator:
    def __init__(self, current_price, initial_capital=100_000_000):
        self.current_price = current_price
        self.initial_capital = initial_capital
        self.risk_per_trade = 0.01  # 1% risk per trade
        
        # Emergency exit levels
        self.emergency_levels = {
            'price_exit': current_price * 1.04,  # 4% above entry
            'rsi_exit': 85,
            'volume_exit': 2.0,  # 2x average volume
            'stop_loss': current_price * 0.9708  # 2.92% below entry
        }
        
        # Take profit levels (scaled based on risk)
        self.take_profit_levels = {
            'tp1': current_price * 1.015,  # 1.5% gain (0.5R)
            'tp2': current_price * 1.029,  # 2.9% gain (1R)
            'tp3': current_price * 1.044   # 4.4% gain (1.5R)
        }
        
        # Dynamic stop loss levels
        self.stop_levels = {
            'initial_stop': current_price * 0.9708,  # 2.92% initial stop
            'breakeven_stop': current_price,  # Move to breakeven after TP1
            'trailing_stop': current_price * 0.985  # 1.5% trailing stop after TP2
        }
        
    def calculate_position_size(self):
        risk_amount = self.initial_capital * self.risk_per_trade
        stop_loss_points = self.current_price - self.stop_levels['initial_stop']
        return int(risk_amount / stop_loss_points)
    
    def simulate_price_path(self, n_steps=390, volatility=0.02):
        """Simulate 1-minute price data for a trading day"""
        returns = np.random.normal(0, volatility/np.sqrt(390), n_steps)
        price_path = self.current_price * np.exp(np.cumsum(returns))
        return price_path
    
    def calculate_rsi(self, prices, period=14):
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        for i in range(period, len(gains)):
            avg_gain = (avg_gain * (period-1) + gains[i]) / period
            avg_loss = (avg_loss * (period-1) + losses[i]) / period
            
        rs = avg_gain / avg_loss if avg_loss != 0 else 0
        return 100 - (100 / (1 + rs))
    
    def check_exit_conditions(self, price, volume, rsi, reached_tp1=False):
        # Emergency exits
        if (price >= self.emergency_levels['price_exit'] or
            volume >= self.emergency_levels['volume_exit'] or
            rsi >= self.emergency_levels['rsi_exit']):
            return True, 'emergency'
            
        # Take profit exits
        if price >= self.take_profit_levels['tp3']:
            return True, 'tp3'
        elif price >= self.take_profit_levels['tp2']:
            return True, 'tp2'
        elif price >= self.take_profit_levels['tp1']:
            return True, 'tp1'
            
        # Stop loss exits
        current_stop = self.stop_levels['initial_stop']
        if reached_tp1:
            current_stop = max(self.stop_levels['breakeven_stop'], 
                             price * 0.985)  # Trailing stop
            
        if price <= current_stop:
            return True, 'stop'
            
        return False, None
    
    def run_simulation(self, n_sims=1000):
        results = []
        for _ in range(n_sims):
            prices = self.simulate_price_path()
            volumes = np.random.lognormal(0, 0.5, len(prices))
            rsi = self.calculate_rsi(prices)
            
            exit_triggered = False
            exit_price = prices[-1]
            exit_time = len(prices) - 1
            exit_type = 'session_end'
            reached_tp1 = False
            
            for t in range(1, len(prices)):
                if prices[t] >= self.take_profit_levels['tp1']:
                    reached_tp1 = True
                    
                should_exit, exit_reason = self.check_exit_conditions(
                    prices[t], volumes[t], rsi, reached_tp1)
                
                if should_exit:
                    exit_triggered = True
                    exit_price = prices[t]
                    exit_time = t
                    exit_type = exit_reason
                    break
            
            pnl = (exit_price - self.current_price) / self.current_price
            results.append({
                'exit_price': exit_price,
                'exit_time': t,
                'pnl': pnl,
                'exit_type': exit_type
            })
        
        return pd.DataFrame(results)

def main():
    # Initialize simulator with entry price of 960
    entry_price = 960
    simulator = EmergencyExitSimulator(entry_price)
    
    # Calculate position size
    position_size = simulator.calculate_position_size()
    print(f"\nEntry Setup for Rp {entry_price}:")
    print(f"Position Size: {position_size:,} shares")
    print(f"Total Position Value: Rp {(position_size * entry_price):,.2f}")
    print(f"Risk Amount: Rp {(simulator.initial_capital * simulator.risk_per_trade):,.2f}")
    
    print("\nExit Levels:")
    print("Stop Loss Levels:")
    for level, value in simulator.stop_levels.items():
        print(f"- {level}: Rp {value:.2f} ({((value/entry_price)-1)*100:.2f}%)")
    
    print("\nTake Profit Levels:")
    for level, value in simulator.take_profit_levels.items():
        print(f"- {level}: Rp {value:.2f} ({((value/entry_price)-1)*100:.2f}%)")
    
    print("\nEmergency Exit Levels:")
    print(f"- Price: Rp {simulator.emergency_levels['price_exit']:.2f} ({((simulator.emergency_levels['price_exit']/entry_price)-1)*100:.2f}%)")
    print(f"- RSI: {simulator.emergency_levels['rsi_exit']}")
    print(f"- Volume: {simulator.emergency_levels['volume_exit']}x average")
    
    # Run simulation
    print("\nRunning 1000 simulations...")
    results = simulator.run_simulation()
    
    # Calculate key metrics
    print("\nSimulation Results:")
    print(f"Average P&L: {results['pnl'].mean()*100:.2f}%")
    print(f"P&L Std Dev: {results['pnl'].std()*100:.2f}%")
    print("\nExit Type Distribution:")
    exit_dist = results['exit_type'].value_counts()
    for exit_type, count in exit_dist.items():
        print(f"- {exit_type}: {count/len(results)*100:.1f}%")
    print(f"\nAverage Exit Time: {results['exit_time'].mean():.0f} minutes")
    
    # Plot P&L distribution
    plt.figure(figsize=(12, 6))
    sns.histplot(data=results, x='pnl', bins=50)
    plt.title('P&L Distribution')
    plt.xlabel('Return %')
    plt.show()
    
    # Plot exit times distribution
    plt.figure(figsize=(12, 6))
    sns.histplot(data=results, x='exit_time', bins=50)
    plt.title('Exit Times Distribution')
    plt.xlabel('Minutes from Entry')
    plt.show()

if __name__ == "__main__":
    main() 