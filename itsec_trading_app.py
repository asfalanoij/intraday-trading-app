import streamlit as st
import json
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class ITSECTradingApp:
    def __init__(self, json_file):
        self.load_data(json_file)
        
    def load_data(self, json_file):
        with open(json_file, 'r') as f:
            self.data = json.load(f)
        
        # Extract key scalping indicators
        self.tech_indicators = {
            # Primary Scalping Indicators
            'rsi': float(next(x['value'] for x in self.data['technical_rating_breakdown']['oscillator']['data'] 
                          if x['name'].startswith('Relative Strength'))),
            'stoch': float(next(x['value'] for x in self.data['technical_rating_breakdown']['oscillator']['data']
                           if x['name'].startswith('Stochastic'))),
            'momentum': float(next(x['value'] for x in self.data['technical_rating_breakdown']['oscillator']['data']
                            if x['name'].startswith('Momentum'))),
            
            # Key Moving Averages for Scalping
            'ema10': float(next(x['value'] for x in self.data['technical_rating_breakdown']['moving_average']['data']
                          if x['name'].startswith('Exponential Moving Average (10)'))),
            'ema20': float(next(x['value'] for x in self.data['technical_rating_breakdown']['moving_average']['data']
                          if x['name'].startswith('Exponential Moving Average (20)'))),
            
            # Price levels
            'current_price': self.data['last_close_price'],
            'ytd_high': self.data['all_time_price']['ytd_high']['price'],
            'ytd_low': self.data['all_time_price']['ytd_low']['price']
        }
        
        # Technical signals summary
        self.tech_summary = {
            'buy': self.data['technical_rating_breakdown']['summary']['buy'],
            'sell': self.data['technical_rating_breakdown']['summary']['sell'],
            'neutral': self.data['technical_rating_breakdown']['summary']['neutral']
        }
        
    def calculate_trading_plan(self, entry_price, lots):
        position_size = lots * 100
        initial_capital = 100_000_000  # Rp 100M
        risk_per_trade = 0.01  # 1% risk
        risk_amount = initial_capital * risk_per_trade
        
        # Exit levels
        exit_levels = {
            'stop_loss': {
                'initial': round(entry_price * 0.9708, 2),  # -2.92%
                'breakeven': entry_price,
                'trailing': round(entry_price * 0.985, 2)  # -1.50%
            },
            'take_profit': {
                'tp1': round(entry_price * 1.015, 2),  # +1.50%
                'tp2': round(entry_price * 1.029, 2),  # +2.90%
                'tp3': round(entry_price * 1.044, 2)   # +4.40%
            },
            'emergency': {
                'price': round(entry_price * 1.04, 2),  # +4.00%
                'rsi': 85,
                'volume': 2.0
            }
        }
        
        # Position distribution
        position_distribution = {
            'tp1': int(position_size * 0.4),  # 40% at TP1
            'tp2': int(position_size * 0.3),  # 30% at TP2
            'tp3': int(position_size * 0.3)   # 30% at TP3
        }
        
        return {
            'entry': {
                'price': entry_price,
                'size': position_size,
                'value': entry_price * position_size,
                'risk_amount': risk_amount
            },
            'exits': exit_levels,
            'distribution': position_distribution
        }

