# Gold Price Prediction API

This API provides gold price predictions based on historical data and various market factors.

## Features

- Fetches real-time gold price data from Yahoo Finance
- Trains an LSTM model on historical data
- Provides predictions for multiple timeframes (1 day to 10 years)
- Scheduled data collection every hour

## API Endpoints

- `/`: Root endpoint, confirms API is running
- `/fetch`: Fetches latest gold price data
- `/train`: Trains the prediction model
- `/predict`: Returns gold price predictions for various timeframes

## Deployment

### Local Development

#### Option 1: Using the run_local.py script

The easiest way to run the application locally is to use the provided script:

```
python run_local.py
```

This will start both the API server and the scheduler in a single terminal window.

#### Option 2: Manual startup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the API:
   ```
   uvicorn main:app --reload
   ```

3. Run the scheduler in a separate terminal:
   ```
   python scheduler.py
   ```

### Testing Deployment Readiness

Before deploying to Heroku, you can test if your application is ready for deployment:

```
python test_deployment.py
```

This script will check for required dependencies, files, and test the API endpoints.

### Deployment to Heroku

This application is configured for deployment to Heroku.

##### Using the deploy.py script

If you prefer Heroku, you can use the provided script:

```
python deploy.py
```

This script will guide you through the deployment process, including:
- Checking if Git and Heroku CLI are installed
- Logging in to Heroku
- Creating a new Heroku app
- Setting up Git
- Deploying the application
- Scaling the worker dyno for the scheduler

##### Manual Heroku deployment

1. Create a Heroku account and install the Heroku CLI

2. Login to Heroku:
   ```
   heroku login
   ```

3. Create a new Heroku app:
   ```
   heroku create gold-price-prediction-api
   ```

4. Push to Heroku:
   ```
   git init
   git add .
   git commit -m "Initial commit"
   git push heroku main
   ```

5. Scale the worker dyno to run the scheduler:
   ```
   heroku ps:scale worker=1
   ```

### Monitoring the Deployed Application

#### Monitoring on Heroku

If using Heroku, you can monitor your application using the Heroku dashboard or CLI:

```
heroku logs --tail
```

You can also check the health of your application by visiting:

```
https://your-app-name.herokuapp.com/health
```

## Data

The application uses the following data sources:
- Gold prices (MCX): Yahoo Finance
- USD/INR exchange rate: Yahoo Finance
- Nifty50 index: Yahoo Finance
- News sentiment: TextBlob analysis of financial news

## Models

The prediction model is an LSTM neural network trained on historical gold price data and related features.