import json
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

class ITSECTradingPlan:
    """
    A class to create and manage a trading plan for ITSEC Asia (CYBR.JK).

    Attributes:
        entry_price (float): Entry price per share.
        lots (int): Number of lots (1 lot = 100 shares).
        position_size (int): Total number of shares in the position.
        data (dict): Technical and fundamental data loaded from a JSON file.
        tech_indicators (dict): Extracted technical indicators like RSI and price levels.
        ...
    """

    def __init__(self, json_file, entry_price, lots):
        """
        Initializes the trading plan by loading data and setting risk parameters.

        Args:
            json_file (str): Path to the JSON file containing technical data.
            entry_price (float): Entry price per share.
            lots (int): Number of lots (1 lot = 100 shares).
        """
        self.entry_price = entry_price
        self.lots = lots  # 1 lot = 100 shares
        self.position_size = lots * 100
        self.load_data(json_file)
        self.setup_risk_parameters()

    def load_data(self, json_file):
        """
        Loads technical data from a JSON file and extracts key indicators.

        Args:
            json_file (str): Path to the JSON file.

        Raises:
            FileNotFoundError: If the JSON file does not exist.
            JSONDecodeError: If the JSON file is not properly formatted.
        """
        try:
            with open(json_file, 'r') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            print(f"Error: The file {json_file} was not found.")
            raise
        except json.JSONDecodeError:
            print(f"Error: Failed to decode JSON from {json_file}.")
            raise

        # Extract key technical indicators
        self.tech_indicators = {
            'rsi': float(next(x['value'] for x in self.data['technical_rating_breakdown']['oscillator']['data']
                              if x['name'].startswith('Relative Strength'))),
            'current_price': self.data['last_close_price'],
            'ytd_high': self.data['all_time_price']['ytd_high']['price'],
            'ytd_low': self.data['all_time_price']['ytd_low']['price']
        }

    def setup_risk_parameters(self):
        """
        Sets up the capital, risk settings, and exit levels for the trading plan.
        """
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
        """
        Generates and prints the complete trading plan report.
        """
        self.print_entry_setup()
        self.print_technical_context()
        self.print_exit_strategy()
        self.print_risk_metrics()
        self.print_important_notes()

    def print_entry_setup(self):
        print("\n=== ENTRY SETUP ===")
        print(f"Entry Price: Rp {self.entry_price:,.2f}")
        print(f"Position Size: {self.position_size:,} shares ({self.lots} lots)")
        print(f"Position Value: Rp {(self.position_size * self.entry_price):,.2f}")
        print(f"Risk Amount: Rp {self.risk_amount:,.2f}")

    def print_technical_context(self):
        print("\n=== TECHNICAL CONTEXT ===")
        print(f"Current Market Price: Rp {self.tech_indicators['current_price']:,.2f}")
        print(f"Current RSI: {self.tech_indicators['rsi']:.1f}")
        print(f"YTD Range: Rp {self.tech_indicators['ytd_low']:,.2f} - Rp {self.tech_indicators['ytd_high']:,.2f}")

    def print_exit_strategy(self):
        print("\n=== EXIT STRATEGY ===")
        print("1. Take Profit Levels:")
        for level, price in self.exit_levels['take_profit'].items():
            shares = self.position_distribution[level]
            print(f"   {level.upper()}: Rp {price:,.2f} (+{((price / self.entry_price) - 1) * 100:.2f}%) "
                  f"- Exit {shares:,} shares")

        print("\n2. Stop Loss Management:")
        print(f"   Initial Stop: Rp {self.exit_levels['stop_loss']['initial']:,.2f} "
              f"(-{((1 - self.exit_levels['stop_loss']['initial'] / self.entry_price) * 100):.2f}%)")
        print(f"   Breakeven Stop: Rp {self.exit_levels['stop_loss']['breakeven']:,.2f} (moves after TP1)")
        print(f"   Trailing Stop: Rp {self.exit_levels['stop_loss']['trailing']:,.2f} "
              f"(-{((1 - self.exit_levels['stop_loss']['trailing'] / self.entry_price) * 100):.2f}%, activates after TP2)")

        print("\n3. Emergency Exit Conditions (Immediate Full Exit):")
        print(f"   - Price spikes to: Rp {self.exit_levels['emergency']['price']:,.2f}")
        print(f"   - RSI reaches: {self.exit_levels['emergency']['rsi']}")
        print(f"   - Volume spikes to: {self.exit_levels['emergency']['volume']}")

    def print_risk_metrics(self):
        print("\n=== RISK METRICS ===")
        print(f"Risk per Share: Rp {(self.entry_price - self.exit_levels['stop_loss']['initial']):,.2f}")
        print(f"Maximum Risk: Rp {self.risk_amount:,.2f} (1% of capital)")
        print(f"Risk:Reward Ratio: 1:1.5 at final target")

    def print_important_notes(self):
        print("\n=== IMPORTANT NOTES ===")
        print("- Average trade duration expected: 12-15 minutes")
        print("- Exit immediately if emergency conditions are met")
        print("- Strict adherence to stop loss levels is crucial")
        print("- No averaging down or position increase allowed")

def main():
    """
    Main function to get user inputs and create the trading plan.
    """
    while True:
        try:
            entry_price = float(input("Enter your entry price (e.g., 960): "))
            if entry_price <= 0:
                raise ValueError("Entry price must be positive.")
            break
        except ValueError as e:
            print(f"Invalid entry price: {e}")

    while True:
        try:
            lots = int(input("Enter number of lots (1 lot = 100 shares): "))
            if lots <= 0:
                raise ValueError("Lots must be positive.")
            break
        except ValueError as e:
            print(f"Invalid lots: {e}")

    # Create trading plan
    plan = ITSECTradingPlan('itsec-asia_full_dataset.json', entry_price, lots)
    plan.generate_report()

if __name__ == "__main__":
    main()
