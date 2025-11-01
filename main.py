import yfinance as yf

# Symbol for NIFTY 50 index
symbol = "^NSEI"

# Download last 5 years data
df = yf.download(symbol, period="5y")

print(df.head())

# Save to CSV
df.to_csv("nifty50_data.csv")
print("\nData saved successfully to nifty50_data.csv")
