import schedule
import time
import logging
import os
import sys
from datetime import datetime
from fetcher import fetch_data
from train_model import train_model
from predict_model import predict_next

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'scheduler.log'))
    ]
)
logger = logging.getLogger('gold-price-scheduler')

def job():
    try:
        logger.info(f"Starting scheduled job at {datetime.now().isoformat()}")
        
        logger.info("Fetching data...")
        fetch_data()
        
        logger.info("Training model...")
        train_model()
        
        logger.info("Generating predictions...")
        predict_next()
        
        logger.info(f"Job completed successfully at {datetime.now().isoformat()}")
    except Exception as e:
        logger.error(f"Error in scheduled job: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

# Schedule job to run every hour
schedule.every(60).minutes.do(job)

if __name__ == "__main__":
    logger.info(" Scheduler starting up...")
    logger.info("Running initial job...")
    job()  # Run immediately on startup
    
    logger.info("Scheduler running every hour...")
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in scheduler loop: {str(e)}")
            # Continue running even if there's an error
            time.sleep(60)  # Wait a minute before retrying
