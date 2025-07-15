import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import joblib
from datetime import datetime, timedelta

def predict_multiple_timeframes():
    """
    Predict gold prices for multiple timeframes: 1 day, 1 week, 1 month, 1 year, 5 years, 10 years
    """
    print("Starting predict_multiple_timeframes()...")
    df = pd.read_csv("data/gold_data.csv")
    features = ["mcx_gold_price", "usd_inr", "nifty50", "news_sentiment"]
    scaler = joblib.load("models/scaler.save")
    model = load_model("models/lstm_model.h5", compile=False)
    
    # Current price as baseline
    current_price = df["mcx_gold_price"].iloc[-1]
    
    # Define timeframes and corresponding number of days to predict
    timeframes = {
        "1 day": 1,
        "1 week": 7,
        "1 month": 30,
        "1 year": 365,
        "5 years": 365 * 5,
        "10 years": 365 * 10
    }
    
    predictions = {}
    scaled_data = scaler.transform(df[features])
    last_seq = scaled_data[-5:]
    
    # For short-term predictions (1 day, 1 week), use the LSTM model directly
    for timeframe, days in timeframes.items():
        if days <= 30:  # For short-term predictions
            # For multi-day predictions, we recursively predict one day at a time
            current_seq = last_seq.copy()
            pred_price = current_price
            
            for _ in range(days):
                next_input = np.expand_dims(current_seq, axis=0)
                next_pred_scaled = model.predict(next_input, verbose=0)
                
                # Get the predicted price
                pred_price = scaler.inverse_transform(
                    np.hstack((next_pred_scaled, np.zeros((1, len(features)-1))))
                )[:, 0][0]
                
                # Update the sequence for the next prediction
                # Assume other features remain constant for simplicity
                new_row = current_seq[-1].copy()
                new_row[0] = next_pred_scaled[0][0]  # Update gold price
                
                # Shift the sequence and add the new prediction
                current_seq = np.vstack([current_seq[1:], new_row])
            
            predictions[timeframe] = round(pred_price, 2)
        else:
            # For long-term predictions (1 year, 5 years, 10 years)
            # Use a simplified growth model based on historical data
            # Calculate average daily growth rate from historical data
            if len(df) > 30:  # Need sufficient historical data
                # Calculate average monthly growth rate from the last year of data or available data
                lookback = min(365, len(df) - 1)
                start_price = df["mcx_gold_price"].iloc[-lookback]
                end_price = df["mcx_gold_price"].iloc[-1]
                
                if start_price > 0:
                    daily_growth_rate = (end_price / start_price) ** (1 / lookback) - 1
                    # Apply compound growth for the prediction period
                    predicted_price = current_price * ((1 + daily_growth_rate) ** days)
                    predictions[timeframe] = round(predicted_price, 2)
                else:
                    predictions[timeframe] = None
            else:
                predictions[timeframe] = None
    
    # Add prediction dates
    today = datetime.now()
    prediction_dates = {}
    for timeframe, days in timeframes.items():
        prediction_date = (today + timedelta(days=days)).strftime("%Y-%m-%d")
        prediction_dates[timeframe] = prediction_date
    
    return {
        "prices": predictions,
        "dates": prediction_dates,
        "current_price": round(current_price, 2),
        "current_date": today.strftime("%Y-%m-%d")
    }

def predict_next():
    print("Starting predict_next()...")
    df = pd.read_csv("data/gold_data.csv")
    print(f"Loaded data with shape: {df.shape}")
    features = ["mcx_gold_price", "usd_inr", "nifty50", "news_sentiment"]
    scaler = joblib.load("models/scaler.save")
    model = load_model("models/lstm_model.h5", compile=False)
    print("Loaded model and scaler")

    scaled_data = scaler.transform(df[features])
    last_seq = scaled_data[-5:]
    next_input = np.expand_dims(last_seq, axis=0)

    next_pred_scaled = model.predict(next_input)
    future_price = scaler.inverse_transform(
        np.hstack((next_pred_scaled, np.zeros((1, len(features)-1))))
    )[:, 0][0]

    # Get 1-day and 1-year predictions for display
    timeframe_predictions = predict_multiple_timeframes()
    one_day_price = timeframe_predictions["prices"]["1 day"]
    one_year_price = timeframe_predictions["prices"]["1 year"]
    one_day_date = timeframe_predictions["dates"]["1 day"]
    one_year_date = timeframe_predictions["dates"]["1 year"]
    
    print(f"🔮 Predicted Next Gold Price: ₹{round(future_price, 2)}")
    print(f"📅 1-Day Forecast ({one_day_date}): ₹{one_day_price}")
    print(f"📈 1-Year Forecast ({one_year_date}): ₹{one_year_price}")
    
    return {
        "next_price": round(future_price, 2),
        "one_day": {
            "price": one_day_price,
            "date": one_day_date
        },
        "one_year": {
            "price": one_year_price,
            "date": one_year_date
        },
        "all_forecasts": timeframe_predictions
    }
