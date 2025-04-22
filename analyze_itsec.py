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

def load_and_analyze_data():
    # Load ITSEC Asia data
    with open('itsec-asia_full_dataset.json', 'r') as f:
        data = json.load(f)

    # Extract key metrics
    print("\nCompany Overview:")
    print(f"Symbol: {data['symbol']}")
    print(f"Company Name: {data['company_name']}")
    print(f"Market Cap: Rp {data['market_cap']:,.2f}")
    print(f"Current Price: Rp {data['last_close_price']}")
    print(f"YTD Change: {data['daily_close_change']*100:.2f}%")

    # Technical Analysis
    tech = data['technical_rating_breakdown']
    print("\nTechnical Analysis Summary:")
    print(f"Buy Signals: {tech['summary']['buy']}")
    print(f"Sell Signals: {tech['summary']['sell']}")
    print(f"Neutral Signals: {tech['summary']['neutral']}")

    # Moving Averages Analysis
    ma = tech['moving_average']['data']
    print("\nMoving Averages:")
    for indicator in ma:
        print(f"{indicator['name']}: {indicator['value']} ({indicator['action']})")

    # Oscillator Analysis
    osc = tech['oscillator']['data']
    print("\nOscillators:")
    for indicator in osc:
        print(f"{indicator['name']}: {indicator['value']} ({indicator['action']})")

    # Risk Analysis
    print("\nRisk Analysis:")
    print(f"52-week Range: Rp {data['all_time_price']['52_w_low']['price']} - Rp {data['all_time_price']['52_w_high']['price']}")
    print(f"YTD Range: Rp {data['all_time_price']['ytd_low']['price']} - Rp {data['all_time_price']['ytd_high']['price']}")

    # Calculate Emergency Exit Levels
    current_price = data['last_close_price']
    emergency_levels = {
        'price_exit': current_price * 1.04,  # 4% above current
        'rsi_exit': 85,
        'volume_exit': 2.0,  # 2x average volume
        'stop_loss': current_price * 1.0292  # 2.92% stop loss
    }

    print("\nEmergency Exit Levels:")
    print(f"Price Exit: Rp {emergency_levels['price_exit']:.2f}")
    print(f"RSI Exit: {emergency_levels['rsi_exit']}")
    print(f"Volume Exit: {emergency_levels['volume_exit']}x average")
    print(f"Stop Loss: Rp {emergency_levels['stop_loss']:.2f}")

    # Position Sizing
    initial_capital = 100_000_000  # Rp 100M
    risk_per_trade = 0.01  # 1%
    risk_amount = initial_capital * risk_per_trade
    stop_loss_points = emergency_levels['stop_loss'] - current_price
    position_size = int(risk_amount / stop_loss_points)

    print("\nPosition Sizing:")
    print(f"Maximum Position Size: {position_size:,} shares")
    print(f"Total Position Value: Rp {(position_size * current_price):,.2f}")
    print(f"Risk Amount: Rp {risk_amount:,.2f}")

    # Take Profit Levels
    take_profits = [
        {'level': 1, 'percent': -0.03, 'size': 0.4},
        {'level': 2, 'percent': -0.05, 'size': 0.3},
        {'level': 3, 'percent': -0.10, 'size': 0.3}
    ]

    print("\nTake Profit Levels:")
    for tp in take_profits:
        price = current_price * (1 + tp['percent'])
        shares = int(position_size * tp['size'])
        print(f"T{tp['level']}: Rp {price:.2f} ({tp['size']*100}% = {shares:,} shares)")

    # Plot Technical Indicators
    plt.figure(figsize=(15, 10))
    
    # Plot 1: Moving Averages
    plt.subplot(2, 1, 1)
    ma_values = [float(i['value']) for i in ma]
    ma_names = [i['name'].split('(')[0].strip() for i in ma]
    plt.bar(ma_names, ma_values)
    plt.title('Moving Averages Analysis')
    plt.xticks(rotation=45)
    plt.axhline(y=current_price, color='r', linestyle='--', label='Current Price')
    plt.legend()

    # Plot 2: Oscillators
    plt.subplot(2, 1, 2)
    osc_values = [float(i['value']) for i in osc if i['value'] != '']
    osc_names = [i['name'].split('(')[0].strip() for i in osc if i['value'] != '']
    plt.bar(osc_names, osc_values)
    plt.title('Oscillator Analysis')
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.show()

    return data, emergency_levels, position_size

if __name__ == "__main__":
    data, emergency_levels, position_size = load_and_analyze_data() 