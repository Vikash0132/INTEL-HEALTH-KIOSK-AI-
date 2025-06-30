import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for the AI Healthcare Kiosk"""
    
    # Google AI Studio Configuration
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    
    # Application Configuration
    APP_NAME = os.getenv('APP_NAME', 'Intel AI Healthcare Kiosk')
    APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Language Configuration
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'hi': 'Hindi',
        'kn': 'Kannada'
    }
    
    # Medical Configuration
    MEDICAL_DISCLAIMER = os.getenv('MEDICAL_DISCLAIMER', 'True').lower() == 'true'
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///healthcare_kiosk.db')
    
    # Security Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 1800))
    
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
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required. Please set it in your .env file")
        return True
