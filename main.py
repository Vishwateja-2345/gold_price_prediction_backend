from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fetcher import fetch_data
from train_model import train_model
from predict_model import predict_next, predict_multiple_timeframes
import os
import json
from datetime import datetime

app = FastAPI(
    title="Gold Price Prediction API",
    description="API for predicting gold prices based on historical data and market factors",
    version="1.0.0"
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
def root():
    # Get the last update time from the historical_prices.json file
    last_update = "Unknown"
    try:
        json_path = os.path.join(os.path.dirname(__file__), "data", "historical_prices.json")
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                data = json.load(f)
                last_update = data.get("timestamp", "Unknown")
    except Exception:
        pass
    
    return {
        "message": "🟡 Gold Price Prediction API is running!",
        "note": "All gold prices are per 10 grams in INR",
        "version": "1.0.0",
        "last_data_update": last_update,
        "endpoints": [
            {
                "path": "/",
                "method": "GET",
                "description": "API information"
            },
            {
                "path": "/health",
                "method": "GET",
                "description": "Health check endpoint"
            },
            {
                "path": "/fetch",
                "method": "POST",
                "description": "Fetch latest gold price data"
            },
            {
                "path": "/train",
                "method": "POST",
                "description": "Train the prediction model"
            },
            {
                "path": "/predict",
                "method": "GET",
                "description": "Get gold price predictions"
            }
        ]
    }

@app.get("/health")
def health_check():
    # Check if data files exist
    data_path = os.path.join(os.path.dirname(__file__), "data")
    csv_path = os.path.join(data_path, "gold_data.csv")
    json_path = os.path.join(data_path, "historical_prices.json")
    model_path = os.path.join(os.path.dirname(__file__), "models", "lstm_model.h5")
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "data_files": {
                "gold_data_csv": os.path.exists(csv_path),
                "historical_prices_json": os.path.exists(json_path)
            },
            "model_files": {
                "lstm_model": os.path.exists(model_path)
            }
        }
    }
    
    # If any critical component is missing, change status
    if not all([health_status["checks"]["data_files"]["gold_data_csv"], 
                health_status["checks"]["model_files"]["lstm_model"]]):
        health_status["status"] = "degraded"
    
    return health_status

@app.post("/fetch")
def fetch_endpoint():
    data = fetch_data()
    return {"status": "success", "fetched_data": data}

@app.post("/train")
def train_endpoint():
    train_model()
    return {"status": "success", "message": "Model trained"}

@app.get("/predict")
def predict_endpoint():
    print("Received request to /predict endpoint")
    try:
        prediction_data = predict_next()
        print("Successfully got prediction data")
        return {
            "status": "success", 
            "predicted_price": prediction_data["next_price"],
            "forecasts": {
                "one_day": {
                    "price": prediction_data["one_day"]["price"],
                    "date": prediction_data["one_day"]["date"]
                },
                "one_year": {
                    "price": prediction_data["one_year"]["price"],
                    "date": prediction_data["one_year"]["date"]
                },
                "all_timeframes": prediction_data["all_forecasts"]
            },
            "unit": "per 10 grams in INR"
        }
    except Exception as e:
        print(f"Error in predict_endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

@app.get("/predict/timeframes")
def predict_timeframes_endpoint():
    predictions = predict_multiple_timeframes()
    return {
        "status": "success", 
        "predictions": predictions,
        "unit": "per 10 grams in INR"
    }

@app.get("/gold/historical")
def historical_prices_endpoint():
    data = fetch_data()
    return {
        "status": "success", 
        "historical_prices": data["historical_prices"],
        "unit": "per 10 grams in INR"
    }
