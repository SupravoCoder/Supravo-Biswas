"""
Demo script for Earthquake Notification System
Shows how to use the notification system with sample data
"""

from earthquake_notifications import notification_system
from datetime import datetime, date
import json

def demo_notification_system():
    """Demonstrate the earthquake notification system"""
    print("🌍 Bhukamp Earthquake Notification System Demo")
    print("=" * 50)
    
    # Add sample subscribers
    print("\n📝 Adding sample subscribers...")
    
    subscriber1 = notification_system.add_subscriber(
        name="Dr. Rajesh Kumar",
        phone_number="+919876543210",
        whatsapp_number="+919876543210",
        notification_types=["high_risk", "medium_risk", "daily_summary"],
        preferred_method="both",
        min_magnitude=4.0,
        regions=["Himalayan", "Central"]
    )
    
    subscriber2 = notification_system.add_subscriber(
        name="Prof. Priya Sharma",
        phone_number="+919123456789",
        whatsapp_number="+919123456789",
        notification_types=["high_risk"],
        preferred_method="whatsapp",
        min_magnitude=5.0,
        regions=["South", "West"]
    )
    
    if subscriber1:
        print(f"✅ Added subscriber 1: Dr. Rajesh Kumar (ID: {subscriber1})")
    if subscriber2:
        print(f"✅ Added subscriber 2: Prof. Priya Sharma (ID: {subscriber2})")
    
    # Show current subscribers
    print("\n👥 Current subscribers:")
    subscribers = notification_system.get_subscribers()
    for _, sub in subscribers.iterrows():
        print(f"- ID {sub['id']}: {sub['name']} - {sub['preferred_method']}")
    
    # Create sample earthquake prediction
    print("\n🔮 Creating sample earthquake prediction...")
    
    sample_earthquake = {
        'prediction_date': str(date.today()),
        'predicted_magnitude': 5.2,
        'earthquake_probability': 0.72,
        'region': 'India',
        'regional_zone': 'Himalayan',
        'model_type': 'PINN-25Year',
        'risk_category': 'High',
        'latitude': 30.3165,
        'longitude': 78.0322,
        'depth': 15.5,
        'prediction_confidence': 0.85
    }
    
    print(f"📊 Sample prediction: M{sample_earthquake['predicted_magnitude']} in {sample_earthquake['regional_zone']}")
    
    # Generate notification message
    print("\n📱 Generating notification message...")
    message = notification_system.generate_notification_message(sample_earthquake, "alert")
    print("\nMessage preview:")
    print("-" * 40)
    print(message)
    print("-" * 40)
    
    # Configure demo APIs (using free services)
    print("\n⚙️ Configuring APIs...")
    
    # TextBelt for SMS (free tier)
    notification_system.configure_sms_api(
        "textbelt",
        api_key="textbelt"  # Free tier key
    )
    print("✅ SMS API configured (TextBelt - free tier)")
    
    # Note: WhatsApp APIs require actual credentials
    print("⚠️ WhatsApp API requires setup with UltraMsg or Twilio")
    
    print("\n🚀 Notification system is ready!")
    print("\nTo send actual notifications:")
    print("1. Configure WhatsApp API (UltraMsg recommended)")
    print("2. Add real phone numbers as subscribers")
    print("3. Run notification_system.process_daily_notifications()")
    
    print("\n📋 Available methods:")
    print("- notification_system.send_sms_message(phone, message)")
    print("- notification_system.send_whatsapp_message(phone, message)")
    print("- notification_system.process_daily_notifications(date)")
    
    return notification_system

def create_sample_predictions():
    """Create sample prediction data for demo"""
    import pandas as pd
    
    sample_data = [
        {
            'prediction_date': '2025-07-11',
            'predicted_magnitude': 5.1,
            'earthquake_probability': 0.68,
            'region': 'India',
            'regional_zone': 'Himalayan',
            'model_type': 'PINN-25Year',
            'risk_category': 'High',
            'latitude': 30.3165,
            'longitude': 78.0322
        },
        {
            'prediction_date': '2025-07-11',
            'predicted_magnitude': 4.3,
            'earthquake_probability': 0.45,
            'region': 'India',
            'regional_zone': 'Central',
            'model_type': 'Random Forest',
            'risk_category': 'Medium',
            'latitude': 23.2599,
            'longitude': 77.4126
        },
        {
            'prediction_date': '2025-07-12',
            'predicted_magnitude': 5.8,
            'earthquake_probability': 0.82,
            'region': 'India',
            'regional_zone': 'South',
            'model_type': 'PINN-25Year',
            'risk_category': 'High',
            'latitude': 11.1271,
            'longitude': 78.6569
        }
    ]
    
    df = pd.DataFrame(sample_data)
    df.to_csv('data/sample_predictions_demo.csv', index=False)
    print("📁 Created sample prediction data: data/sample_predictions_demo.csv")
    
    return df

if __name__ == "__main__":
    # Run the demo
    notification_system = demo_notification_system()
    
    # Create sample prediction data
    print("\n📁 Creating sample prediction data...")
    sample_predictions = create_sample_predictions()
    
    print("\n🎉 Demo completed successfully!")
    print("\nNext steps:")
    print("1. Configure your API credentials in the Streamlit app")
    print("2. Add real subscribers")
    print("3. Set up the scheduler for automated notifications")
    print("4. Run: python notification_scheduler.py")
