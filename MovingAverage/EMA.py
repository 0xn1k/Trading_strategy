import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

def calculate_ema(prices, window):
    """
    Calculate Exponential Moving Average

    Args:
        prices: Array or Series of prices
        window: Number of periods for EMA

    Returns:
        pandas Series with EMA values
    """
    return pd.Series(prices).ewm(span=window, adjust=False).mean()

def calculate_multiple_ema(data, windows=[12, 26, 50]):
    """
    Calculate multiple EMAs for given windows

    Args:
        data: DataFrame with price data
        windows: List of window periods

    Returns:
        DataFrame with original data and EMA columns
    """
    result = data.copy()

    for window in windows:
        result[f'EMA_{window}'] = calculate_ema(data['Close'], window)

    return result

def calculate_macd(data, fast_period=12, slow_period=26, signal_period=9):
    """
    Calculate MACD (Moving Average Convergence Divergence)

    Args:
        data: DataFrame with price data
        fast_period: Fast EMA period
        slow_period: Slow EMA period
        signal_period: Signal line EMA period

    Returns:
        DataFrame with MACD columns added
    """
    result = data.copy()

    # Calculate MACD line
    ema_fast = calculate_ema(data['Close'], fast_period)
    ema_slow = calculate_ema(data['Close'], slow_period)
    result['MACD'] = ema_fast - ema_slow

    # Calculate Signal line
    result['MACD_Signal'] = calculate_ema(result['MACD'], signal_period)

    # Calculate MACD Histogram
    result['MACD_Histogram'] = result['MACD'] - result['MACD_Signal']

    return result

def detect_ema_crossover_signals(data, short_ema='EMA_12', long_ema='EMA_26'):
    """
    Detect EMA crossover signals

    Args:
        data: DataFrame with EMA columns
        short_ema: Column name for short-term EMA
        long_ema: Column name for long-term EMA

    Returns:
        DataFrame with signal columns added
    """
    data = data.copy()

    # Calculate crossover signals
    data['EMA_Signal'] = 0
    data['EMA_Signal'][data[short_ema] > data[long_ema]] = 1  # Bullish
    data['EMA_Signal'][data[short_ema] < data[long_ema]] = -1  # Bearish

    # Find crossover points
    data['EMA_Position'] = data['EMA_Signal'].diff()
    data['EMA_Golden_Cross'] = (data['EMA_Position'] == 2)
    data['EMA_Death_Cross'] = (data['EMA_Position'] == -2)

    return data

def detect_macd_signals(data):
    """
    Detect MACD trading signals

    Args:
        data: DataFrame with MACD data

    Returns:
        DataFrame with MACD signal columns added
    """
    data = data.copy()

    # MACD Line above/below Signal Line
    data['MACD_Buy_Signal'] = (data['MACD'] > data['MACD_Signal']) & (data['MACD'].shift(1) <= data['MACD_Signal'].shift(1))
    data['MACD_Sell_Signal'] = (data['MACD'] < data['MACD_Signal']) & (data['MACD'].shift(1) >= data['MACD_Signal'].shift(1))

    # MACD Zero Line Crossover
    data['MACD_Zero_Cross_Up'] = (data['MACD'] > 0) & (data['MACD'].shift(1) <= 0)
    data['MACD_Zero_Cross_Down'] = (data['MACD'] < 0) & (data['MACD'].shift(1) >= 0)

    return data

def load_nse_data(symbol, period='1y'):
    """
    Load NSE stock data using yfinance

    Args:
        symbol: Stock ticker symbol (add .NS for NSE stocks)
        period: Time period

    Returns:
        DataFrame with stock data
    """
    try:
        if not symbol.endswith('.NS') and not symbol.startswith('^'):
            symbol = symbol + '.NS'

        stock = yf.Ticker(symbol)
        data = stock.history(period=period)
        return data
    except Exception as e:
        print(f"Error loading data for {symbol}: {e}")
        return None

