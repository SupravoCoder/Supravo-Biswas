# 📱 Bhukamp Earthquake Notification System

A comprehensive notification system that sends WhatsApp and SMS alerts for earthquake predictions from PINN and Random Forest models.

## 🌟 Features

### 📲 Multi-Channel Notifications
- **WhatsApp**: Using UltraMsg or Twilio APIs
- **SMS**: Using TextBelt or Twilio APIs
- **Flexible Preferences**: Users can choose WhatsApp, SMS, or both

### 🎯 Smart Filtering
- **Magnitude Thresholds**: Customizable minimum magnitude alerts
- **Regional Filters**: Subscribe to specific regions (Himalayan, Central, South, West, East)
- **Risk Categories**: High risk, medium risk, and daily summary options

### 🤖 AI Model Integration
- **PINN Predictions**: Physics-Informed Neural Network forecasts
- **Random Forest**: Machine learning predictions
- **Real-time Processing**: Automated daily notifications

### 📊 Management Dashboard
- Subscriber management
- Notification analytics
- API configuration
- Test notifications
- Daily prediction viewer

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Demo
```bash
python demo_notifications.py
```

### 3. Access the Dashboard
```bash
streamlit run pages/Earthquake_Notifications.py
```

## ⚙️ API Configuration

### WhatsApp APIs

