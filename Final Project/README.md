
# Trading Strategy Analysis

This repository contains a Jupyter Notebook that implements a comprehensive trading strategy using various technical indicators and machine learning models. The primary focus is on optimizing trade execution and maximizing profits through algorithmic trading techniques.

## Features

1. **Technical Indicators**:
   - Moving Averages (Short SMA, Long SMA)
   - Relative Strength Index (RSI)
   - Moving Average Convergence Divergence (MACD)
   - Support and Resistance Levels

2. **Trading Strategy**:
   - Buy Signal: Check for bullish engulfing or hammer candles near by the support lines  
   - Sell Signal: Check for bearish engulfing or shooting star candles near by the resistance lines 
   - Trailing Stop Loss and Profit Targets for risk management

3. **Machine Learning**:
   - LSTM Model for predictive analysis
   - Hyperparameter tuning for optimal model performance

4. **Data Handling**:
   - Web scraping for real-time financial data
   - Integration with brokerage firm APIs for automated trade execution

## Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Jayasuryan0821/AlgoTrading-on-Kite.git
   cd trading-strategy
   ```

2. **Install the required packages**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Jupyter Notebook**:
   ```bash
   jupyter notebook final.ipynb
   ```

## Usage

- **Web Scraping**: Fetch real-time data using Selenium WebDriver.
- **Data Preprocessing**: Clean and prepare data for analysis.
- **Technical Analysis**: Apply technical indicators to identify buy and sell signals.
- **Trade Execution**: Automatically place trades based on identified signals.
- **Model Training**: Train and evaluate the LSTM model for predictive analysis.

## Results

The notebook provides detailed logs and visualizations for each step, including:
- Buy and sell signals with corresponding prices and dates
- Profit and loss calculations for each trade
- Model accuracy and performance metrics