def analyze_ema_performance(data, short_ema='EMA_12', long_ema='EMA_26'):
    """
    Analyze EMA trading strategy performance

    Args:
        data: DataFrame with price and EMA data
        short_ema: Short-term EMA column
        long_ema: Long-term EMA column

    Returns:
        Dictionary with performance metrics
    """
    signals_data = detect_ema_crossover_signals(data, short_ema, long_ema)

    # Calculate returns
    signals_data['Returns'] = signals_data['Close'].pct_change()
    signals_data['EMA_Strategy_Returns'] = signals_data['EMA_Signal'].shift(1) * signals_data['Returns']

    # Performance metrics
    total_return = (1 + signals_data['EMA_Strategy_Returns']).cumprod().iloc[-1] - 1
    buy_hold_return = (signals_data['Close'].iloc[-1] / signals_data['Close'].iloc[0]) - 1

    # Count signals
    golden_crosses = signals_data['EMA_Golden_Cross'].sum()
    death_crosses = signals_data['EMA_Death_Cross'].sum()

    # Calculate volatility
    strategy_volatility = signals_data['EMA_Strategy_Returns'].std() * (252 ** 0.5)
    buy_hold_volatility = signals_data['Returns'].std() * (252 ** 0.5)

    # Sharpe ratio (assuming 0% risk-free rate)
    strategy_sharpe = (total_return * 252) / strategy_volatility if strategy_volatility != 0 else 0
    buy_hold_sharpe = (buy_hold_return * 252) / buy_hold_volatility if buy_hold_volatility != 0 else 0

    return {
        'total_return': total_return,
        'buy_hold_return': buy_hold_return,
        'golden_crosses': golden_crosses,
        'death_crosses': death_crosses,
        'strategy_volatility': strategy_volatility,
        'buy_hold_volatility': buy_hold_volatility,
        'strategy_sharpe': strategy_sharpe,
        'buy_hold_sharpe': buy_hold_sharpe,
        'win_rate': len(signals_data[signals_data['EMA_Strategy_Returns'] > 0]) / len(signals_data[signals_data['EMA_Strategy_Returns'] != 0]) if len(signals_data[signals_data['EMA_Strategy_Returns'] != 0]) > 0 else 0
    }

def plot_ema_analysis(data, symbol, ema_windows=[12, 26, 50]):
    """
    Plot price data with EMAs and trading signals

    Args:
        data: DataFrame with price and EMA data
        symbol: Stock symbol for title
        ema_windows: List of EMA windows to plot
    """
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12), height_ratios=[3, 1, 1])

    # Plot price and EMAs
    ax1.plot(data.index, data['Close'], label='Close Price', linewidth=2, color='blue')

    colors = ['orange', 'red', 'green']
    for i, window in enumerate(ema_windows):
        if f'EMA_{window}' in data.columns:
            ax1.plot(data.index, data[f'EMA_{window}'],
                    label=f'EMA {window}', alpha=0.8, color=colors[i % len(colors)])

    # Mark EMA crossover signals
    if 'EMA_Golden_Cross' in data.columns:
        golden_cross_points = data[data['EMA_Golden_Cross']]
        ax1.scatter(golden_cross_points.index, golden_cross_points['Close'],
                   color='green', marker='^', s=100, label='EMA Golden Cross', zorder=5)

    if 'EMA_Death_Cross' in data.columns:
        death_cross_points = data[data['EMA_Death_Cross']]
        ax1.scatter(death_cross_points.index, death_cross_points['Close'],
                   color='red', marker='v', s=100, label='EMA Death Cross', zorder=5)

    ax1.set_title(f'{symbol} - EMA Analysis')
    ax1.set_ylabel('Price')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot EMA signals
    if 'EMA_Signal' in data.columns:
        ax2.plot(data.index, data['EMA_Signal'], label='EMA Trading Signal', color='blue')
        ax2.fill_between(data.index, 0, data['EMA_Signal'], alpha=0.3)
        ax2.set_ylabel('EMA Signal')
        ax2.set_ylim(-1.5, 1.5)
        ax2.grid(True, alpha=0.3)
        ax2.legend()

    # Plot MACD
    if 'MACD' in data.columns:
        ax3.plot(data.index, data['MACD'], label='MACD', color='blue', linewidth=1)
        ax3.plot(data.index, data['MACD_Signal'], label='Signal', color='red', linewidth=1)
        ax3.bar(data.index, data['MACD_Histogram'], label='Histogram', alpha=0.3, color='gray')
        ax3.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax3.set_ylabel('MACD')
        ax3.set_xlabel('Date')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

    plt.tight_layout()

    # Save the plot as JPEG
    filename = f"{symbol.replace('^', '').replace('.', '_')}_ema_analysis.jpg"
    plt.savefig(filename, format='jpg', dpi=300, bbox_inches='tight')
    print(f"Graph saved as: {filename}")

    plt.show()

