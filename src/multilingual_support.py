from typing import Dict, Any, Optional
import logging
import json

try:
    from googletrans import Translator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False
    print("Warning: googletrans not available. Translation features will be limited.")

logger = logging.getLogger(__name__)

class MultilingualSupport:
    """
    Multilingual support system for English, Hindi, and Kannada
    """
    
    def __init__(self):
        """Initialize multilingual support"""
        if TRANSLATOR_AVAILABLE:
            self.translator = Translator()
        else:
            self.translator = None
        
        self.supported_languages = {
            'en': 'English',
            'hi': 'Hindi', 
            'kn': 'Kannada'
        }
        
        # Load predefined translations for medical terms
        self.medical_translations = self._load_medical_translations()
        
        logger.info("Multilingual support initialized")
    
    def _load_medical_translations(self) -> Dict[str, Dict[str, str]]:
        """Load predefined medical term translations"""
        return {
            # Medical Disclaimers
            'medical_disclaimer': {
                'en': "This is a preliminary assessment only. Please consult a qualified healthcare professional for proper medical diagnosis and treatment.",
                'hi': "यह केवल एक प्रारंभिक मूल्यांकन है। उचित चिकित्सा निदान और उपचार के लिए कृपया किसी योग्य स्वास्थ्य सेवा पेशेवर से सलाह लें।",
                'kn': "ಇದು ಕೇವಲ ಪ್ರಾಥಮಿಕ ಮೌಲ್ಯಮಾಪನವಾಗಿದೆ. ಸರಿಯಾದ ವೈದ್ಯಕೀಯ ರೋಗನಿರ್ಣಯ ಮತ್ತು ಚಿಕಿತ್ಸೆಗಾಗಿ ದಯವಿಟ್ಟು ಅರ್ಹ ಆರೋಗ್ಯ ಸೇವಾ ವೃತ್ತಿಪರರನ್ನು ಸಂಪರ್ಕಿಸಿ."
            },
            
            # Emergency Messages
            'emergency_message': {
                'en': "This appears to be a medical emergency. Please call emergency services immediately or go to the nearest hospital.",
                'hi': "यह एक चिकित्सा आपातकाल प्रतीत होता है। कृपया तुरंत आपातकालीन सेवाओं को कॉल करें या निकटतम अस्पताल जाएं।",
                'kn': "ಇದು ವೈದ್ಯಕೀಯ ತುರ್ತುಸ್ಥಿತಿಯಂತೆ ಕಾಣುತ್ತದೆ. ದಯವಿಟ್ಟು ತಕ್ಷಣ ತುರ್ತು ಸೇವೆಗಳಿಗೆ ಕರೆ ಮಾಡಿ ಅಥವಾ ಹತ್ತಿರದ ಆಸ್ಪತ್ರೆಗೆ ಹೋಗಿ."
            },
            
            # Common Medical Terms
            'blood_pressure': {
                'en': 'Blood Pressure',
                'hi': 'रक्तचाप',
                'kn': 'ರಕ್ತದೊತ್ತಡ'
            },
            'heart_rate': {
                'en': 'Heart Rate',
                'hi': 'हृदय गति',
                'kn': 'ಹೃದಯ ಬಡಿತ'
            },
            'temperature': {
                'en': 'Temperature',
                'hi': 'तापमान',
                'kn': 'ತಾಪಮಾನ'
            },
            'normal': {
                'en': 'Normal',
                'hi': 'सामान्य',
                'kn': 'ಸಾಮಾನ್ಯ'
            },
            'high': {
                'en': 'High',
                'hi': 'उच्च',
                'kn': 'ಹೆಚ್ಚು'
            },
            'low': {
                'en': 'Low',
                'hi': 'कम',
                'kn': 'ಕಡಿಮೆ'
            },
            'critical': {
                'en': 'Critical',
                'hi': 'गंभीर',
                'kn': 'ಗಂಭೀರ'
            },
            
            # First Aid Terms
            'first_aid': {
                'en': 'First Aid',
                'hi': 'प्राथमिक चिकित्सा',
                'kn': 'ಪ್ರಾಥಮಿಕ ಚಿಕಿತ್ಸೆ'
            },
            'emergency_steps': {
                'en': 'Emergency Steps',
                'hi': 'आपातकालीन कदम',
                'kn': 'ತುರ್ತು ಹಂತಗಳು'
            },
            'call_doctor': {
                'en': 'Call a doctor immediately',
                'hi': 'तुरंत डॉक्टर को कॉल करें',
                'kn': 'ತಕ್ಷಣ ವೈದ್ಯರನ್ನು ಕರೆಯಿರಿ'
            },
            
            # Vital Signs Categories
            'cardiovascular': {
                'en': 'Cardiovascular',
                'hi': 'हृदय संबंधी',
                'kn': 'ಹೃದಯರಕ್ತನಾಳ'
            },
            'respiratory': {
                'en': 'Respiratory',
                'hi': 'श्वसन संबंधी',
                'kn': 'ಉಸಿರಾಟ'
            },
            'metabolic': {
                'en': 'Metabolic',
                'hi': 'चयापचय',
                'kn': 'ಚಯಾಪಚಯ'
            },
            
            # UI Elements
            'welcome_message': {
                'en': 'Welcome to Intel AI Healthcare Kiosk. How can I help you today?',
                'hi': 'इंटेल एआई हेल्थकेयर कियोस्क में आपका स्वागत है। आज मैं आपकी कैसे मदद कर सकता हूं?',
                'kn': 'ಇಂಟೆಲ್ AI ಆರೋಗ್ಯ ಸೇವಾ ಕಿಯಾಸ್ಕ್‌ಗೆ ಸ್ವಾಗತ. ಇಂದು ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?'
            },
            'select_language': {
                'en': 'Please select your preferred language',
                'hi': 'कृपया अपनी पसंदीदा भाषा चुनें',
                'kn': 'ದಯವಿಟ್ಟು ನಿಮ್ಮ ಆದ್ಯತೆಯ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆ ಮಾಡಿ'
            },
            'vitals_collection': {
                'en': 'Vitals Collection',
                'hi': 'जीवन संकेत संग्रह',
                'kn': 'ಪ್ರಾಣ ಸಂಕೇತಗಳ ಸಂಗ್ರಹ'
            },
            'health_assessment': {
                'en': 'Health Assessment',
                'hi': 'स्वास्थ्य मूल्यांकन',
                'kn': 'ಆರೋಗ್ಯ ಮೌಲ್ಯಮಾಪನ'
            }
        }
    
    def get_translation(self, key: str, language: str = 'en') -> str:
        """
        Get predefined translation for a medical term
        
        Args:
            key: Translation key
            language: Target language code
            
        Returns:
            Translated text or original key if not found
        """
        if key in self.medical_translations:
            return self.medical_translations[key].get(language, 
                                                    self.medical_translations[key].get('en', key))
        return key
    
    async def translate_text(self, text: str, target_language: str = 'en', source_language: str = 'auto') -> str:
        """
        Translate text using Google Translate
        
        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Source language code (auto-detect if 'auto')
            
        Returns:
            Translated text
        """
        try:
            if not TRANSLATOR_AVAILABLE or self.translator is None:
                logger.warning("Google Translate not available, returning original text")
                return text
                
            if target_language not in self.supported_languages:
                logger.warning(f"Unsupported language: {target_language}, falling back to English")
                target_language = 'en'
            
            if target_language == source_language:
                return text
            
            # Use Google Translate
            result = self.translator.translate(text, dest=target_language, src=source_language)
            return result.text
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return text  # Return original text if translation fails
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of input text
        
        Args:
            text: Input text
            
        Returns:
            Detected language code
        """
        try:
            if not TRANSLATOR_AVAILABLE or self.translator is None:
                # Fallback: simple heuristic detection
                if any(char in text for char in 'हृदयरक्तचाप'):
                    return 'hi'
                elif any(char in text for char in 'ಹೃದಯರಕ್ತದೊತ್ತಡ'):
                    return 'kn'
                else:
                    return 'en'
            
            detection = self.translator.detect(text)
            detected_lang = detection.lang
            
            # Map to supported languages
            if detected_lang in self.supported_languages:
                return detected_lang
            elif detected_lang in ['bn', 'as', 'or']:  # Related Indian languages
                return 'hi'  # Default to Hindi
            else:
                return 'en'  # Default to English
                
        except Exception as e:
            logger.error(f"Language detection error: {str(e)}")
            return 'en'  # Default to English on error
    
    def format_vital_signs_multilingual(self, vitals_data: Dict[str, Any], language: str = 'en') -> Dict[str, Any]:
        """
        Format vital signs data with multilingual labels
        
        Args:
            vitals_data: Vital signs data
            language: Target language
            
        Returns:
            Formatted data with translated labels
        """
        formatted_data = {}
        
        for vital_name, vital_value in vitals_data.items():
            # Translate vital name if available
            translated_name = self.get_translation(vital_name, language)
            
            if isinstance(vital_value, dict):
                # If it's a VitalSign object converted to dict
                formatted_vital = vital_value.copy()
                formatted_vital['display_name'] = translated_name
                
                # Translate status
                if 'status' in formatted_vital:
                    status_key = formatted_vital['status']
                    formatted_vital['status_display'] = self.get_translation(status_key, language)
                
                formatted_data[vital_name] = formatted_vital
            else:
                # Simple value
                formatted_data[vital_name] = {
                    'value': vital_value,
                    'display_name': translated_name
                }
        
        return formatted_data
    
    def get_localized_ui_text(self, language: str = 'en') -> Dict[str, str]:
        """
        Get all UI text in specified language
        
        Args:
            language: Target language code
            
        Returns:
            Dictionary of localized UI text
        """
        ui_text = {}
        
        ui_keys = [
            'welcome_message', 'select_language', 'vitals_collection',
            'health_assessment', 'medical_disclaimer', 'emergency_message',
            'first_aid', 'call_doctor'
        ]
        
        for key in ui_keys:
            ui_text[key] = self.get_translation(key, language)
        
        return ui_text
    
    def create_multilingual_response(self, response_data: Dict[str, Any], language: str = 'en') -> Dict[str, Any]:
        """
        Create a response with multilingual support
        
        Args:
            response_data: Response data from AI agent
            language: Target language
            
        Returns:
            Multilingual response data
        """
        multilingual_response = response_data.copy()
        
        # Add localized UI elements
        multilingual_response['ui_text'] = self.get_localized_ui_text(language)
        
        # Add language metadata
        multilingual_response['language'] = language
        multilingual_response['language_name'] = self.supported_languages.get(language, 'Unknown')
        
        # Ensure medical disclaimer is present
        if 'medical_disclaimer' not in multilingual_response:
            multilingual_response['medical_disclaimer'] = self.get_translation('medical_disclaimer', language)
        
        return multilingual_response
    
    def get_language_preferences(self) -> Dict[str, str]:
        """Get supported language preferences"""
        return self.supported_languages.copy()
    
    def is_supported_language(self, language_code: str) -> bool:
        """Check if language is supported"""
        return language_code in self.supported_languages
    
    def get_medical_terms_glossary(self, language: str = 'en') -> Dict[str, str]:
        """
        Get medical terms glossary in specified language
        
        Args:
            language: Target language code
            
        Returns:
            Dictionary of medical terms
        """
        glossary = {}
        
        medical_term_keys = [
            'blood_pressure', 'heart_rate', 'temperature', 'normal', 'high', 'low', 'critical',
            'cardiovascular', 'respiratory', 'metabolic'
        ]
        
        for key in medical_term_keys:
            glossary[key] = self.get_translation(key, language)
        
        return glossary
    
    def format_emergency_response(self, language: str = 'en') -> Dict[str, str]:
        """
        Format emergency response messages in specified language
        
        Args:
            language: Target language code
            
        Returns:
            Emergency response messages
        """
        return {
            'emergency_message': self.get_translation('emergency_message', language),
            'call_doctor': self.get_translation('call_doctor', language),
            'emergency_steps': self.get_translation('emergency_steps', language)
        }
