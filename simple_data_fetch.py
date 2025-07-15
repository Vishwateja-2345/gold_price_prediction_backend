import yfinance as yf
import pandas as pd
import os
import numpy as np
from datetime import datetime

# Set date range for data collection
start = "2023-07-01"
end = datetime.now().strftime("%Y-%m-%d")

print(f"Downloading gold price data from {start} to {end}...")

try:
    # Download gold price data
    print("Downloading gold price data (GC=F)...")
    gold_data = yf.download("GC=F", start=start, end=end, interval="1d")
    print(f"Gold data shape: {gold_data.shape}")
    print(f"Gold data columns: {gold_data.columns.tolist()}")
    print(f"Gold data first few rows:\n{gold_data.head()}")
    
    # Download USD/INR exchange rate data
    print("Downloading USD/INR exchange rate data...")
    usd_inr_data = yf.download("USDINR=X", start=start, end=end, interval="1d")
    print(f"USD/INR data shape: {usd_inr_data.shape}")
    print(f"USD/INR data columns: {usd_inr_data.columns.tolist()}")
    print(f"USD/INR data first few rows:\n{usd_inr_data.head()}")
    
    # Download Nifty50 data
    print("Downloading Nifty50 data...")
    nifty_data = yf.download("^NSEI", start=start, end=end, interval="1d")
    print(f"Nifty50 data shape: {nifty_data.shape}")
    print(f"Nifty50 data columns: {nifty_data.columns.tolist()}")
    print(f"Nifty50 data first few rows:\n{nifty_data.head()}")
    
    # Create a new DataFrame with the required columns
    print("Creating combined DataFrame...")
    
    # Create a new DataFrame with the required columns
    # First, create separate Series with the Close prices
    gold_series = gold_data['Close']
    usd_inr_series = usd_inr_data['Close']
    nifty_series = nifty_data['Close']
    
    # Create a new DataFrame by joining the series
    df = pd.DataFrame()
    df['gold_usd'] = gold_series
    df['usd_inr'] = usd_inr_series
    df['nifty50'] = nifty_series
    
    # Handle any missing values
    print("Handling missing values...")
    print(f"Missing values before filling: {df.isna().sum().to_dict()}")
    df = df.ffill().bfill()
    print(f"Missing values after filling: {df.isna().sum().to_dict()}")
    
    # Calculate MCX gold price in INR per 10 grams
    print("Calculating MCX gold price...")
    df['mcx_gold_price'] = df['gold_usd'] * df['usd_inr'] * (10 / 31.1035)
    
    # Add dummy sentiment
    df['news_sentiment'] = 0.05
    
    # Reset index to make date a column
    print("Converting index to timestamp column...")
    df = df.reset_index()
    print(f"DataFrame columns after reset_index: {df.columns.tolist()}")
    df = df.rename(columns={'Date': 'timestamp'})
    print(f"DataFrame columns after rename: {df.columns.tolist()}")
    
    # Reorder columns
    print("Reordering columns...")
    df = df[['timestamp', 'mcx_gold_price', 'usd_inr', 'nifty50', 'news_sentiment']]
    
    # Save to CSV
    os.makedirs("data", exist_ok=True)
    output_file = "data/gold_data_real.csv"
    df.to_csv(output_file, index=False)
    
    print(f"[SUCCESS] Successfully saved {len(df)} records to {output_file}")
    print(f"First few rows:\n{df.head()}")
    print(f"Last few rows:\n{df.tail()}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    print(traceback.format_exc())