#### UltraMsg (Recommended)
1. Visit [ultramsg.com](https://ultramsg.com)
2. Create account and connect WhatsApp
3. Get Instance ID and Token
4. Configure in the dashboard

#### Twilio WhatsApp
1. Visit [twilio.com](https://twilio.com)
2. Apply for WhatsApp Business API
3. Get Account SID, Auth Token, and WhatsApp number
4. Configure in the dashboard

### SMS APIs

#### TextBelt (Free Tier)
- Free: Use API key "textbelt" (1 SMS/day)
- Paid: Purchase API key for unlimited usage

#### Twilio SMS
1. Get Account SID and Auth Token from Twilio
2. Purchase a phone number
3. Configure in the dashboard

## 📋 Usage Examples

### Adding Subscribers Programmatically
```python
from earthquake_notifications import notification_system

# Add a subscriber
subscriber_id = notification_system.add_subscriber(
    name="Dr. John Doe",
    phone_number="+1234567890",
    whatsapp_number="+1234567890",
    notification_types=["high_risk", "medium_risk"],
    preferred_method="both",
    min_magnitude=4.5,
    regions=["Himalayan", "Central"]
)
```

### Sending Manual Notifications
```python
# Send WhatsApp message
success = notification_system.send_whatsapp_message(
    phone_number="+1234567890",
    message="Earthquake alert message"
)

# Send SMS
success = notification_system.send_sms_message(
    phone_number="+1234567890", 
    message="Earthquake alert message"
)
```

### Processing Daily Notifications
```python
from datetime import date

# Process notifications for today
notification_system.process_daily_notifications(date.today())
```

## 🔄 Automated Scheduling

### Run Scheduler
```bash
python notification_scheduler.py
```

### Schedule Configuration
- **Daily Notifications**: 7:00 AM IST
- **Weekly Summary**: Sunday 8:00 AM IST  
- **High-Priority Checks**: Every 3 hours

### Background Integration
```python
from notification_scheduler import run_scheduler_in_background

# Start scheduler in background
scheduler_thread = run_scheduler_in_background()
```

## 📁 File Structure

```
myproject/
├── earthquake_notifications.py      # Core notification system
├── pages/Earthquake_Notifications.py # Streamlit dashboard
├── notification_scheduler.py        # Automated scheduling
├── demo_notifications.py           # Demo and testing
├── earthquake_notifications.db     # SQLite database
└── earthquake_notifications.log    # Log file
```

## 🗄️ Database Schema

### Subscribers Table
- ID, name, phone numbers
- Notification preferences
- Regional and magnitude filters
- Active status and creation date

### Notifications Log
- Sent notifications history
- Success/failure status
- Error messages and timestamps

### Prediction Alerts
- Earthquake prediction data
- Alert status and metadata

## 🔧 Configuration Options

### Notification Types
- `high_risk`: Magnitude ≥ 5.0 or high probability
- `medium_risk`: Magnitude 4.0-4.9 or medium probability  
- `daily_summary`: Daily prediction summary

### Regional Zones
- `Himalayan`: Northern India, Kashmir region
- `Central`: Central India plains
- `South`: Southern India
- `West`: Western India, Gujarat region
- `East`: Eastern India, Bengal region

### Preferred Methods
- `whatsapp`: WhatsApp only
- `sms`: SMS only
- `both`: WhatsApp and SMS

## 📱 Message Templates

### Alert Message
```
🚨 EARTHQUAKE PREDICTION ALERT

⚠️ High Risk Earthquake Predicted
📅 Date: 2025-07-11
📍 Region: Himalayan, India
📊 Magnitude: 5.2
🎯 Probability: 72.0%
🤖 Model: PINN-25Year

📍 Coordinates: 30.32°N, 78.03°E

⚠️ Preparedness Recommendations:
• Keep emergency kit ready
• Review evacuation plans
• Stay informed through official channels

🌍 Bhukamp - Earthquake Forecasting for India
```

### Daily Summary
```
🌍 Bhukamp Daily Earthquake Forecast - 2025-07-11

⚠️ Medium Risk Prediction
📍 Location: Central, India
📊 Magnitude: 4.3
🎯 Probability: 45.0%
🤖 Model: Random Forest
📍 Coordinates: 23.26°N, 77.41°E

*About Bhukamp*: AI-powered earthquake forecasting 
for India using PINN and Random Forest models.

Stay safe! 🙏
Team Bhukamp
```

## 🔍 Monitoring and Analytics

### Dashboard Features
- Subscriber count and preferences
- Notification success rates
- Method distribution (WhatsApp vs SMS)
- Recent notification history
- Failed notification tracking

### Logging
- All notifications logged to `earthquake_notifications.log`
- Database tracking of all activities
- Error reporting and debugging

## 🚨 Error Handling

### Common Issues
1. **API Configuration**: Ensure all credentials are correct
2. **Phone Number Format**: Use international format (+country code)
3. **Rate Limits**: Some APIs have sending limits
4. **Network Issues**: Handle timeouts gracefully

### Debugging
- Check log file for detailed error messages
- Verify API credentials in dashboard
- Test with demo script first
- Use test notification feature

## 🔐 Security Considerations

### API Keys
- Store credentials securely
- Use environment variables in production
- Rotate keys regularly

### Phone Numbers
- Validate phone number formats
- Respect user privacy and consent
- Provide unsubscribe options

### Data Protection
- SQLite database for local storage
- No cloud data transmission (except APIs)
- User consent for notifications

## 🎯 Production Deployment

### Server Requirements
- Python 3.8+
- SQLite database
- Internet connection for APIs
- Scheduled task runner (cron/systemd)

### Environment Setup
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3-pip sqlite3

# Install Python dependencies
pip install -r requirements.txt

# Set up service
sudo systemctl enable bhukamp-notifications.service
```

### Monitoring
- Set up log rotation
- Monitor API usage and costs
- Track notification delivery rates
- Regular database backups

## 📞 Support

### API Support
- **UltraMsg**: [Support Documentation](https://docs.ultramsg.com)
- **Twilio**: [Help Center](https://support.twilio.com)
- **TextBelt**: [API Documentation](https://textbelt.com/docs)

### Bhukamp Team
- Technical support for notification system
- Feature requests and bug reports
- Integration assistance

## 🔄 Updates and Maintenance

### Regular Tasks
- Update prediction models
- Monitor API changes
- Review subscriber preferences
- Backup notification database

### Feature Roadmap
- Email notifications
- Mobile app integration
- Advanced filtering options
- Multi-language message templates
- Integration with emergency services

---

© 2025 Bhukamp Team - Earthquake Prediction Notifications for India
