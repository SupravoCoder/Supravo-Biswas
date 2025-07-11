import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import json
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from earthquake_notifications import notification_system

# Page configuration
st.set_page_config(
    page_title="Earthquake Notifications - Bhukamp",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply consistent theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;700&display=swap');
    
    @keyframes smoothGradient {
        0% { background-position: 0% 50%; }
        25% { background-position: 50% 0%; }
        50% { background-position: 100% 50%; }
        75% { background-position: 50% 100%; }
        100% { background-position: 0% 50%; }
    }
    
    html, body, .stApp {
        height: 100%;
        font-family: 'Roboto', sans-serif;
        background: linear-gradient(-45deg, #1b4332, #2d6a4f, #1f4e79, #40916c, #2563eb, #52b788, #3b82f6);
        background-size: 400% 400%;
        animation: smoothGradient 25s ease infinite;
        color: #f8f8f8;
    }
    
    .glass-container {
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(15px);
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        border: 1px solid rgba(255, 255, 255, 0.18);
        margin-bottom: 1rem;
    }
    
    .notification-card {
        background: rgba(255, 255, 255, 0.15);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #52b788;
    }
    
    .api-config-card {
        background: rgba(52, 183, 136, 0.2);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid rgba(52, 183, 136, 0.3);
    }
    
    .footer {
        text-align: center;
        font-size: 0.85em;
        color: #cccccc;
        margin-top: 40px;
    }
    
    section[data-testid="stSidebar"] {
        background: linear-gradient(-45deg, #1b4332, #2d6a4f, #1f4e79, #40916c, #2563eb, #52b788, #3b82f6);
        color: #f8f8f8;
    }
    
    section[data-testid="stSidebar"] * {
        color: #f8f8f8 !important;
    }
    
    .stSelectbox label, .stTextInput label, .stTextArea label {
        color: #f8f8f8 !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.markdown("## 📱 Notification Management")
    
    page_options = [
        "📝 Subscribe to Alerts",
        "⚙️ API Configuration", 
        "👥 Manage Subscribers",
        "📊 Notification Analytics",
        "🔔 Send Test Notification",
        "📅 Daily Predictions"
    ]
    
    selected_page = st.selectbox("Select Page", page_options, key="nav_select")
    
    st.markdown("---")
    st.markdown("### 🌍 Bhukamp Navigation")
    st.info("💡 Use the sidebar or browser navigation to access other pages of Bhukamp")
    st.markdown("- 🏠 **Main Dashboard**: Close this tab and go back to main app")
    st.markdown("- 📊 **Historical Analysis**: Available in main app navigation")
    st.markdown("- 🔮 **ML Predictions**: Available in main app navigation")

# Header
st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
st.markdown("# 📱 Earthquake Notification System")
st.markdown("### *Real-time WhatsApp & SMS alerts for earthquake predictions*")
st.markdown("Configure and manage notifications for PINN and Random Forest earthquake predictions across India.")
st.markdown("</div>", unsafe_allow_html=True)

# Main content based on selected page
if selected_page == "📝 Subscribe to Alerts":
    st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
    st.markdown("## 📝 Subscribe to Earthquake Alerts")
    
    with st.form("subscribe_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name *", placeholder="Enter your full name")
            phone = st.text_input("Phone Number *", placeholder="+91XXXXXXXXXX")
            whatsapp = st.text_input("WhatsApp Number", placeholder="Same as phone if blank")
            
        with col2:
            preferred_method = st.selectbox(
                "Preferred Notification Method", 
                ["both", "whatsapp", "sms"],
                format_func=lambda x: {
                    "both": "📱 WhatsApp + SMS",
                    "whatsapp": "💬 WhatsApp Only", 
                    "sms": "📨 SMS Only"
                }[x]
            )
            
            min_magnitude = st.slider(
                "Minimum Magnitude Alert", 
                min_value=2.0, max_value=8.0, value=4.0, step=0.1,
                help="Only receive alerts for earthquakes above this magnitude"
            )
            
            regions = st.multiselect(
                "Regions of Interest",
                ["Himalayan", "Central", "South", "West", "East"],
                default=["Himalayan", "Central", "South", "West", "East"],
                help="Select regions you want to monitor"
            )
        
        notification_types = st.multiselect(
            "Alert Types",
            ["high_risk", "medium_risk", "daily_summary"],
            default=["high_risk", "medium_risk"],
            format_func=lambda x: {
                "high_risk": "🚨 High Risk Alerts",
                "medium_risk": "⚠️ Medium Risk Alerts",
                "daily_summary": "📅 Daily Summary"
            }[x]
        )
        
        terms = st.checkbox("I agree to receive earthquake prediction notifications and understand these are AI-based predictions.")
        
        submitted = st.form_submit_button("🔔 Subscribe to Alerts", use_container_width=True)
        
        if submitted:
            if not all([name, phone, terms]):
                st.error("Please fill all required fields and accept terms.")
            else:
                try:
                    subscriber_id = notification_system.add_subscriber(
                        name=name,
                        phone_number=phone,
                        whatsapp_number=whatsapp or phone,
                        notification_types=notification_types,
                        preferred_method=preferred_method,
                        min_magnitude=min_magnitude,
                        regions=regions
                    )
                    
                    if subscriber_id:
                        st.success(f"✅ Successfully subscribed! Subscriber ID: {subscriber_id}")
                        st.info("📱 You will start receiving notifications based on your preferences.")
                    else:
                        st.error("❌ Subscription failed. Phone number might already be registered.")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    st.markdown("</div>", unsafe_allow_html=True)

elif selected_page == "⚙️ API Configuration":
    st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
    st.markdown("## ⚙️ API Configuration")
    st.markdown("Configure WhatsApp and SMS API providers for sending notifications.")
    
    tab1, tab2 = st.tabs(["💬 WhatsApp APIs", "📨 SMS APIs"])
    
    with tab1:
        st.markdown("### Configure WhatsApp API Providers")
        
        # UltraMsg Configuration
        st.markdown("<div class='api-config-card'>", unsafe_allow_html=True)
        st.markdown("#### 🔵 UltraMsg (Recommended)")
        st.markdown("Free tier available, easy setup")
        
        with st.expander("Configure UltraMsg"):
            ultramsg_token = st.text_input("UltraMsg Token", type="password", key="ultramsg_token")
            ultramsg_instance = st.text_input("Instance ID", key="ultramsg_instance")
            
            if st.button("Save UltraMsg Config", key="save_ultramsg"):
                if ultramsg_token and ultramsg_instance:
                    notification_system.configure_whatsapp_api(
                        "ultramsg",
                        token=ultramsg_token,
                        instance_id=ultramsg_instance
                    )
                    st.success("✅ UltraMsg configuration saved!")
                else:
                    st.error("❌ Please fill all fields")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Twilio Configuration
        st.markdown("<div class='api-config-card'>", unsafe_allow_html=True)
        st.markdown("#### 🟢 Twilio WhatsApp")
        st.markdown("Enterprise grade, requires approval")
        
        with st.expander("Configure Twilio WhatsApp"):
            twilio_sid = st.text_input("Account SID", type="password", key="twilio_wa_sid")
            twilio_token = st.text_input("Auth Token", type="password", key="twilio_wa_token")
            twilio_whatsapp_number = st.text_input("WhatsApp Number", key="twilio_wa_number", placeholder="+14155238886")
            
            if st.button("Save Twilio WhatsApp Config", key="save_twilio_wa"):
                if all([twilio_sid, twilio_token, twilio_whatsapp_number]):
                    notification_system.configure_whatsapp_api(
                        "twilio",
                        account_sid=twilio_sid,
                        auth_token=twilio_token,
                        whatsapp_number=twilio_whatsapp_number
                    )
                    st.success("✅ Twilio WhatsApp configuration saved!")
                else:
                    st.error("❌ Please fill all fields")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### Configure SMS API Providers")
        
        # TextBelt Configuration
        st.markdown("<div class='api-config-card'>", unsafe_allow_html=True)
        st.markdown("#### 📱 TextBelt")
        st.markdown("Simple SMS API, free tier available")
        
        with st.expander("Configure TextBelt"):
            textbelt_key = st.text_input("TextBelt API Key", type="password", key="textbelt_key", 
                                       help="Use 'textbelt' for free tier (1 SMS/day)")
            
            if st.button("Save TextBelt Config", key="save_textbelt"):
                notification_system.configure_sms_api(
                    "textbelt",
                    api_key=textbelt_key or "textbelt"
                )
                st.success("✅ TextBelt configuration saved!")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Twilio SMS Configuration
        st.markdown("<div class='api-config-card'>", unsafe_allow_html=True)
        st.markdown("#### 📞 Twilio SMS")
        st.markdown("Reliable SMS delivery worldwide")
        
        with st.expander("Configure Twilio SMS"):
            twilio_sms_sid = st.text_input("Account SID", type="password", key="twilio_sms_sid")
            twilio_sms_token = st.text_input("Auth Token", type="password", key="twilio_sms_token")
            twilio_phone_number = st.text_input("Phone Number", key="twilio_sms_number", placeholder="+1234567890")
            
            if st.button("Save Twilio SMS Config", key="save_twilio_sms"):
                if all([twilio_sms_sid, twilio_sms_token, twilio_phone_number]):
                    notification_system.configure_sms_api(
                        "twilio",
                        account_sid=twilio_sms_sid,
                        auth_token=twilio_sms_token,
                        phone_number=twilio_phone_number
                    )
                    st.success("✅ Twilio SMS configuration saved!")
                else:
                    st.error("❌ Please fill all fields")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Setup Instructions
    st.markdown("### 📋 Setup Instructions")
    
    with st.expander("🔍 How to get API credentials"):
        st.markdown("""
        #### UltraMsg (WhatsApp)
        1. Visit [ultramsg.com](https://ultramsg.com)
        2. Create account and connect your WhatsApp
        3. Get your Instance ID and Token from dashboard
        
        #### Twilio (WhatsApp & SMS)
        1. Visit [twilio.com](https://twilio.com)
        2. Create account and verify phone number
        3. Get Account SID and Auth Token from console
        4. For WhatsApp: Apply for WhatsApp Business API
        
        #### TextBelt (SMS)
        1. Visit [textbelt.com](https://textbelt.com)
        2. Use 'textbelt' for free tier (1 SMS/day)
        3. Purchase API key for unlimited usage
        """)
    
    st.markdown("</div>", unsafe_allow_html=True)

elif selected_page == "👥 Manage Subscribers":
    st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
    st.markdown("## 👥 Manage Subscribers")
    
    # Get subscribers data
    subscribers_df = notification_system.get_subscribers()
    
    if not subscribers_df.empty:
        st.markdown(f"### 📊 Total Subscribers: {len(subscribers_df)}")
        
        # Subscriber statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            active_count = len(subscribers_df[subscribers_df['active'] == 1])
            st.metric("Active Subscribers", active_count)
        
        with col2:
            whatsapp_count = len(subscribers_df[subscribers_df['preferred_method'].isin(['whatsapp', 'both'])])
            st.metric("WhatsApp Users", whatsapp_count)
        
        with col3:
            sms_count = len(subscribers_df[subscribers_df['preferred_method'].isin(['sms', 'both'])])
            st.metric("SMS Users", sms_count)
        
        with col4:
            avg_magnitude = subscribers_df['min_magnitude'].mean()
            st.metric("Avg Magnitude Threshold", f"{avg_magnitude:.1f}")
        
        # Subscribers table
        st.markdown("### 📋 Subscriber List")
        
        # Parse JSON columns for better display
        display_df = subscribers_df.copy()
        display_df['regions'] = display_df['regions'].apply(lambda x: ', '.join(json.loads(x)) if pd.notna(x) else '')
        display_df['notification_types'] = display_df['notification_types'].apply(lambda x: ', '.join(json.loads(x)) if pd.notna(x) else '')
        display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        
        st.dataframe(
            display_df[['id', 'name', 'phone_number', 'preferred_method', 'min_magnitude', 'regions', 'active', 'created_at']],
            use_container_width=True
        )
        
        # Subscriber management actions
        st.markdown("### ⚙️ Subscriber Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Deactivate subscriber
            st.markdown("#### 🔴 Deactivate Subscriber")
            subscriber_id_deactivate = st.selectbox(
                "Select Subscriber to Deactivate",
                options=subscribers_df[subscribers_df['active'] == 1]['id'].tolist(),
                format_func=lambda x: f"ID {x}: {subscribers_df[subscribers_df['id'] == x]['name'].iloc[0]}",
                key="deactivate_select"
            )
            
            if st.button("🔴 Deactivate", key="deactivate_btn"):
                # TODO: Implement deactivate functionality
                st.warning("⚠️ Deactivation feature coming soon!")
        
        with col2:
            # Send individual notification
            st.markdown("#### 📤 Send Test Notification")
            subscriber_id_test = st.selectbox(
                "Select Subscriber for Test",
                options=subscribers_df[subscribers_df['active'] == 1]['id'].tolist(),
                format_func=lambda x: f"ID {x}: {subscribers_df[subscribers_df['id'] == x]['name'].iloc[0]}",
                key="test_select"
            )
            
            if st.button("📤 Send Test", key="test_btn"):
                # TODO: Implement test notification
                st.info("📱 Test notification feature coming soon!")
    
    else:
        st.info("📝 No subscribers yet. Use the 'Subscribe to Alerts' page to add subscribers.")
    
    st.markdown("</div>", unsafe_allow_html=True)

elif selected_page == "📊 Notification Analytics":
    st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
    st.markdown("## 📊 Notification Analytics")
    
    # Get notification history
    history_df = notification_system.get_notification_history(days=30)
    
    if not history_df.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_sent = len(history_df)
            st.metric("Total Notifications", total_sent)
        
        with col2:
            success_rate = len(history_df[history_df['status'] == 'sent']) / len(history_df) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
        
        with col3:
            whatsapp_count = len(history_df[history_df['notification_type'] == 'whatsapp'])
            st.metric("WhatsApp Sent", whatsapp_count)
        
        with col4:
            sms_count = len(history_df[history_df['notification_type'] == 'sms'])
            st.metric("SMS Sent", sms_count)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Notifications by method
            method_counts = history_df['notification_type'].value_counts()
            fig1 = px.pie(
                values=method_counts.values,
                names=method_counts.index,
                title="Notifications by Method"
            )
            fig1.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Status distribution
            status_counts = history_df['status'].value_counts()
            fig2 = px.bar(
                x=status_counts.index,
                y=status_counts.values,
                title="Notification Status Distribution"
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Recent notifications table
        st.markdown("### 📋 Recent Notifications")
        display_history = history_df.copy()
        display_history['sent_at'] = pd.to_datetime(display_history['sent_at']).dt.strftime('%Y-%m-%d %H:%M')
        
        st.dataframe(
            display_history[['sent_at', 'name', 'phone_number', 'notification_type', 'status']].head(20),
            use_container_width=True
        )
    
    else:
        st.info("📈 No notification history available yet.")
    
    st.markdown("</div>", unsafe_allow_html=True)

elif selected_page == "🔔 Send Test Notification":
    st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
    st.markdown("## 🔔 Send Test Notification")
    
    with st.form("test_notification_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            test_phone = st.text_input("Phone Number", placeholder="+91XXXXXXXXXX")
            test_method = st.selectbox("Method", ["whatsapp", "sms"])
        
        with col2:
            test_magnitude = st.slider("Test Magnitude", 2.0, 8.0, 5.0, 0.1)
            test_region = st.selectbox("Test Region", ["Himalayan", "Central", "South", "West", "East"])
        
        test_message_type = st.selectbox(
            "Message Type", 
            ["alert", "daily_summary"],
            format_func=lambda x: "🚨 Alert" if x == "alert" else "📅 Daily Summary"
        )
        
        # Create test earthquake data
        test_earthquake = {
            'prediction_date': str(date.today()),
            'predicted_magnitude': test_magnitude,
            'earthquake_probability': 0.65,
            'region': 'India',
            'regional_zone': test_region,
            'model_type': 'Test-Model',
            'risk_category': 'High' if test_magnitude >= 5.0 else 'Medium',
            'latitude': 28.6139,
            'longitude': 77.2090
        }
        
        # Preview message
        st.markdown("### 📱 Message Preview")
        preview_message = notification_system.generate_notification_message(
            test_earthquake, test_message_type
        )
        st.text_area("Message Content", preview_message, height=200, disabled=True)
        
        sent_test = st.form_submit_button("📤 Send Test Notification", use_container_width=True)
        
        if sent_test:
            if not test_phone:
                st.error("❌ Please enter a phone number")
            else:
                try:
                    if test_method == "whatsapp":
                        success = notification_system.send_whatsapp_message(test_phone, preview_message)
                    else:
                        success = notification_system.send_sms_message(test_phone, preview_message)
                    
                    if success:
                        st.success("✅ Test notification sent successfully!")
                    else:
                        st.error("❌ Failed to send test notification. Check API configuration.")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    st.markdown("</div>", unsafe_allow_html=True)

elif selected_page == "📅 Daily Predictions":
    st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
    st.markdown("## 📅 Daily Earthquake Predictions")
    
    # Date selector
    selected_date = st.date_input(
        "Select Date for Predictions",
        value=date.today(),
        min_value=date.today(),
        max_value=date.today() + timedelta(days=365)
    )
    
    if st.button("🔍 Load Predictions", use_container_width=True):
        # Load prediction data (simplified version)
        try:
            # This would load from your actual prediction files
            st.info("📊 Loading earthquake predictions...")
            
            # For demo purposes, create sample data
            sample_predictions = pd.DataFrame({
                'time': [f"{selected_date} 10:30:00", f"{selected_date} 15:45:00"],
                'magnitude': [4.2, 5.1],
                'region': ['Central India', 'Himalayan Region'],
                'probability': [0.35, 0.68],
                'risk': ['Medium', 'High'],
                'model': ['Random Forest', 'PINN']
            })
            
            if not sample_predictions.empty:
                st.markdown(f"### 📋 Predictions for {selected_date}")
                
                for _, pred in sample_predictions.iterrows():
                    risk_color = "🔴" if pred['risk'] == 'High' else "🟡"
                    
                    st.markdown(f"""
                    <div class='notification-card'>
                        <h4>{risk_color} {pred['risk']} Risk Prediction</h4>
                        <p><strong>📍 Region:</strong> {pred['region']}</p>
                        <p><strong>📊 Magnitude:</strong> {pred['magnitude']}</p>
                        <p><strong>🎯 Probability:</strong> {pred['probability']:.1%}</p>
                        <p><strong>🤖 Model:</strong> {pred['model']}</p>
                        <p><strong>⏰ Time:</strong> {pred['time']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Manual notification trigger
                st.markdown("### 📤 Send Notifications")
                
                if st.button("🚀 Send Notifications to All Subscribers"):
                    try:
                        notification_system.process_daily_notifications(selected_date)
                        st.success("✅ Notifications sent to all subscribers!")
                    except Exception as e:
                        st.error(f"❌ Error sending notifications: {str(e)}")
            
            else:
                st.info("📭 No significant predictions found for this date.")
                
        except Exception as e:
            st.error(f"❌ Error loading predictions: {str(e)}")
    
    # Scheduled notifications info
    st.markdown("### ⏰ Automated Scheduling")
    st.info("""
    🤖 **Automated Daily Notifications**
    
    The system can be configured to automatically send daily predictions:
    - **Time**: Every day at 7:00 AM IST
    - **Content**: High and medium risk predictions for the day
    - **Recipients**: All active subscribers matching criteria
    
    To enable automated scheduling, deploy the system with a task scheduler.
    """)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("<div class='footer'>© 2025 Bhukamp - भूकंप | Earthquake Prediction Notifications | Built with ❤️ from Team Bhukamp</div>", unsafe_allow_html=True)