def compare_ema_vs_sma(data, ema_window=20, sma_window=20):
    """
    Compare EMA vs SMA performance

    Args:
        data: DataFrame with price data
        ema_window: EMA period
        sma_window: SMA period

    Returns:
        DataFrame with comparison metrics
    """
    # Calculate EMA and SMA
    data[f'EMA_{ema_window}'] = calculate_ema(data['Close'], ema_window)
    data[f'SMA_{sma_window}'] = data['Close'].rolling(window=sma_window).mean()

    # Calculate signals for both
    data['EMA_Signal'] = 0
    data['EMA_Signal'][data['Close'] > data[f'EMA_{ema_window}']] = 1
    data['EMA_Signal'][data['Close'] < data[f'EMA_{ema_window}']] = -1

    data['SMA_Signal'] = 0
    data['SMA_Signal'][data['Close'] > data[f'SMA_{sma_window}']] = 1
    data['SMA_Signal'][data['Close'] < data[f'SMA_{sma_window}']] = -1

    # Calculate returns
    data['Returns'] = data['Close'].pct_change()
    data['EMA_Returns'] = data['EMA_Signal'].shift(1) * data['Returns']
    data['SMA_Returns'] = data['SMA_Signal'].shift(1) * data['Returns']

    # Performance comparison
    ema_total_return = (1 + data['EMA_Returns']).cumprod().iloc[-1] - 1
    sma_total_return = (1 + data['SMA_Returns']).cumprod().iloc[-1] - 1

    comparison = {
        'EMA_Return': ema_total_return,
        'SMA_Return': sma_total_return,
        'EMA_Volatility': data['EMA_Returns'].std() * (252 ** 0.5),
        'SMA_Volatility': data['SMA_Returns'].std() * (252 ** 0.5),
        'EMA_Wins': len(data[data['EMA_Returns'] > 0]),
        'SMA_Wins': len(data[data['SMA_Returns'] > 0])
    }

    return comparison

if __name__ == "__main__":
    # NSE stocks and indices examples
    symbols = [
        "^NSEI",        # Nifty 50
        "RELIANCE.NS",  # Reliance Industries
        "TCS.NS",       # Tata Consultancy Services
        "INFY.NS"       # Infosys
    ]

    symbol = "^NSEI"  # Default to Nifty 50
    print(f"Analyzing EMA strategy for {symbol}")

    # Load data
    data = load_nse_data(symbol, period='2y')

    if data is not None:
        # Calculate EMAs
        data_with_ema = calculate_multiple_ema(data, windows=[12, 26, 50])

        # Calculate MACD
        data_with_macd = calculate_macd(data_with_ema)

        # Detect EMA signals
        data_with_signals = detect_ema_crossover_signals(data_with_macd, 'EMA_12', 'EMA_26')

        # Detect MACD signals
        data_with_signals = detect_macd_signals(data_with_signals)

        # Analyze performance
        performance = analyze_ema_performance(data_with_signals, 'EMA_12', 'EMA_26')

        print("\nEMA Strategy Performance Metrics:")
        print(f"Strategy Return: {performance['total_return']:.2%}")
        print(f"Buy & Hold Return: {performance['buy_hold_return']:.2%}")
        print(f"Golden Crosses: {performance['golden_crosses']}")
        print(f"Death Crosses: {performance['death_crosses']}")
        print(f"Win Rate: {performance['win_rate']:.2%}")
        print(f"Strategy Sharpe Ratio: {performance['strategy_sharpe']:.2f}")
        print(f"Buy & Hold Sharpe Ratio: {performance['buy_hold_sharpe']:.2f}")

        # Compare EMA vs SMA
        comparison = compare_ema_vs_sma(data.copy(), ema_window=20, sma_window=20)
        print(f"\nEMA vs SMA Comparison (20-period):")
        print(f"EMA Return: {comparison['EMA_Return']:.2%}")
        print(f"SMA Return: {comparison['SMA_Return']:.2%}")

        # Plot analysis
        plot_ema_analysis(data_with_signals, symbol)

        # Display recent data
        print("\nRecent EMA data:")
        columns_to_show = ['Close', 'EMA_12', 'EMA_26', 'EMA_50', 'MACD', 'MACD_Signal', 'EMA_Signal']
        available_columns = [col for col in columns_to_show if col in data_with_signals.columns]
        print(data_with_signals[available_columns].tail(10))