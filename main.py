import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime, timedelta


def load_stock_data(symbol, period='1y', interval='1d'): 
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period, interval=interval)
        return data
    except Exception as e:
        print(f"Error loading data for {symbol}: {e}")
        return pd.DataFrame()       

if __name__ == "__main__":
      # Example usage - Indian stocks
    symbol = "^NSEI"  # Nifty 50 Index
    print(f"Analyzing SMA strategy for {symbol}")

    # Load data
    data = load_stock_data(symbol, period='2y')
    print(data.head())