import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta
from textblob import TextBlob
import os

NEWS_API_KEY = "8cb14c8857c146a080386ecc4be99ed9"  # 👉 get it from https://newsapi.org

def get_sentiment():
    url = f"https://newsapi.org/v2/everything?q=gold+india&apiKey={NEWS_API_KEY}"
    response = requests.get(url).json()
    articles = response.get("articles", [])
    titles = [article["title"] for article in articles]
    if not titles:
        return 0
    scores = [TextBlob(t).sentiment.polarity for t in titles]
    return sum(scores) / len(scores)

def get_gold_price_inr():
    # Using Gold futures in USD and converting to INR
    try:
        # Use Gold futures (GC=F) which is more reliable
        gold_usd = yf.Ticker("GC=F")  # Gold futures in USD
        usdinr = yf.Ticker("INR=X")  # USD/INR exchange rate
        
        # Get the latest prices
        gold_usd_data = gold_usd.history(period="1d")
        usdinr_data = usdinr.history(period="1d")
        
        if gold_usd_data.empty or usdinr_data.empty:
            # If no data, use hardcoded fallback values
            print("Warning: Using fallback gold price data")
            gold_usd_price = 2400.0  # Approximate USD per troy ounce
            usd_inr_rate = 85.0     # Approximate USD/INR rate
        else:
            gold_usd_price = gold_usd_data['Close'].iloc[-1]
            usd_inr_rate = usdinr_data['Close'].iloc[-1]
        
        # Convert to INR per troy ounce
        gold_price_inr_per_ounce = gold_usd_price * usd_inr_rate
        
        # Convert from INR per troy ounce to INR per 10 grams
        # 1 troy ounce = 31.1035 grams
        gold_price_per_10g = (gold_price_inr_per_ounce / 31.1035) * 10
        return gold_price_per_10g
    except Exception as e:
        print(f"Error fetching gold price: {e}")
        # Return a reasonable fallback value for gold price in INR per 10g
        return 92000.0  # Approximate price in INR per 10g

def fetch_historical_prices():
    # Get historical gold prices for different timeframes
    timeframes = {
        "1d": "1 day",
        "1wk": "1 week",
        "1mo": "1 month",
        "1y": "1 year",
        "5y": "5 years",
        "10y": "10 years"
    }
    
    historical_prices = {}
    
    # Use the same reliable tickers as in get_gold_price_inr
    gold_usd = yf.Ticker("GC=F")  # Gold futures in USD
    usdinr = yf.Ticker("INR=X")  # USD/INR exchange rate
    
    # Get all historical data at once to minimize API calls
    try:
        # Get the longest period data (10y) and we'll use subsets for shorter periods
        gold_df_all = gold_usd.history(period="10y")
        inr_df_all = usdinr.history(period="10y")
        
        if gold_df_all.empty or inr_df_all.empty:
            print("Warning: Could not fetch historical data, using current price for all timeframes")
            # Use current price for all timeframes
            current_price = get_gold_price_inr()
            for label in timeframes.values():
                historical_prices[label] = current_price
            return historical_prices
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        # Use current price for all timeframes
        current_price = get_gold_price_inr()
        for label in timeframes.values():
            historical_prices[label] = current_price
        return historical_prices
    
    # Process each timeframe
    for period, label in timeframes.items():
        try:
            # Get the appropriate slice of data for this period
            if period == "1d":
                gold_df = gold_df_all.iloc[-1:]
                inr_df = inr_df_all.iloc[-1:]
            elif period == "1wk":
                gold_df = gold_df_all.iloc[-7:]
                inr_df = inr_df_all.iloc[-7:]
            elif period == "1mo":
                gold_df = gold_df_all.iloc[-30:]
                inr_df = inr_df_all.iloc[-30:]
            elif period == "1y":
                gold_df = gold_df_all.iloc[-365:]
                inr_df = inr_df_all.iloc[-365:]
            elif period == "5y":
                gold_df = gold_df_all.iloc[-1825:]
                inr_df = inr_df_all.iloc[-1825:]
            else:  # 10y or any other
                gold_df = gold_df_all
                inr_df = inr_df_all
            
            if not gold_df.empty and not inr_df.empty:
                # Use the latest available price
                gold_price = gold_df['Close'].iloc[-1]
                inr_rate = inr_df['Close'].iloc[-1]
                
                # Convert from INR per troy ounce to INR per 10 grams
                gold_price_per_ounce = gold_price * inr_rate
                gold_price_per_10g = (gold_price_per_ounce / 31.1035) * 10
                historical_prices[label] = round(gold_price_per_10g, 2)
            else:
                # Fallback to current price
                historical_prices[label] = get_gold_price_inr()
        except Exception as e:
            print(f"Error processing {label} data: {e}")
            # Fallback to current price
            historical_prices[label] = get_gold_price_inr()
    
    return historical_prices

def fetch_data():
    print("Fetching gold price data...")
    gold_price_inr = get_gold_price_inr()
    
    print("Fetching Nifty50 data...")
    try:
        nifty = yf.Ticker("^NSEI")
        nifty_data = nifty.history(period="1d")
        if not nifty_data.empty:
            nifty_price = nifty_data['Close'].iloc[-1]
        else:
            print("Warning: Could not fetch Nifty50 data, using fallback value")
            nifty_price = 25000.0  # Fallback value
    except Exception as e:
        print(f"Error fetching Nifty50 data: {e}")
        nifty_price = 25000.0  # Fallback value
    
    print("Fetching USD/INR data...")
    try:
        usdinr = yf.Ticker("INR=X")  # More reliable ticker
        usdinr_data = usdinr.history(period="1d")
        if not usdinr_data.empty:
            usd_inr = usdinr_data['Close'].iloc[-1]
        else:
            print("Warning: Could not fetch USD/INR data, using fallback value")
            usd_inr = 85.0  # Fallback value
    except Exception as e:
        print(f"Error fetching USD/INR data: {e}")
        usd_inr = 85.0  # Fallback value
    
    print("Fetching news sentiment...")
    try:
        sentiment = get_sentiment()
    except Exception as e:
        print(f"Error fetching sentiment data: {e}")
        sentiment = 0.05  # Neutral sentiment as fallback
    
    print("Fetching historical prices...")
    historical_prices = fetch_historical_prices()

    # Create the main record without historical_prices to avoid CSV parsing issues
    record = {
        "timestamp": datetime.now().isoformat(),
        "mcx_gold_price": round(gold_price_inr, 2),  # Gold price per 10 grams in INR
        "usd_inr": round(usd_inr, 2),
        "nifty50": round(nifty_price, 2),
        "news_sentiment": round(sentiment, 3)
        # Historical prices will be stored separately
    }

    # Store the main record in CSV
    df = pd.DataFrame([record])
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/gold_data.csv", mode='a', index=False, header=not os.path.exists("data/gold_data.csv"))
    
    # Store historical prices in a separate JSON file for easy retrieval
    import json
    historical_data = {
        "timestamp": datetime.now().isoformat(),
        "historical_prices": {k: float(v) if v is not None else None for k, v in historical_prices.items()}
    }
    
    with open("data/historical_prices.json", "w") as f:
        json.dump(historical_data, f, indent=2)
    
    # Add historical prices to the record for the return value
    record["historical_prices"] = historical_prices
    
    print("[SUCCESS] Fetched and stored:", record)
    return record
