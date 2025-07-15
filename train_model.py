import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
import joblib
import os

def train_model():
    df = pd.read_csv("data/gold_data.csv")
    if len(df) < 50:
        print("⛔ Not enough data to train.")
        return

    # Check if historical_prices column exists and remove it for training
    features = ["mcx_gold_price", "usd_inr", "nifty50", "news_sentiment"]
    train_df = df[features].copy()
    
    # Check if we need to normalize the gold price data
    # If there's a large discrepancy in the gold price values, it might indicate
    # a change in the unit (from per ounce to per 10 grams)
    gold_prices = train_df['mcx_gold_price']
    max_price = gold_prices.max()
    min_price = gold_prices.min()
    
    # If there's a huge difference, we might need to normalize the older data
    if max_price / min_price > 100:  # Arbitrary threshold to detect unit change
        print("Detected significant change in gold price units. Normalizing data...")
        # Find the transition point (where prices jumped significantly)
        for i in range(1, len(gold_prices)):
            if gold_prices.iloc[i] / gold_prices.iloc[i-1] > 50:  # Threshold for detecting jump
                transition_idx = i
                break
        else:
            transition_idx = len(gold_prices)  # No clear transition found
        
        # Convert older prices to the new scale (per 10 grams)
        # Assuming the conversion factor is approximately 31.1035 (troy ounce to grams) / 10 * 100
        conversion_factor = (gold_prices.iloc[transition_idx:].mean() / gold_prices.iloc[:transition_idx].mean())
        train_df.loc[:transition_idx-1, 'mcx_gold_price'] *= conversion_factor
        
        print(f"Converted older gold prices using factor: {conversion_factor:.2f}")
    
    # Save the normalized data for future use
    df[features] = train_df
    df.to_csv("data/gold_data_normalized.csv", index=False)
    
    # Handle any missing values
    train_df.fillna(method='ffill', inplace=True)
    train_df.fillna(method='bfill', inplace=True)  # Backup in case there are NaNs at the beginning
    
    print(f"Training model with {len(train_df)} data points")
    
    # Scale the data
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(train_df)
    joblib.dump(scaler, "models/scaler.save")

    # Create sequences for LSTM
    X, y = [], []
    window = 5
    for i in range(len(scaled_data) - window):
        X.append(scaled_data[i:i+window])
        y.append(scaled_data[i+window][0])  # gold price is the first column

    X, y = np.array(X), np.array(y)
    
    # Build a more robust LSTM model
    model = Sequential()
    model.add(LSTM(128, activation='relu', return_sequences=True, input_shape=(X.shape[1], X.shape[2])))
    model.add(Dropout(0.2))
    model.add(LSTM(64, activation='relu'))
    model.add(Dropout(0.2))
    model.add(Dense(32, activation='relu'))
    model.add(Dense(1))
    
    model.compile(optimizer='adam', loss='mse')
    
    # Train with early stopping
    from tensorflow.keras.callbacks import EarlyStopping
    early_stopping = EarlyStopping(monitor='loss', patience=10, restore_best_weights=True)
    
    print("Training LSTM model...")
    model.fit(
        X, y, 
        epochs=200, 
        batch_size=32, 
        verbose=1,
        callbacks=[early_stopping]
    )

    os.makedirs("models", exist_ok=True)
    model.save("models/lstm_model.h5")
    print("[SUCCESS] Model trained and saved.")
    
    # Evaluate model
    train_loss = model.evaluate(X, y, verbose=0)
    print(f"Training MSE: {train_loss:.4f}")
    
    return model
