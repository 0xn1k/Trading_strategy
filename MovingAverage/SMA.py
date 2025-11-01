import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime, timedelta

def calculate_sma(prices, window):
    """
    Calculate Simple Moving Average

    Args:
        prices: Array or Series of prices
        window: Number of periods for moving average

    Returns:
        pandas Series with SMA values
    """
    return pd.Series(prices).rolling(window=window, min_periods=1).mean()

def calculate_multiple_sma(data, windows=[20, 50, 200]):
    """
    Calculate multiple SMAs for given windows

    Args:
        data: DataFrame with price data
        windows: List of window periods

    Returns:
        DataFrame with original data and SMA columns
    """
    result = data.copy()

    for window in windows:
        result[f'SMA_{window}'] = calculate_sma(data['Close'], window)

    return result

def detect_crossover_signals(data, short_sma='SMA_20', long_sma='SMA_50'):
    """
    Detect golden cross and death cross signals

    Args:
        data: DataFrame with SMA columns
        short_sma: Column name for short-term SMA
        long_sma: Column name for long-term SMA

    Returns:
        DataFrame with signal columns added
    """
    data = data.copy()

    # Calculate crossover signals
    data['Signal'] = 0
    data['Signal'][data[short_sma] > data[long_sma]] = 1  # Golden cross
    data['Signal'][data[short_sma] < data[long_sma]] = -1  # Death cross

    # Find crossover points
    data['Position'] = data['Signal'].diff()
    data['Golden_Cross'] = (data['Position'] == 2)  # From -1 to 1
    data['Death_Cross'] = (data['Position'] == -2)   # From 1 to -1

    return data

def load_stock_data(symbol, period='1y'):
    """
    Load stock data using yfinance

    Args:
        symbol: Stock ticker symbol
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

    Returns:
        DataFrame with stock data
    """
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period)
        return data
    except Exception as e:
        print(f"Error loading data for {symbol}: {e}")
        return None

def analyze_sma_performance(data, short_sma='SMA_20', long_sma='SMA_50'):
    """
    Analyze SMA trading strategy performance

    Args:
        data: DataFrame with price and SMA data
        short_sma: Short-term SMA column
        long_sma: Long-term SMA column

    Returns:
        Dictionary with performance metrics
    """
    signals_data = detect_crossover_signals(data, short_sma, long_sma)

    # Calculate returns
    signals_data['Returns'] = signals_data['Close'].pct_change()
    signals_data['Strategy_Returns'] = signals_data['Signal'].shift(1) * signals_data['Returns']

    # Performance metrics
    total_return = (1 + signals_data['Strategy_Returns']).cumprod().iloc[-1] - 1
    buy_hold_return = (signals_data['Close'].iloc[-1] / signals_data['Close'].iloc[0]) - 1

    # Count signals
    golden_crosses = signals_data['Golden_Cross'].sum()
    death_crosses = signals_data['Death_Cross'].sum()

    return {
        'total_return': total_return,
        'buy_hold_return': buy_hold_return,
        'golden_crosses': golden_crosses,
        'death_crosses': death_crosses,
        'win_rate': len(signals_data[signals_data['Strategy_Returns'] > 0]) / len(signals_data[signals_data['Strategy_Returns'] != 0])
    }

def plot_sma_analysis(data, symbol, sma_windows=[20, 50, 200]):
    """
    Plot price data with SMAs and trading signals

    Args:
        data: DataFrame with price and SMA data
        symbol: Stock symbol for title
        sma_windows: List of SMA windows to plot
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), height_ratios=[3, 1])

    # Plot price and SMAs
    ax1.plot(data.index, data['Close'], label='Close Price', linewidth=2)

    colors = ['orange', 'red', 'purple']
    for i, window in enumerate(sma_windows):
        if f'SMA_{window}' in data.columns:
            ax1.plot(data.index, data[f'SMA_{window}'],
                    label=f'SMA {window}', alpha=0.7, color=colors[i % len(colors)])

    # Mark crossover signals
    if 'Golden_Cross' in data.columns:
        golden_cross_points = data[data['Golden_Cross']]
        ax1.scatter(golden_cross_points.index, golden_cross_points['Close'],
                   color='green', marker='^', s=100, label='Golden Cross', zorder=5)

    if 'Death_Cross' in data.columns:
        death_cross_points = data[data['Death_Cross']]
        ax1.scatter(death_cross_points.index, death_cross_points['Close'],
                   color='red', marker='v', s=100, label='Death Cross', zorder=5)

    ax1.set_title(f'{symbol} - SMA Analysis')
    ax1.set_ylabel('Price')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot trading signals
    if 'Signal' in data.columns:
        ax2.plot(data.index, data['Signal'], label='Trading Signal', color='blue')
        ax2.fill_between(data.index, 0, data['Signal'], alpha=0.3)
        ax2.set_ylabel('Signal')
        ax2.set_xlabel('Date')
        ax2.set_ylim(-1.5, 1.5)
        ax2.grid(True, alpha=0.3)
        ax2.legend()

    plt.tight_layout()
    # Save the plot as JPEG
    filename = f"{symbol.replace('^', '').replace('.', '_')}_sma_analysis.jpg"
    plt.savefig(filename, format='jpg', dpi=300, bbox_inches='tight')
    print(f"Graph saved as: {filename}")
    plt.show()

if __name__ == "__main__":
    # Example usage - Indian stocks
    symbol = "^NSEI"  # Nifty 50 Index
    print(f"Analyzing SMA strategy for {symbol}")

    # Load data
    data = load_stock_data(symbol, period='2y')

    if data is not None:
        # Calculate SMAs
        data_with_sma = calculate_multiple_sma(data, windows=[20, 50, 200])

        # Detect signals
        data_with_signals = detect_crossover_signals(data_with_sma, 'SMA_20', 'SMA_50')

        # Analyze performance
        performance = analyze_sma_performance(data_with_signals, 'SMA_20', 'SMA_50')

        print("\nPerformance Metrics:")
        print(f"Strategy Return: {performance['total_return']:.2%}")
        print(f"Buy & Hold Return: {performance['buy_hold_return']:.2%}")
        print(f"Golden Crosses: {performance['golden_crosses']}")
        print(f"Death Crosses: {performance['death_crosses']}")
        print(f"Win Rate: {performance['win_rate']:.2%}")

        # Plot analysis
        plot_sma_analysis(data_with_signals, symbol)

        # Display recent data
        print("\nRecent SMA data:")
        print(data_with_signals[['Close', 'SMA_20', 'SMA_50', 'SMA_200', 'Signal']].tail(10))