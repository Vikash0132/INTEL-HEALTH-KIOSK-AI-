import streamlit as st
import asyncio
import logging
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our custom modules
from src.ai_agent import HealthcareAIAgent
from src.vitals_system import VitalsCollectionSystem
from src.multilingual_support import MultilingualSupport
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

def main():
    """Main application"""
    # Header
    st.title("🏥 Intel AI Healthcare Kiosk")
    st.markdown("*Preliminary Health Assessment & First Aid Assistant*")
    
    # Display medical disclaimer
    display_medical_disclaimer()
    
    # Language selection
    language_selector()
    
    # Initialize AI agent
    if not initialize_ai_agent():
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Select Section:",
            ["Vitals Collection", "Health Chat", "First Aid", "Export Data"]
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
