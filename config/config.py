import os
from dotenv import load_dotenv

# Load environment variables from .env file if running locally
load_dotenv()

class Config:
    """Configuration class for the AI Healthcare Kiosk"""
    
    # Try to get from Streamlit secrets first (for cloud deployment), then environment variables
    @staticmethod
    def get_config_value(key: str, default: str = None):
        """Get configuration value from Streamlit secrets or environment variables"""
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and key in st.secrets:
                return st.secrets[key]
        except (ImportError, AttributeError, KeyError):
            pass
        return os.getenv(key, default)
    
    # Google AI Studio Configuration
    GOOGLE_API_KEY = None
    
    @classmethod
    def initialize(cls):
        """Initialize configuration values"""
        cls.GOOGLE_API_KEY = cls.get_config_value('GOOGLE_API_KEY')
    
    # Application Configuration
    APP_NAME = 'Intel AI Healthcare Kiosk'
    APP_VERSION = '1.0.0'
    DEBUG = False
    
    # Language Configuration
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'hi': 'Hindi',
        'kn': 'Kannada'
    }
    
    # Medical Configuration
    MEDICAL_DISCLAIMER = True
    
    # Database Configuration
    DATABASE_URL = 'sqlite:///healthcare_kiosk.db'
    
    # Security Configuration
    SECRET_KEY = 'healthcare-kiosk-secret-key'
    SESSION_TIMEOUT = 1800
    
    # Vitals Configuration
    VITAL_SIGNS = [
        'heart_rate', 'blood_pressure_systolic', 'blood_pressure_diastolic',
        'respiratory_rate', 'body_temperature', 'oxygen_saturation',
        'pulse_rate', 'blood_glucose', 'cholesterol_total', 'cholesterol_ldl',
        'cholesterol_hdl', 'triglycerides', 'hemoglobin', 'white_blood_cells',
        'red_blood_cells', 'platelets', 'height', 'weight', 'bmi',
        'waist_circumference', 'hip_circumference', 'body_fat_percentage',
        'muscle_mass', 'bone_density', 'vision_acuity', 'hearing_threshold',
        'blood_pressure_pulse_pressure', 'mean_arterial_pressure'
    ]
    
    @classmethod
    def validate_config(cls):
        """Validate essential configuration"""
        # Initialize configuration if not already done
        if cls.GOOGLE_API_KEY is None:
            cls.initialize()
            
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required. Please set it in your environment variables or Streamlit secrets")
        return True
