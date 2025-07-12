import streamlit as st
import asyncio
import logging
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, Any, Optional
import os
import csv

USER_CSV = "data/users.csv"

def ensure_user_csv():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(USER_CSV):
        with open(USER_CSV, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["id", "name", "phone"])

def get_users():
    ensure_user_csv()
    users = {}
    with open(USER_CSV, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            users[row["id"]] = {"name": row["name"], "phone": row["phone"]}
    return users

def add_user(user_id, name, phone):
    ensure_user_csv()
    with open(USER_CSV, "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([user_id, name, phone])

def login_signup():
    st.title("Login / Signup")
    user_id = st.text_input("Aayushman Bharat ID / Reference Number")
    name = st.text_input("Name")
    phone = st.text_input("Phone Number")
    action = st.radio("Action", ["Login", "Sign Up"])
    users = get_users()

    if st.button("Continue"):
        if action == "Login":
            if user_id in users:
                st.session_state["user_id"] = user_id
                st.session_state["user_name"] = users[user_id]["name"]
                st.session_state["user_phone"] = users[user_id]["phone"]
                st.success(f"Welcome back, {users[user_id]['name']}!")
                st.rerun()
            else:
                st.error("User not found. Please sign up first.")
        else:
            if user_id in users:
                st.warning("User already exists. Please log in.")
            elif not user_id or not name or not phone:
                st.error("Please fill all fields.")
            else:
                add_user(user_id, name, phone)
                st.session_state["user_id"] = user_id
                st.session_state["user_name"] = name
                st.session_state["user_phone"] = phone
                st.success("Signup successful! Welcome.")
                st.rerun()

if "user_id" not in st.session_state:
    login_signup()
    st.stop()
else:
    st.write(f"Logged in as: {st.session_state['user_id']}")


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our custom modules
from src.ai_agent import HealthcareAIAgent
from src.vitals_system import VitalsCollectionSystem
from src.multilingual_support import MultilingualSupport
from src.appointment_system import AppointmentSystem
from config.config import Config

# Page configuration
st.set_page_config(
    page_title="Intel AI Healthcare Kiosk",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'ai_agent' not in st.session_state:
    st.session_state.ai_agent = None
if 'vitals_system' not in st.session_state:
    st.session_state.vitals_system = VitalsCollectionSystem()
if 'multilingual' not in st.session_state:
    st.session_state.multilingual = MultilingualSupport()
if 'appointment_system' not in st.session_state:
    st.session_state.appointment_system = AppointmentSystem()
if 'language' not in st.session_state:
    st.session_state.language = 'en'
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'current_vitals' not in st.session_state:
    st.session_state.current_vitals = {}

def initialize_ai_agent():
    """Initialize the AI agent"""
    try:
        if st.session_state.ai_agent is None:
            st.session_state.ai_agent = HealthcareAIAgent()
        return True
    except Exception as e:
        st.error(f"Failed to initialize AI agent: {str(e)}")
        st.info("Please ensure your Google AI Studio API key is set in the .env file")
        return False

def display_medical_disclaimer():
    """Display medical disclaimer"""
    disclaimer = st.session_state.multilingual.get_translation(
        'medical_disclaimer', 
        st.session_state.language
    )
    
    st.warning(f"⚠️ **Medical Disclaimer**: {disclaimer}")

def language_selector():
    """Language selection component"""
    languages = st.session_state.multilingual.get_language_preferences()
    
    selected_lang = st.selectbox(
        "🌍 Select Language / भाषा चुनें / ಭಾಷೆ ಆಯ್ಕೆ ಮಾಡಿ",
        options=list(languages.keys()),
        format_func=lambda x: f"{languages[x]} ({x.upper()})",
        index=list(languages.keys()).index(st.session_state.language)
    )
    
    if selected_lang != st.session_state.language:
        st.session_state.language = selected_lang
        st.rerun()

def vitals_input_form():
    """Vitals input form"""
    st.subheader("📊 Vitals Collection")
    
    # Get vital definitions
    vital_defs = st.session_state.vitals_system.get_all_vital_definitions()
    
    # Group vitals by category
    categories = {}
    for vital_name, vital_def in vital_defs.items():
        category = vital_def['category']
        if category not in categories:
            categories[category] = []
        categories[category].append((vital_name, vital_def))
    
    collected_vitals = {}
    
    # Create tabs for each category
    category_tabs = st.tabs([cat.title().replace('_', ' ') for cat in categories.keys()])
    
    for tab, (category, vitals) in zip(category_tabs, categories.items()):
        with tab:
            cols = st.columns(2)
            for i, (vital_name, vital_def) in enumerate(vitals):
                col = cols[i % 2]
                
                with col:
                    # Translate vital name
                    display_name = st.session_state.multilingual.get_translation(
                        vital_name, st.session_state.language
                    )
                    
                    value = st.number_input(
                        f"{display_name} ({vital_def['unit']})",
                        min_value=0.0,
                        help=f"Normal range: {vital_def['normal_range'][0]} - {vital_def['normal_range'][1]} {vital_def['unit']}",
                        key=f"vital_{vital_name}"
                    )
                    
                    if value > 0:
                        # Validate the value
                        validation = st.session_state.vitals_system.validate_vital_value(vital_name, value)
                        if validation['valid']:
                            collected_vitals[vital_name] = value
                        else:
                            st.error(f"⚠️ {validation['error']}")
    
    if st.button("📈 Collect Vitals", type="primary"):
        if collected_vitals:
            # Collect vitals
            vital_signs = st.session_state.vitals_system.collect_multiple_vitals(collected_vitals)
            
            # Calculate derived vitals
            derived_vitals = st.session_state.vitals_system.calculate_derived_vitals()
            
            # Update session state
            st.session_state.current_vitals = {
                **{name: vs.value for name, vs in vital_signs.items()},
                **{name: vs.value for name, vs in derived_vitals.items()}
            }
            
            st.success(f"✅ Collected {len(vital_signs)} vitals successfully!")
            st.rerun()

            user_id = st.session_state["user_id"]
            today = datetime.now().strftime("%Y-%m-%d")
            vitals_file = f"data/vitals_{user_id}_{today}.csv"
            file_exists = os.path.exists(vitals_file)
            with open(vitals_file, "a", newline='') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["datetime"] + list(collected_vitals.keys()))
                writer.writerow([datetime.now().isoformat()] + list(collected_vitals.values()))

        else:
            st.warning("Please enter at least one vital sign measurement.")

def display_vitals_summary():
    """Display vitals summary and health score"""
    if not st.session_state.vitals_system.current_session:
        return
    
    st.subheader("📋 Vitals Summary")
    
    # Get health score
    health_score = st.session_state.vitals_system.get_health_score()
    
    # Display health score
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Health Score", f"{health_score['score']}/100", delta=None)
    
    with col2:
        st.metric("Grade", health_score['grade'])
    
    with col3:
        st.metric("Critical Vitals", health_score['critical_vitals'])
    
    # Get vitals summary
    summary = st.session_state.vitals_system.get_vitals_summary()
    
    # Display status breakdown
    if summary['status_counts']:
        fig = px.pie(
            values=list(summary['status_counts'].values()),
            names=list(summary['status_counts'].keys()),
            title="Vitals Status Distribution",
            color_discrete_map={
                'normal': 'green',
                'low': 'orange',
                'high': 'red',
                'critical': 'darkred'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Display critical and abnormal vitals
    if summary['critical_vitals']:
        st.error("🚨 Critical Vitals Detected:")
        for vital in summary['critical_vitals']:
            st.write(f"- **{vital['name']}**: {vital['value']} {vital['unit']} (Normal: {vital['normal_range'][0]}-{vital['normal_range'][1]})")
    
    if summary['abnormal_vitals']:
        st.warning("⚠️ Abnormal Vitals:")
        for vital in summary['abnormal_vitals']:
            st.write(f"- **{vital['name']}**: {vital['value']} {vital['unit']} - {vital['status'].title()}")

def chat_interface():
    """Chat interface for AI interaction"""
    st.subheader("💬 AI Health Assistant")
    
    # Chat history
    chat_container = st.container()
    
    with chat_container:
        for entry in st.session_state.conversation_history:
            with st.chat_message("user"):
                st.write(entry['user'])
            with st.chat_message("assistant"):
                st.write(entry['assistant'])
                if 'health_assessment' in entry:
                    st.info(f"**Assessment**: {entry['health_assessment']}")
                if 'recommendations' in entry and entry['recommendations']:
                    st.write("**Recommendations**:")
                    for rec in entry['recommendations']:
                        st.write(f"• {rec}")
    
    # Chat input
    user_input = st.chat_input("Ask me about your health concerns...")
    
    if user_input:
        # Add user message to history
        with st.chat_message("user"):
            st.write(user_input)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your health data..."):
                try:
                    # Generate response
                    response = asyncio.run(
                        st.session_state.ai_agent.generate_response(
                            user_input=user_input,
                            vitals_data=st.session_state.current_vitals,
                            language=st.session_state.language,
                            conversation_history=st.session_state.conversation_history
                        )
                    )
                    
                    # Display response
                    st.write(response['response'])
                    
                    if response.get('health_assessment'):
                        st.info(f"**Assessment**: {response['health_assessment']}")
                    
                    if response.get('risk_level'):
                        risk_color = {
                            'low': 'green',
                            'moderate': 'orange', 
                            'high': 'red',
                            'emergency': 'darkred'
                        }
                        color = risk_color.get(response['risk_level'], 'blue')
                        st.markdown(f"**Risk Level**: :{color}[{response['risk_level'].title()}]")
                    
                    if response.get('recommendations'):
                        st.write("**Recommendations**:")
                        for rec in response['recommendations']:
                            st.write(f"• {rec}")
                    
                    if response.get('next_steps'):
                        st.info(f"**Next Steps**: {response['next_steps']}")
                    
                    # Add to conversation history
                    conversation_entry = {
                        'user': user_input,
                        'assistant': response['response'],
                        'health_assessment': response.get('health_assessment', ''),
                        'recommendations': response.get('recommendations', []),
                        'timestamp': datetime.now().isoformat()
                    }
                    st.session_state.conversation_history.append(conversation_entry)
                    
                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")
        
        st.rerun()

def first_aid_section():
    """First aid guidance section"""
    st.subheader("🚑 First Aid Guidance")
    
    common_conditions = [
        "Heart Attack", "Stroke", "Choking", "Severe Bleeding", 
        "Burns", "Allergic Reaction", "Unconsciousness", "Seizure"
    ]
    
    selected_condition = st.selectbox(
        "Select a condition for first aid guidance:",
        [""] + common_conditions
    )
    
    if selected_condition:
        with st.spinner(f"Getting first aid guidance for {selected_condition}..."):
            try:
                guidance = st.session_state.ai_agent.get_first_aid_guidance(
                    condition=selected_condition,
                    language=st.session_state.language
                )
                
                st.write(guidance['response'])
                
                if guidance.get('recommendations'):
                    st.warning("**Immediate Actions**:")
                    for rec in guidance['recommendations']:
                        st.write(f"• {rec}")
                
            except Exception as e:
                st.error(f"Error getting first aid guidance: {str(e)}")

def appointment_booking_interface():
    """Appointment booking interface"""
    st.subheader("📅 Book Doctor Appointment")
    
    # Get available doctors
    doctors = st.session_state.appointment_system.get_doctors()
    
    if not doctors:
        st.error("No doctors available at the moment. Please try again later.")
        return
    
    # Doctor selection
    doctor_options = {f"{doc['name']} - {doc['specialty']}": doc['doctor_id'] for doc in doctors}
    selected_doctor_display = st.selectbox(
        "Select a Doctor:",
        [""] + list(doctor_options.keys())
    )
    
    if not selected_doctor_display:
        st.info("Please select a doctor to continue.")
        return
    
    selected_doctor_id = doctor_options[selected_doctor_display]
    selected_doctor = st.session_state.appointment_system.get_doctor_by_id(selected_doctor_id)
    
    # Display doctor information
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Doctor:** {selected_doctor['name']}")
        st.info(f"**Specialty:** {selected_doctor['specialty']}")
    with col2:
        st.info(f"**Available Days:** {selected_doctor['available_days']}")
        st.info(f"**Available Times:** {selected_doctor['available_times']}")
    
    # Date selection (today and next 30 days)
    min_date = datetime.now().date()  # Today
    max_date = datetime.now().date() + timedelta(days=30)  # Next 30 days
    
    st.info("📅 **Same-day appointments available!** For today's appointments, a 1-hour advance booking is required.")
    
    selected_date = st.date_input(
        "Select Appointment Date:",
        min_value=min_date,
        max_value=max_date,
        value=min_date
    )
    
    # Display booking information based on selected date
    if selected_date == datetime.now().date():
        st.success("🚀 **Same-day appointment** - Available slots start 1 hour from now")
    else:
        days_ahead = (selected_date - datetime.now().date()).days
        st.info(f"📅 **Future appointment** - Booking for {days_ahead} day(s) ahead")
    
    # Get available time slots for selected date
    available_slots = st.session_state.appointment_system.get_available_time_slots(
        selected_doctor_id, 
        datetime.combine(selected_date, datetime.min.time())
    )
    
    if not available_slots:
        if selected_date == datetime.now().date():
            st.warning("⏰ No available time slots for today. The doctor may not be available today or all slots are booked. Please try tomorrow.")
        else:
            st.warning("No available time slots for the selected date. Please choose another date.")
        return
    
    # Time slot selection
    selected_time = st.selectbox(
        "Select Time Slot:",
        [""] + available_slots
    )
    
    if not selected_time:
        st.info("Please select a time slot.")
        return
    
    # Additional notes
    notes = st.text_area(
        "Additional Notes (Optional):",
        placeholder="Describe your symptoms or concerns..."
    )
    
    # Medical disclaimer
    st.warning(
        "⚠️ **Medical Disclaimer**: This appointment is for consultation only. "
        "In case of emergency, please contact emergency services immediately."
    )
    
    # Book appointment button
    if st.button("📅 Book Appointment", type="primary"):
        with st.spinner("Booking your appointment..."):
            result = st.session_state.appointment_system.book_appointment(
                user_id=st.session_state.user_id,
                user_name=st.session_state.user_name,
                doctor_id=selected_doctor_id,
                appointment_date=selected_date.strftime('%Y-%m-%d'),
                appointment_time=selected_time,
                notes=notes
            )
            
            if result['success']:
                st.success(f"✅ {result['message']}")
                st.success(f"**Appointment ID:** {result['appointment_id']}")
                
                # Display meeting information
                st.info("### 📹 Video Call Information")
                st.write(f"**Doctor:** {result['doctor_name']}")
                st.write(f"**Date:** {selected_date.strftime('%B %d, %Y')}")
                st.write(f"**Time:** {selected_time}")
                
                # Video call link
                meeting_platform = selected_doctor['meeting_platform'].title()
                st.write(f"**Platform:** {meeting_platform}")
                
                if st.button(f"🚀 Join {meeting_platform} Meeting", key="join_meeting"):
                    st.markdown(f"**Click the link below to join your appointment:**")
                    st.markdown(f"[🔗 Join {meeting_platform} Meeting]({result['meeting_link']})")
                    
                # Instructions
                appointment_time_info = ""
                if selected_date == datetime.now().date():
                    appointment_time_info = "📍 **Same-day appointment** - Please be ready to join on time\n"
                
                st.info(
                    f"### 📋 Instructions:\n"
                    f"{appointment_time_info}"
                    "1. Save your appointment ID for reference\n"
                    "2. Join the meeting 5 minutes before your scheduled time\n"
                    "3. Have your vitals data ready if collected\n"
                    "4. Ensure stable internet connection\n"
                    "5. Test your camera and microphone beforehand\n"
                    "6. Same-day appointments require 1-hour advance booking"
                )
                
            else:
                st.error(f"❌ {result['message']}")

def my_appointments_interface():
    """Display user's appointments"""
    st.subheader("📋 My Appointments")
    
    # Get user appointments
    appointments = st.session_state.appointment_system.get_user_appointments(st.session_state.user_id)
    
    if not appointments:
        st.info("You don't have any appointments yet.")
        st.info("Use the 'Book Appointment' section to schedule a consultation with a doctor.")
        return
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox(
            "Filter by Status:",
            ["All", "confirmed", "cancelled", "completed"]
        )
    with col2:
        sort_order = st.selectbox(
            "Sort by:",
            ["Newest First", "Oldest First", "Date Ascending", "Date Descending"]
        )
    
    # Filter appointments
    filtered_appointments = appointments
    if status_filter != "All":
        filtered_appointments = [apt for apt in appointments if apt['status'] == status_filter]
    
    # Sort appointments
    if sort_order == "Newest First":
        filtered_appointments = sorted(filtered_appointments, key=lambda x: x['created_at'], reverse=True)
    elif sort_order == "Oldest First":
        filtered_appointments = sorted(filtered_appointments, key=lambda x: x['created_at'])
    elif sort_order == "Date Ascending":
        filtered_appointments = sorted(filtered_appointments, key=lambda x: x['appointment_date'])
    else:  # Date Descending
        filtered_appointments = sorted(filtered_appointments, key=lambda x: x['appointment_date'], reverse=True)
    
    # Display appointments
    for i, appointment in enumerate(filtered_appointments):
        with st.expander(f"📅 {appointment['doctor_name']} - {appointment['appointment_date']} at {appointment['appointment_time']}", expanded=(i == 0)):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Appointment ID:** {appointment['appointment_id']}")
                st.write(f"**Doctor:** {appointment['doctor_name']}")
                st.write(f"**Specialty:** {appointment['specialty']}")
                st.write(f"**Date:** {appointment['appointment_date']}")
                st.write(f"**Time:** {appointment['appointment_time']}")
                st.write(f"**Status:** {appointment['status'].upper()}")
            
            with col2:
                if appointment['notes']:
                    st.write(f"**Notes:** {appointment['notes']}")
                st.write(f"**Booked:** {appointment['created_at'][:10]}")
                
                # Status badge
                if appointment['status'] == 'confirmed':
                    st.success("✅ Confirmed")
                elif appointment['status'] == 'cancelled':
                    st.error("❌ Cancelled")
                elif appointment['status'] == 'completed':
                    st.info("✅ Completed")
            
            # Action buttons
            if appointment['status'] == 'confirmed':
                appointment_datetime = datetime.strptime(
                    f"{appointment['appointment_date']} {appointment['appointment_time']}", 
                    "%Y-%m-%d %H:%M"
                )
                now = datetime.now()
                
                # Show join button if appointment is within 30 minutes
                time_until_appointment = appointment_datetime - now
                if -timedelta(minutes=30) <= time_until_appointment <= timedelta(hours=1):
                    if st.button(f"🚀 Join Meeting", key=f"join_{appointment['appointment_id']}"):
                        st.markdown(f"**Click the link below to join your appointment:**")
                        st.markdown(f"[🔗 Join Meeting]({appointment['meeting_link']})")
                
                # Cancel button (only for future appointments)
                if appointment_datetime > now:
                    if st.button(f"❌ Cancel Appointment", key=f"cancel_{appointment['appointment_id']}"):
                        if st.session_state.appointment_system.cancel_appointment(
                            appointment['appointment_id'], 
                            st.session_state.user_id
                        ):
                            st.success("Appointment cancelled successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to cancel appointment. Please try again.")

def doctor_management_interface():
    """Admin interface for managing doctors"""
    st.subheader("👨‍⚕️ Doctor Management (Admin)")
    
    # Add authentication check (simple password for demo)
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
    
    if not st.session_state.admin_authenticated:
        st.warning("🔐 Admin access required")
        admin_password = st.text_input("Enter Admin Password:", type="password")
        if st.button("Login as Admin"):
            if admin_password == "admin123":  # Change this to a secure password
                st.session_state.admin_authenticated = True
                st.success("✅ Admin access granted")
                st.rerun()
            else:
                st.error("❌ Invalid password")
        return
    
    # Admin tabs
    tab1, tab2, tab3 = st.tabs(["➕ Add Doctor", "📋 View Doctors", "✏️ Edit Doctors"])
    
    with tab1:
        st.subheader("Add New Doctor")
        
        # Doctor form
        with st.form("add_doctor_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                doctor_id = st.text_input("Doctor ID (e.g., DR006):", placeholder="DR006")
                doctor_name = st.text_input("Doctor Name:", placeholder="Dr. John Smith")
                specialty = st.selectbox(
                    "Specialty:",
                    ["General Physician", "Cardiologist", "Dermatologist", "Pediatrician", 
                     "Neurologist", "Orthopedic", "Gynecologist", "Psychiatrist", "ENT", "Other"]
                )
                if specialty == "Other":
                    specialty = st.text_input("Custom Specialty:")
            
            with col2:
                # Available days
                st.write("**Available Days:**")
                days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                selected_days = []
                day_cols = st.columns(4)
                for i, day in enumerate(days):
                    with day_cols[i % 4]:
                        if st.checkbox(day, key=f"day_{day}"):
                            selected_days.append(day)
                
                # Available times
                start_time = st.time_input("Start Time:", value=datetime.strptime("09:00", "%H:%M").time())
                end_time = st.time_input("End Time:", value=datetime.strptime("17:00", "%H:%M").time())
                
                # Meeting platform
                meeting_platform = st.selectbox("Meeting Platform:", ["zoom", "meet"])
                meeting_room = st.text_input(
                    "Meeting Room URL:", 
                    placeholder="https://zoom.us/j/1234567890 or https://meet.google.com/abc-defg-hij"
                )
            
            submitted = st.form_submit_button("➕ Add Doctor", type="primary")
            
            if submitted:
                if not all([doctor_id, doctor_name, specialty, selected_days, meeting_room]):
                    st.error("❌ Please fill all required fields")
                else:
                    # Validate doctor ID doesn't exist
                    existing_doctors = st.session_state.appointment_system.get_doctors()
                    if any(doc['doctor_id'] == doctor_id for doc in existing_doctors):
                        st.error(f"❌ Doctor ID {doctor_id} already exists")
                    else:
                        # Add doctor to CSV
                        try:
                            with open("data/doctors.csv", 'a', newline='') as f:
                                writer = csv.writer(f)
                                writer.writerow([
                                    doctor_id, doctor_name, specialty, 
                                    ','.join(selected_days),
                                    f"{start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}",
                                    meeting_platform, meeting_room, "active"
                                ])
                            st.success(f"✅ Doctor {doctor_name} added successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error adding doctor: {str(e)}")
    
    with tab2:
        st.subheader("Current Doctors")
        doctors = st.session_state.appointment_system.get_doctors()
        
        if doctors:
            # Create a dataframe for better display
            df = pd.DataFrame(doctors)
            st.dataframe(df, use_container_width=True)
            
            # Doctor cards
            for doctor in doctors:
                with st.expander(f"👨‍⚕️ {doctor['name']} - {doctor['specialty']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**ID:** {doctor['doctor_id']}")
                        st.write(f"**Name:** {doctor['name']}")
                        st.write(f"**Specialty:** {doctor['specialty']}")
                        st.write(f"**Status:** {doctor['status']}")
                    with col2:
                        st.write(f"**Available Days:** {doctor['available_days']}")
                        st.write(f"**Available Times:** {doctor['available_times']}")
                        st.write(f"**Platform:** {doctor['meeting_platform']}")
                        st.write(f"**Meeting Room:** {doctor['meeting_room']}")
        else:
            st.info("No doctors found.")
    
    with tab3:
        st.subheader("Edit/Deactivate Doctors")
        doctors = st.session_state.appointment_system.get_doctors()
        
        if doctors:
            doctor_options = {f"{doc['name']} ({doc['doctor_id']})": doc for doc in doctors}
            selected_doctor_key = st.selectbox("Select Doctor to Edit:", list(doctor_options.keys()))
            
            if selected_doctor_key:
                selected_doctor = doctor_options[selected_doctor_key]
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🚫 Deactivate Doctor", type="secondary"):
                        # Update doctor status to inactive
                        try:
                            # Read all doctors
                            all_doctors = []
                            with open("data/doctors.csv", 'r', newline='') as f:
                                reader = csv.DictReader(f)
                                all_doctors = list(reader)
                            
                            # Update the selected doctor
                            for doctor in all_doctors:
                                if doctor['doctor_id'] == selected_doctor['doctor_id']:
                                    doctor['status'] = 'inactive'
                                    break
                            
                            # Write back
                            with open("data/doctors.csv", 'w', newline='') as f:
                                if all_doctors:
                                    writer = csv.DictWriter(f, fieldnames=all_doctors[0].keys())
                                    writer.writeheader()
                                    writer.writerows(all_doctors)
                            
                            st.success(f"✅ Doctor {selected_doctor['name']} deactivated")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error deactivating doctor: {str(e)}")
                
                with col2:
                    if st.button("✅ Activate Doctor", type="primary"):
                        # Update doctor status to active
                        try:
                            # Read all doctors
                            all_doctors = []
                            with open("data/doctors.csv", 'r', newline='') as f:
                                reader = csv.DictReader(f)
                                all_doctors = list(reader)
                            
                            # Update the selected doctor
                            for doctor in all_doctors:
                                if doctor['doctor_id'] == selected_doctor['doctor_id']:
                                    doctor['status'] = 'active'
                                    break
                            
                            # Write back
                            with open("data/doctors.csv", 'w', newline='') as f:
                                if all_doctors:
                                    writer = csv.DictWriter(f, fieldnames=all_doctors[0].keys())
                                    writer.writeheader()
                                    writer.writerows(all_doctors)
                            
                            st.success(f"✅ Doctor {selected_doctor['name']} activated")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error activating doctor: {str(e)}")
        else:
            st.info("No doctors available to edit.")
    
    # Logout button
    if st.button("🚪 Logout Admin"):
        st.session_state.admin_authenticated = False
        st.rerun()

def main():
    """Main application"""
    # Header
    st.title("🏥 Intel AI Healthcare Kiosk")
    st.markdown("*Preliminary Health Assessment & First Aid Assistant*")
    
    # Display medical disclaimer
    display_medical_disclaimer()
    
    # Language selection
    language_selector()
    
    # Initialize configuration
    Config.initialize()
    
    # Initialize AI agent
    if not initialize_ai_agent():
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Select Section:",
            ["Vitals Collection", "Health Chat", "First Aid", "Book Appointment", "My Appointments", "Doctor Management", "Export Data"]
        )
        
        # Display current session info
        if st.session_state.vitals_system.current_session:
            st.success(f"✅ {len(st.session_state.vitals_system.current_session)} vitals collected")
            
            if st.button("🗑️ Clear Session"):
                st.session_state.vitals_system.clear_session()
                st.session_state.current_vitals = {}
                st.session_state.conversation_history = []
                st.rerun()
    
    # Main content based on selected page
    if page == "Vitals Collection":
        vitals_input_form()
        display_vitals_summary()
        
    elif page == "Health Chat":
        chat_interface()
        
    elif page == "First Aid":
        first_aid_section()
        
    elif page == "Book Appointment":
        appointment_booking_interface()
        
    elif page == "My Appointments":
        my_appointments_interface()
        
    elif page == "Export Data":
        st.subheader("📁 Export Health Data")
        
        if st.session_state.vitals_system.current_session:
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📄 Export as JSON"):
                    json_data = st.session_state.vitals_system.export_vitals_data('json')
                    st.download_button(
                        label="Download JSON",
                        data=json_data,
                        file_name=f"vitals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
            
            with col2:
                if st.button("📊 Export as CSV"):
                    csv_data = st.session_state.vitals_system.export_vitals_data('csv')
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name=f"vitals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
        else:
            st.info("No vitals data to export. Please collect some vitals first.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"**Intel AI Healthcare Kiosk** v{Config.APP_VERSION} | "
        f"Language: {st.session_state.multilingual.supported_languages[st.session_state.language]}"
    )

if __name__ == "__main__":
    main()
