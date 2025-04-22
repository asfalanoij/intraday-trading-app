import streamlit as st
import json
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class MultiTradingApp:
    def __init__(self, config_file):
        # Load emergency exit configuration
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        # Available datasets
        self.datasets = {
            'CENT.JK': 'centratama-t_full_dataset.json',
            'DMMX.JK': 'digital-medi_full_dataset.json'
        }
        
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

        # Company info
        self.company_info = {
            'symbol': self.data['symbol'],
            'name': self.data['company_name'],
            'market_cap': self.data['market_cap'],
            'sector': self.data['sector'],
            'industry': self.data['industry']
        }
        
    def calculate_trading_plan(self, entry_price, lots):
        position_size = lots * 100
        initial_capital = self.config['RISK_PARAMETERS']['INITIAL_CAPITAL']
        risk_per_trade = self.config['RISK_PARAMETERS']['RISK_PER_TRADE']
        risk_amount = initial_capital * risk_per_trade
        
        # Exit levels
        exit_levels = {
            'stop_loss': {
                'initial': round(entry_price * (1 - self.config['RISK_PARAMETERS']['STOP_LOSS_PERCENT']), 2),
                'breakeven': entry_price,
                'trailing': round(entry_price * 0.985, 2)  # -1.50%
            },
            'take_profit': {
                'tp1': round(entry_price * (1 + abs(self.config['RISK_PARAMETERS']['TAKE_PROFIT_LEVELS'][0]['percent'])), 2),
                'tp2': round(entry_price * (1 + abs(self.config['RISK_PARAMETERS']['TAKE_PROFIT_LEVELS'][1]['percent'])), 2),
                'tp3': round(entry_price * (1 + abs(self.config['RISK_PARAMETERS']['TAKE_PROFIT_LEVELS'][2]['percent'])), 2)
            },
            'emergency': {
                'price': round(entry_price * 1.04, 2),  # +4.00%
                'rsi': self.config['RSI_THRESHOLD'],
                'volume': self.config['VOLUME_MULTIPLIER']
            }
        }
        
        # Position distribution based on config
        position_distribution = {
            'tp1': int(position_size * self.config['RISK_PARAMETERS']['TAKE_PROFIT_LEVELS'][0]['position_size']),
            'tp2': int(position_size * self.config['RISK_PARAMETERS']['TAKE_PROFIT_LEVELS'][1]['position_size']),
            'tp3': int(position_size * self.config['RISK_PARAMETERS']['TAKE_PROFIT_LEVELS'][2]['position_size'])
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
    st.set_page_config(page_title="MultiScalpingStrategy", layout="wide")
    
    # Custom CSS for compact layout
    st.markdown("""
        <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .main > div {
            padding: 0.7rem 0.7rem;
        }
        .stMetric {
            padding: 0.3rem 0;
        }
        .st-emotion-cache-1629p8f h1 {
            font-size: 1.4rem !important;
        }
        .st-emotion-cache-1629p8f h2 {
            font-size: 1.1rem !important;
        }
        .st-emotion-cache-1629p8f h3 {
            font-size: 0.9rem !important;
        }
        .st-emotion-cache-1629p8f p {
            font-size: 0.7rem !important;
        }
        .st-emotion-cache-1629p8f .stMetric label {
            font-size: 0.6rem !important;
        }
        .st-emotion-cache-1629p8f .stMetric div[data-testid="stMetricValue"] {
            font-size: 2.5rem !important;
        }
        .st-emotion-cache-1629p8f .stMetric div[data-testid="stMetricDelta"] {
            font-size: 0.6rem !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize app with config
    app = MultiTradingApp('emergency_exit_config.json')
    
    # Sidebar inputs
    with st.sidebar:
        selected_stock = st.selectbox(
            "Select Stock",
            options=list(app.datasets.keys()),
            format_func=lambda x: f"{x}"
        )
        
        # Load selected dataset
        app.load_data(app.datasets[selected_stock])
        
        st.header("Trading Parameters")
        entry_price = st.number_input("Entry Price (Rp)", 
                                    min_value=100.0, 
                                    max_value=2000.0, 
                                    value=float(app.tech_indicators['current_price']),
                                    step=0.5)
        
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
    
    # Main content - Compact layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.title(f"{app.company_info['name']} ({app.company_info['symbol']}) Scalping Plan")
        st.caption(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Company Info
        st.markdown(f"""
        **Sector:** {app.company_info['sector']}  
        **Industry:** {app.company_info['industry']}  
        **Market Cap:** Rp {app.company_info['market_cap']:,.0f}
        """)
        
        # Key Scalping Indicators
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
        
        # Entry and Risk
        st.subheader("Position Setup")
        setup_cols = st.columns(4)
        with setup_cols[0]:
            st.metric("Entry Price", f"Rp {plan['entry']['price']:,.2f}")
        with setup_cols[1]:
            st.metric("Position", f"{plan['entry']['size']:,} shares ≈ {plan['entry']['size']/100:.1f} lots")
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
    
    # Visualization
    st.subheader("Price Levels")
    
    # Create price levels chart
    fig = go.Figure()
    
    # Add price levels
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
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Key Reminders in a compact box
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