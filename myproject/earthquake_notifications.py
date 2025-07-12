"""
Earthquake Prediction Notification System
Sends WhatsApp and SMS notifications for future earthquake predictions
from PINN and Random Forest models.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import streamlit as st
import requests
import json
import sqlite3
import os
from typing import List, Dict, Optional
import schedule
import time
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EarthquakeNotificationSystem:
    """
    A comprehensive system for sending earthquake prediction notifications
    via WhatsApp and SMS using various APIs.
    """
    
    def __init__(self):
        self.db_path = "earthquake_notifications.db"
        self.init_database()
        
        # Notification APIs configuration
        self.whatsapp_apis = {
            "twilio": {
                "enabled": False,
                "account_sid": "",
                "auth_token": "",
                "whatsapp_number": ""
            },
            "ultramsg": {
                "enabled": False,
                "token": "",
                "instance_id": ""
            }
        }
        
        self.sms_apis = {
            "twilio": {
                "enabled": False,
                "account_sid": "",
                "auth_token": "",
                "phone_number": ""
            },
            "textbelt": {
                "enabled": False,
                "api_key": ""
            }
        }
        
    def init_database(self):
        """Initialize SQLite database for tracking notifications"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notification_subscribers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone_number TEXT NOT NULL UNIQUE,
                whatsapp_number TEXT,
                notification_types TEXT,  -- JSON array of types
                preferred_method TEXT,  -- 'whatsapp', 'sms', 'both'
                min_magnitude REAL DEFAULT 4.0,
                regions TEXT,  -- JSON array of regions
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                active BOOLEAN DEFAULT 1
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sent_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subscriber_id INTEGER,
                prediction_date DATE,
                earthquake_data TEXT,  -- JSON of earthquake prediction
                notification_type TEXT,  -- 'whatsapp', 'sms'
                status TEXT,  -- 'sent', 'failed', 'pending'
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                error_message TEXT,
                FOREIGN KEY (subscriber_id) REFERENCES notification_subscribers (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prediction_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_date DATE,
                latitude REAL,
                longitude REAL,
                predicted_magnitude REAL,
                probability REAL,
                risk_category TEXT,
                model_type TEXT,
                region TEXT,
                alert_sent BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_subscriber(self, name: str, phone_number: str, whatsapp_number: str = None,
                      notification_types: List[str] = None, preferred_method: str = "both",
                      min_magnitude: float = 4.0, regions: List[str] = None):
        """Add a new notification subscriber"""
        if notification_types is None:
            notification_types = ["high_risk", "medium_risk"]
        if regions is None:
            regions = ["Himalayan", "Central", "South", "West", "East"]
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO notification_subscribers 
                (name, phone_number, whatsapp_number, notification_types, 
                 preferred_method, min_magnitude, regions)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, phone_number, whatsapp_number or phone_number,
                  json.dumps(notification_types), preferred_method, 
                  min_magnitude, json.dumps(regions)))
            
            conn.commit()
            subscriber_id = cursor.lastrowid
            logger.info(f"Added subscriber: {name} (ID: {subscriber_id})")
            return subscriber_id
            
        except sqlite3.IntegrityError:
            logger.error("A subscriber with the provided phone number already exists.")
            return None
        finally:
            conn.close()
    
    def configure_whatsapp_api(self, provider: str, **config):
        """Configure WhatsApp API settings"""
        if provider in self.whatsapp_apis:
            self.whatsapp_apis[provider].update(config)
            self.whatsapp_apis[provider]["enabled"] = True
            logger.info(f"Configured {provider} WhatsApp API")
    
    def configure_sms_api(self, provider: str, **config):
        """Configure SMS API settings"""
        if provider in self.sms_apis:
            self.sms_apis[provider].update(config)
            self.sms_apis[provider]["enabled"] = True
            logger.info(f"Configured {provider} SMS API")
    
    def load_prediction_data(self, file_path: str) -> pd.DataFrame:
        """Load earthquake prediction data from CSV"""
        try:
            df = pd.read_csv(file_path)
            df['prediction_date'] = pd.to_datetime(df['prediction_date']).dt.date
            return df
        except Exception as e:
            logger.error(f"Error loading prediction data: {e}")
            return pd.DataFrame()
    
    def filter_predictions_for_notifications(self, df: pd.DataFrame, 
                                           target_date: date = None) -> pd.DataFrame:
        """Filter predictions that should trigger notifications"""
        if target_date is None:
            target_date = date.today()
        
        # Filter for specific date and high-risk predictions
        filtered_df = df[
            (df['prediction_date'] == target_date) &
            (
                (df['risk_category'].isin(['High', 'Medium'])) |
                (df['predicted_magnitude'] >= 4.0) |
                (df['earthquake_probability'] >= 0.3)
            )
        ].copy()
        
        return filtered_df.sort_values(['predicted_magnitude', 'earthquake_probability'], 
                                     ascending=[False, False])
    
    def generate_notification_message(self, earthquake_data: Dict, 
                                    notification_type: str = "alert") -> str:
        """Generate notification message text"""
        date_str = earthquake_data['prediction_date']
        magnitude = earthquake_data['predicted_magnitude']
        probability = earthquake_data['earthquake_probability'] * 100
        region = earthquake_data['region']
        regional_zone = earthquake_data['regional_zone']
        model = earthquake_data['model_type']
        risk = earthquake_data['risk_category']
        lat = earthquake_data['latitude']
        lng = earthquake_data['longitude']
        
        # Determine urgency emoji
        if magnitude >= 6.0:
            urgency_emoji = "🚨🚨🚨"
        elif magnitude >= 5.0:
            urgency_emoji = "⚠️⚠️"
        else:
            urgency_emoji = "⚡"
        
        if notification_type == "daily_summary":
            message = f"""
🌍 *Bhukamp Daily Earthquake Forecast - {date_str}*

{urgency_emoji} *{risk} Risk Prediction*
📍 *Location*: {regional_zone}, {region}
📊 *Magnitude*: {magnitude:.1f}
🎯 *Probability*: {probability:.1f}%
🤖 *Model*: {model}
📍 *Coordinates*: {lat:.2f}°N, {lng:.2f}°E

*About Bhukamp*: AI-powered earthquake forecasting for India using PINN and Random Forest models.

⚠️ *Disclaimer*: This is a prediction based on AI models. Maintain earthquake preparedness always.

Stay safe! 🙏
Team Bhukamp
            """.strip()
        
        else:  # alert type
            message = f"""
🚨 *EARTHQUAKE PREDICTION ALERT*

{urgency_emoji} *{risk} Risk Earthquake Predicted*
📅 *Date*: {date_str}
📍 *Region*: {regional_zone}, {region}
📊 *Magnitude*: {magnitude:.1f}
🎯 *Probability*: {probability:.1f}%
🤖 *Model*: {model}

📍 *Coordinates*: {lat:.2f}°N, {lng:.2f}°E

⚠️ *Preparedness Recommendations*:
• Keep emergency kit ready
• Review evacuation plans
• Stay informed through official channels

*This is an AI prediction - maintain general earthquake preparedness.*

🌍 Bhukamp - Earthquake Forecasting for India
            """.strip()
        
        return message
    
    def send_whatsapp_message(self, phone_number: str, message: str, 
                            provider: str = "ultramsg") -> bool:
        """Send WhatsApp message using specified provider"""
        if not self.whatsapp_apis[provider]["enabled"]:
            logger.error(f"{provider} WhatsApp API not configured")
            return False
        
        try:
            if provider == "twilio":
                return self._send_whatsapp_twilio(phone_number, message)
            elif provider == "ultramsg":
                return self._send_whatsapp_ultramsg(phone_number, message)
            else:
                logger.error(f"Unknown WhatsApp provider: {provider}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            return False
    
    def _send_whatsapp_ultramsg(self, phone_number: str, message: str) -> bool:
        """Send WhatsApp message using UltraMsg API"""
        config = self.whatsapp_apis["ultramsg"]
        
        url = f"https://api.ultramsg.com/{config['instance_id']}/messages/chat"
        
        payload = {
            "token": config["token"],
            "to": phone_number,
            "body": message
        }
        
        response = requests.post(url, data=payload)
        
        if response.status_code == 200:
            logger.info(f"WhatsApp message sent successfully to {phone_number}")
            return True
        else:
            logger.error(f"Failed to send WhatsApp message: {response.text}")
            return False
    
    def _send_whatsapp_twilio(self, phone_number: str, message: str) -> bool:
        """Send WhatsApp message using Twilio API"""
        config = self.whatsapp_apis["twilio"]
        
        try:
            from twilio.rest import Client
            
            client = Client(config["account_sid"], config["auth_token"])
            
            message_obj = client.messages.create(
                body=message,
                from_=f"whatsapp:{config['whatsapp_number']}",
                to=f"whatsapp:{phone_number}"
            )
            
            logger.info(f"WhatsApp message sent via Twilio: {message_obj.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Twilio WhatsApp error: {e}")
            return False
    
    def send_sms_message(self, phone_number: str, message: str, 
                        provider: str = "textbelt") -> bool:
        """Send SMS message using specified provider"""
        if not self.sms_apis[provider]["enabled"]:
            logger.error(f"{provider} SMS API not configured")
            return False
        
        try:
            if provider == "twilio":
                return self._send_sms_twilio(phone_number, message)
            elif provider == "textbelt":
                return self._send_sms_textbelt(phone_number, message)
            else:
                logger.error(f"Unknown SMS provider: {provider}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending SMS message: {e}")
            return False
    
    def _send_sms_textbelt(self, phone_number: str, message: str) -> bool:
        """Send SMS using TextBelt API"""
        config = self.sms_apis["textbelt"]
        
        # Truncate message for SMS limits
        if len(message) > 1600:
            message = message[:1600] + "..."
        
        response = requests.post('https://textbelt.com/text', {
            'phone': phone_number,
            'message': message,
            'key': config["api_key"] if config["api_key"] else "textbelt"
        })
        
        result = response.json()
        
        if result.get('success'):
            logger.info(f"SMS sent successfully to {phone_number}")
            return True
        else:
            logger.error(f"Failed to send SMS: {result.get('error')}")
            return False
    
    def _send_sms_twilio(self, phone_number: str, message: str) -> bool:
        """Send SMS using Twilio API"""
        config = self.sms_apis["twilio"]
        
        try:
            from twilio.rest import Client
            
            client = Client(config["account_sid"], config["auth_token"])
            
            # Truncate message for SMS limits
            if len(message) > 1600:
                message = message[:1600] + "..."
            
            message_obj = client.messages.create(
                body=message,
                from_=config["phone_number"],
                to=phone_number
            )
            
            logger.info(f"SMS sent via Twilio: {message_obj.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Twilio SMS error: {e}")
            return False
    
    def send_notification_to_subscriber(self, subscriber_id: int, 
                                      earthquake_data: Dict,
                                      notification_type: str = "alert") -> bool:
        """Send notification to a specific subscriber"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get subscriber details
            cursor.execute('''
                SELECT name, phone_number, whatsapp_number, preferred_method,
                       min_magnitude, regions, notification_types
                FROM notification_subscribers 
                WHERE id = ? AND active = 1
            ''', (subscriber_id,))
            
            subscriber = cursor.fetchone()
            if not subscriber:
                logger.error(f"Subscriber {subscriber_id} not found or inactive")
                return False
            
            name, phone, whatsapp, method, min_mag, regions_json, types_json = subscriber
            
            # Check if earthquake meets subscriber criteria
            regions = json.loads(regions_json)
            types = json.loads(types_json)
            
            if (earthquake_data['predicted_magnitude'] < min_mag or
                earthquake_data['regional_zone'] not in regions):
                logger.info(f"Earthquake doesn't meet criteria for {name}")
                return False
            
            # Generate message
            message = self.generate_notification_message(earthquake_data, notification_type)
            
            success = False
            
            # Send notifications based on preference
            if method in ["whatsapp", "both"]:
                success_wa = self.send_whatsapp_message(whatsapp or phone, message)
                if success_wa:
                    self._log_notification(subscriber_id, earthquake_data, "whatsapp", "sent")
                    success = True
                else:
                    self._log_notification(subscriber_id, earthquake_data, "whatsapp", "failed")
            
            if method in ["sms", "both"]:
                success_sms = self.send_sms_message(phone, message)
                if success_sms:
                    self._log_notification(subscriber_id, earthquake_data, "sms", "sent")
                    success = True
                else:
                    self._log_notification(subscriber_id, earthquake_data, "sms", "failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending notification to subscriber {subscriber_id}: {e}")
            return False
        finally:
            conn.close()
    
    def _log_notification(self, subscriber_id: int, earthquake_data: Dict,
                         notification_type: str, status: str, error_msg: str = None):
        """Log notification attempt to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sent_notifications 
            (subscriber_id, prediction_date, earthquake_data, notification_type, 
             status, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (subscriber_id, earthquake_data['prediction_date'],
              json.dumps(earthquake_data), notification_type, status, error_msg))
        
        conn.commit()
        conn.close()
    
    def process_daily_notifications(self, target_date: date = None):
        """Process and send daily earthquake prediction notifications"""
        if target_date is None:
            target_date = date.today()
        
        logger.info(f"Processing notifications for {target_date}")
        
        # Load prediction data
        prediction_files = [
            "data/future_earthquake_predictions_india_25years_2025_2050.csv",
            "data/future_earthquake_predictions_100years.csv"
        ]
        
        all_predictions = pd.DataFrame()
        
        for file_path in prediction_files:
            if os.path.exists(file_path):
                df = self.load_prediction_data(file_path)
                all_predictions = pd.concat([all_predictions, df], ignore_index=True)
        
        if all_predictions.empty:
            logger.warning("No prediction data found")
            return
        
        # Filter predictions for notifications
        notification_predictions = self.filter_predictions_for_notifications(
            all_predictions, target_date
        )
        
        if notification_predictions.empty:
            logger.info(f"No significant predictions for {target_date}")
            return
        
        # Get active subscribers
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM notification_subscribers WHERE active = 1')
        subscriber_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # Send notifications for each significant prediction
        for _, prediction in notification_predictions.iterrows():
            earthquake_data = prediction.to_dict()
            
            for subscriber_id in subscriber_ids:
                try:
                    success = self.send_notification_to_subscriber(
                        subscriber_id, earthquake_data, "daily_summary"
                    )
                    if success:
                        logger.info(f"Notification sent to subscriber {subscriber_id}")
                    
                    # Small delay between notifications
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error sending to subscriber {subscriber_id}: {e}")
        
        logger.info(f"Completed processing notifications for {target_date}")
    
    def get_subscribers(self) -> pd.DataFrame:
        """Get list of all subscribers"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('''
            SELECT id, name, phone_number, whatsapp_number, preferred_method,
                   min_magnitude, regions, notification_types, created_at, active
            FROM notification_subscribers
            ORDER BY created_at DESC
        ''', conn)
        conn.close()
        return df
    
    def get_notification_history(self, days: int = 30) -> pd.DataFrame:
        """Get notification history"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('''
            SELECT sn.*, ns.name, ns.phone_number
            FROM sent_notifications sn
            JOIN notification_subscribers ns ON sn.subscriber_id = ns.id
            WHERE sn.sent_at >= datetime('now', '-{} days')
            ORDER BY sn.sent_at DESC
        '''.format(days), conn)
        conn.close()
        return df

# Initialize global notification system
notification_system = EarthquakeNotificationSystem()