def main():
    st.set_page_config(page_title="ScalpingStrategy", layout="wide")
    
    # Custom CSS for responsive layout and better number visibility
    st.markdown("""
        <style>
        .stApp {
            max-width: 1600px;  /* Increased from 1200px */
            margin: 0 auto;
        }
        .main > div {
            padding: 1rem 1.5rem;  /* Increased padding */
        }
        .stMetric {
            padding: 0.5rem 0;
            min-width: 200px;  /* Minimum width for metrics */
        }
        /* Header sizes */
        .st-emotion-cache-1629p8f h1 {
            font-size: 2rem !important;
            margin-bottom: 1rem !important;
        }
        .st-emotion-cache-1629p8f h2 {
            font-size: 1.5rem !important;
            margin-bottom: 0.8rem !important;
        }
        .st-emotion-cache-1629p8f h3 {
            font-size: 1.2rem !important;
            margin-bottom: 0.6rem !important;
        }
        /* Metric values - prevent truncation */
        .st-emotion-cache-1629p8f .stMetric div[data-testid="stMetricValue"] {
            font-size: 1.8rem !important;
            font-weight: 600 !important;
            white-space: nowrap !important;
            overflow: visible !important;
            min-width: fit-content !important;
        }
        /* Metric labels */
        .st-emotion-cache-1629p8f .stMetric label {
            font-size: 0.9rem !important;
            white-space: nowrap !important;
        }
        /* Metric deltas */
        .st-emotion-cache-1629p8f .stMetric div[data-testid="stMetricDelta"] {
            font-size: 0.8rem !important;
            white-space: nowrap !important;
        }
        /* Make columns more responsive */
        .st-emotion-cache-1629p8f .row-widget.stHorizontalBlock {
            flex-wrap: wrap !important;
            gap: 1rem !important;
        }
        /* Ensure charts are responsive */
        .js-plotly-plot {
            width: 100% !important;
        }
        /* Sidebar adjustments */
        .st-emotion-cache-1629p8f .st-emotion-cache-16txtl3 {
            padding: 2rem 1rem;
        }
        /* Better text readability */
        p, li {
            font-size: 0.9rem !important;
            line-height: 1.5 !important;
        }
        /* Info box styling */
        .stInfo {
            padding: 1rem !important;
            margin: 1rem 0 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize app
    app = ITSECTradingApp('itsec-asia_full_dataset.json')
    
    # Sidebar inputs
    with st.sidebar:
        st.header("Trading Parameters")
        entry_price = st.number_input("Entry Price (Rp)", 
                                    min_value=100.0, 
                                    max_value=2000.0, 
                                    value=930.0,
                                    step=0.5,
                                    format="%.2f")  # Added format specification
        
        lots = st.number_input("Number of Lots", 
                             min_value=1, 
                             max_value=100, 
                             value=8)
        
        # Add image with error handling
        try:
            st.image("pic/rudypic.jpg", use_container_width=True)
        except Exception as e:
            st.info("📸 Profile picture placeholder")
    
    # Calculate trading plan
    plan = app.calculate_trading_plan(entry_price, lots)
    
    # Main content - Responsive layout
    col1, col2 = st.columns([3, 1])  # Adjusted ratio for better space utilization
    
    with col1:
        st.title("ITSEC ASIA (CYBR.JK) Scalping Plan")
        st.caption(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Key Scalping Indicators with more space
        st.subheader("Scalping Indicators")
        ind_cols = st.columns(4)
        with ind_cols[0]:
            st.metric("RSI", f"{app.tech_indicators['rsi']:.1f}", 
                     "Overbought > 70" if app.tech_indicators['rsi'] > 70 else "Oversold < 30" if app.tech_indicators['rsi'] < 30 else "Neutral")
        with ind_cols[1]:
            st.metric("Stochastic", f"{app.tech_indicators['stoch']:.1f}")
        with ind_cols[2]:
            st.metric("EMA10", f"Rp {app.tech_indicators['ema10']:,.2f}")
        with ind_cols[3]:
            st.metric("EMA20", f"Rp {app.tech_indicators['ema20']:,.2f}")
        
        # Entry and Risk with better spacing
        st.subheader("Position Setup")
        setup_cols = st.columns(4)
        with setup_cols[0]:
            st.metric("Entry Price", f"Rp {plan['entry']['price']:,.2f}")
        with setup_cols[1]:
            st.metric("Position", f"{plan['entry']['size']:,} shares")
        with setup_cols[2]:
            st.metric("Value", f"Rp {plan['entry']['value']:,.2f}")
        with setup_cols[3]:
            st.metric("Risk", f"Rp {plan['entry']['risk_amount']:,.2f}")
    
    with col2:
        # Signal Summary
        signals = pd.DataFrame({
            'Signal': ['Buy', 'Sell', 'Neutral'],
            'Count': [app.tech_summary['buy'], app.tech_summary['sell'], app.tech_summary['neutral']]
        })
        fig = go.Figure(data=[go.Bar(
            x=signals['Signal'],
            y=signals['Count'],
            marker_color=['green', 'red', 'gray']
        )])
        fig.update_layout(
            title="Signal Summary",
            height=200,
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Exit Strategy
    st.header("Exit Strategy")
    
    # Take Profit and Stop Loss in two columns
    exit_col1, exit_col2 = st.columns(2)
    
    with exit_col1:
        st.subheader("Take Profit Levels")
        for level, price in plan['exits']['take_profit'].items():
            shares = plan['distribution'][level]
            gain_pct = ((price/entry_price)-1)*100
            st.metric(
                f"{level.upper()}", 
                f"Rp {price:,.2f}",
                f"+{gain_pct:.2f}% ({shares:,} shares ≈ {shares/100:.1f} lots)"
            )
    
    with exit_col2:
        st.subheader("Stop Loss Management")
        for level, price in plan['exits']['stop_loss'].items():
            loss_pct = ((price/entry_price)-1)*100
            st.metric(
                level.title(), 
                f"Rp {price:,.2f}",
                f"{loss_pct:.2f}%"
            )
    
    # Emergency Exits
    st.subheader("Emergency Exit Conditions")
    emg_cols = st.columns(3)
    with emg_cols[0]:
        st.metric("Price Spike", f"Rp {plan['exits']['emergency']['price']:,.2f}")
    with emg_cols[1]:
        st.metric("RSI Level", plan['exits']['emergency']['rsi'])
    with emg_cols[2]:
        st.metric("Volume Spike", f"{plan['exits']['emergency']['volume']}x avg")
    
    # Visualization adjustments
    st.subheader("Price Levels")
    fig = go.Figure()
    
    # Add price levels with better formatting
    levels = {
        'Entry': plan['entry']['price'],
        'TP1': plan['exits']['take_profit']['tp1'],
        'TP2': plan['exits']['take_profit']['tp2'],
        'TP3': plan['exits']['take_profit']['tp3'],
        'Initial Stop': plan['exits']['stop_loss']['initial'],
        'Trailing Stop': plan['exits']['stop_loss']['trailing'],
        'Emergency Exit': plan['exits']['emergency']['price']
    }
    
    colors = {
        'Entry': 'yellow',
        'TP1': 'green',
        'TP2': 'green',
        'TP3': 'green',
        'Initial Stop': 'red',
        'Trailing Stop': 'orange',
        'Emergency Exit': 'purple'
    }
    
    for level_name, price in levels.items():
        fig.add_hline(
            y=price,
            line_dash="dash",
            line_color=colors[level_name],
            annotation_text=f"{level_name}: Rp {price:,.2f}",
            annotation_position="right"
        )
    
    # Add current price range
    fig.add_hrect(
        y0=app.tech_indicators['ytd_low'],
        y1=app.tech_indicators['ytd_high'],
        fillcolor="lightgray",
        opacity=0.2,
        line_width=0
    )
    
    fig.update_layout(
        title="Trading Levels",
        yaxis_title="Price (Rp)",
        showlegend=False,
        height=500,  # Increased height
        margin=dict(l=40, r=120, t=40, b=40),  # Adjusted margins
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Key Reminders with better formatting
    st.info("""
    **Key Trading Rules:**
    • Average trade duration: 12-15 minutes
    • Move stop to breakeven after TP1
    • Use 1.5% trailing stop after TP2
    • Risk:Reward = 1:1.5 at final target
    • No averaging down allowed
    """)

if __name__ == "__main__":
    main() 