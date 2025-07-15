import yfinance as yf
import pandas as pd
import os
import numpy as np
from datetime import datetime
import time

start = "2023-07-01"
end = datetime.now().strftime("%Y-%m-%d")

print(f"Downloading gold price data from {start} to {end}...")

# [STEP 1] Download individual Close series and rename them
try:
    print("Downloading gold price data (GC=F)...")
    gold_data = yf.download("GC=F", start=start, end=end, interval="1d")
    print(f"Gold data columns: {gold_data.columns.tolist()}")
    gold_usd = gold_data["Close"]
    gold_usd.name = "gold_usd"
    print(f"Gold USD data shape: {gold_usd.shape}")
    print(f"Gold USD first few values: {gold_usd.head()}")
    
    print("Downloading USD/INR exchange rate data...")
    usd_inr_data = yf.download("USDINR=X", start=start, end=end, interval="1d")
    print(f"USD/INR data columns: {usd_inr_data.columns.tolist()}")
    usd_inr = usd_inr_data["Close"]
    usd_inr.name = "usd_inr"
    print(f"USD/INR data shape: {usd_inr.shape}")
    print(f"USD/INR first few values: {usd_inr.head()}")
    
    print("Downloading Nifty50 data...")
    nifty_data = yf.download("^NSEI", start=start, end=end, interval="1d")
    print(f"Nifty50 data columns: {nifty_data.columns.tolist()}")
    nifty = nifty_data["Close"]
    nifty.name = "nifty50"
    print(f"Nifty50 data shape: {nifty.shape}")
    print(f"Nifty50 first few values: {nifty.head()}")
    
    # [STEP 2] Concatenate into a single DataFrame
    print("Combining data...")
    df = pd.concat([gold_usd, usd_inr, nifty], axis=1)
    print(f"Combined DataFrame shape: {df.shape}")
    print(f"Combined DataFrame columns: {df.columns.tolist()}")
    print(f"Combined DataFrame first few rows:\n{df.head()}")
    
    # Handle any missing values by forward filling then backward filling
    print("Handling missing values...")
    df = df.ffill().bfill()
    
    print(f"Downloaded {len(df)} days of data")
except Exception as e:
    print(f"Error downloading data: {e}")
    import traceback
    print(traceback.format_exc())
    raise

# [STEP 3] Compute MCX price of gold in INR per 10 grams
print("Computing MCX gold price in INR per 10 grams...")
df["mcx_gold_price"] = df["gold_usd"] * df["usd_inr"] * (10 / 31.1035)
print(f"MCX gold price range: {df['mcx_gold_price'].min()} to {df['mcx_gold_price'].max()}")

# [STEP 4] Cleanup and formatting
print("Cleaning up and formatting data...")
df = df[["mcx_gold_price", "usd_inr", "nifty50"]]
df.reset_index(inplace=True)
df.rename(columns={"Date": "timestamp"}, inplace=True)
print(f"DataFrame after cleanup: {df.shape} with columns {df.columns.tolist()}")

# Add dummy sentiment
print("Adding news sentiment...")
df["news_sentiment"] = 0.05

# [STEP 5] Save CSV
print("Saving data to CSV...")
os.makedirs("data", exist_ok=True)
output_file = "data/gold_data_real.csv"
df.to_csv(output_file, index=False)

print(f"[SUCCESS] Saved {len(df)} records to {output_file}")
print(f"First few rows:\n{df.head()}")
