# Intraday Trading App

A Streamlit-based application for intraday trading analysis and scalping strategy planning.

## Features

- Real-time technical indicator analysis
- Dynamic trading plan calculation
- Interactive price level visualization
- Position sizing and risk management
- Emergency exit conditions monitoring
- Responsive design optimized for MacOS

## Technical Indicators

- RSI (Relative Strength Index)
- Stochastic Oscillator
- EMA (10 & 20 periods)
- Momentum
- Signal Summary (Buy/Sell/Neutral)

## Trading Rules

- Average trade duration: 12-15 minutes
- Move stop to breakeven after TP1
- Use 1.5% trailing stop after TP2
- Risk:Reward = 1:1.5 at final target
- No averaging down allowed

## Installation

```bash
# Clone the repository
git clone https://github.com/asfalanoij/intraday-trading-app.git

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run intraday_trading_app.py
```

## Requirements

Create a requirements.txt file with the following dependencies:

```
streamlit>=1.24.0
pandas>=1.5.0
numpy>=1.23.0
plotly>=5.13.0
```

## Usage

1. Place your JSON dataset files in the root directory
2. Run the Streamlit app
3. Input your trading parameters
4. Monitor technical indicators
5. Follow the trading plan and exit strategy

## Directory Structure

```
intraday-trading-app/
├── README.md
├── requirements.txt
├── intraday_trading_app.py
├── static/
│   └── styles.css
└── pic/
    └── rudypic.jpg
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/) 