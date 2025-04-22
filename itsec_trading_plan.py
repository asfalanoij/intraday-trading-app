import json
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

class ITSECTradingPlan:
    def __init__(self, json_file, entry_price, lots):
        self.entry_price = entry_price
        self.lots = lots  # 1 lot = 100 shares
        self.position_size = lots * 100
        self.load_data(json_file)
        self.setup_risk_parameters()
        
    def load_data(self, json_file):
        with open(json_file, 'r') as f:
            self.data = json.load(f)
        
        # Extract key technical indicators
        self.tech_indicators = {
            'rsi': float(next(x['value'] for x in self.data['technical_rating_breakdown']['oscillator']['data'] 
                          if x['name'].startswith('Relative Strength'))),
            'current_price': self.data['last_close_price'],
            'ytd_high': self.data['all_time_price']['ytd_high']['price'],
            'ytd_low': self.data['all_time_price']['ytd_low']['price']
        }
        
    def setup_risk_parameters(self):
        # Capital and risk settings
        self.initial_capital = 100_000_000  # Rp 100M
        self.risk_per_trade = 0.01  # 1% risk
        self.risk_amount = self.initial_capital * self.risk_per_trade
        
        # Calculate exit levels
        self.exit_levels = {
            'stop_loss': {
                'initial': round(self.entry_price * 0.9708, 2),  # -2.92%
                'breakeven': self.entry_price,
                'trailing': round(self.entry_price * 0.985, 2)  # -1.50%
            },
            'take_profit': {
                'tp1': round(self.entry_price * 1.015, 2),  # +1.50%
                'tp2': round(self.entry_price * 1.029, 2),  # +2.90%
                'tp3': round(self.entry_price * 1.044, 2)   # +4.40%
            },
            'emergency': {
                'price': round(self.entry_price * 1.04, 2),  # +4.00%
                'rsi': 85,
                'volume': '2.0x average'
            }
        }
        
        # Position distribution
        self.position_distribution = {
            'tp1': int(self.position_size * 0.4),  # 40% at TP1
            'tp2': int(self.position_size * 0.3),  # 30% at TP2
            'tp3': int(self.position_size * 0.3)   # 30% at TP3
        }
        
    def generate_report(self):
        print("\n=== ITSEC ASIA (CYBR.JK) TRADING PLAN ===")
        print(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n=== ENTRY SETUP ===")
        print(f"Entry Price: Rp {self.entry_price:,.2f}")
        print(f"Position Size: {self.position_size:,} shares ({self.lots} lots)")
        print(f"Position Value: Rp {(self.position_size * self.entry_price):,.2f}")
        print(f"Risk Amount: Rp {self.risk_amount:,.2f}")
        
        print("\n=== TECHNICAL CONTEXT ===")
        print(f"Current Market Price: Rp {self.tech_indicators['current_price']:,.2f}")
        print(f"Current RSI: {self.tech_indicators['rsi']:.1f}")
        print(f"YTD Range: Rp {self.tech_indicators['ytd_low']:,.2f} - Rp {self.tech_indicators['ytd_high']:,.2f}")
        
        print("\n=== EXIT STRATEGY ===")
        print("1. Take Profit Levels:")
        for level, price in self.exit_levels['take_profit'].items():
            shares = self.position_distribution[level]
            print(f"   {level.upper()}: Rp {price:,.2f} (+{((price/self.entry_price)-1)*100:.2f}%) "
                  f"- Exit {shares:,} shares")
        
        print("\n2. Stop Loss Management:")
        print(f"   Initial Stop: Rp {self.exit_levels['stop_loss']['initial']:,.2f} "
              f"(-{((1-self.exit_levels['stop_loss']['initial']/self.entry_price)*100):.2f}%)")
        print(f"   Breakeven Stop: Rp {self.exit_levels['stop_loss']['breakeven']:,.2f} "
              f"(moves after TP1)")
        print(f"   Trailing Stop: Rp {self.exit_levels['stop_loss']['trailing']:,.2f} "
              f"(-{((1-self.exit_levels['stop_loss']['trailing']/self.entry_price)*100):.2f}%, activates after TP2)")
        
        print("\n3. Emergency Exit Conditions (Immediate Full Exit):")
        print(f"   - Price spikes to: Rp {self.exit_levels['emergency']['price']:,.2f}")
        print(f"   - RSI reaches: {self.exit_levels['emergency']['rsi']}")
        print(f"   - Volume spikes to: {self.exit_levels['emergency']['volume']}")
        
        print("\n=== EXECUTION SEQUENCE ===")
        print("1. Entry Phase:")
        print(f"   - Enter full position at Rp {self.entry_price:,.2f}")
        print("   - Set initial stop loss immediately")
        
        print("\n2. Management Phase:")
        print("   - After TP1: Move stop loss to breakeven")
        print("   - After TP2: Activate trailing stop")
        print("   - Monitor emergency exit conditions continuously")
        
        print("\n=== RISK METRICS ===")
        print(f"Risk per Share: Rp {(self.entry_price - self.exit_levels['stop_loss']['initial']):,.2f}")
        print(f"Maximum Risk: Rp {self.risk_amount:,.2f} (1% of capital)")
        print(f"Risk:Reward Ratio: 1:1.5 at final target")
        
        print("\n=== IMPORTANT NOTES ===")
        print("- Average trade duration expected: 12-15 minutes")
        print("- Exit immediately if emergency conditions are met")
        print("- Strict adherence to stop loss levels is crucial")
        print("- No averaging down or position increase allowed")

def main():
    # Get user inputs
    entry_price = float(input("Enter your entry price (e.g., 960): "))
    lots = int(input("Enter number of lots (1 lot = 100 shares): "))
    
    # Create trading plan
    plan = ITSECTradingPlan('itsec-asia_full_dataset.json', entry_price, lots)
    plan.generate_report()

if __name__ == "__main__":
    main() 