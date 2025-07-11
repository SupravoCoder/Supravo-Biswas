"""
Automated Earthquake Notification Scheduler
Runs daily to send earthquake prediction notifications to subscribers
"""

import schedule
import time
import logging
from datetime import datetime, date
from earthquake_notifications import notification_system
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('earthquake_notifications.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def send_daily_notifications():
    """Send daily earthquake prediction notifications"""
    try:
        logger.info("Starting daily notification process...")
        current_date = date.today()
        
        # Process and send notifications
        notification_system.process_daily_notifications(current_date)
        
        logger.info("Daily notification process completed successfully")
        
    except Exception as e:
        logger.error(f"Error in daily notification process: {e}")

def send_weekly_summary():
    """Send weekly earthquake activity summary"""
    try:
        logger.info("Starting weekly summary process...")
        # TODO: Implement weekly summary functionality
        logger.info("Weekly summary process completed")
        
    except Exception as e:
        logger.error(f"Error in weekly summary process: {e}")

def setup_scheduler():
    """Setup the notification scheduler"""
    logger.info("Setting up earthquake notification scheduler...")
    
    # Schedule daily notifications at 7:00 AM IST
    schedule.every().day.at("07:00").do(send_daily_notifications)
    
    # Schedule weekly summary on Sundays at 8:00 AM IST
    schedule.every().sunday.at("08:00").do(send_weekly_summary)
    
    # Schedule high-priority alerts check every 3 hours
    schedule.every(3).hours.do(send_daily_notifications)
    
    logger.info("Scheduler setup completed")
    logger.info("Scheduled tasks:")
    logger.info("- Daily notifications: 7:00 AM IST")
    logger.info("- Weekly summary: Sunday 8:00 AM IST")
    logger.info("- High-priority checks: Every 3 hours")

def run_scheduler():
    """Run the scheduler in a loop"""
    setup_scheduler()
    
    logger.info("Starting earthquake notification scheduler...")
    logger.info("Press Ctrl+C to stop the scheduler")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler error: {e}")

def run_scheduler_in_background():
    """Run scheduler in background thread"""
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info("Notification scheduler started in background")
    return scheduler_thread

if __name__ == "__main__":
    # Run scheduler directly
    run_scheduler()
