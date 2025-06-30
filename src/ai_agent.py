import google.generativeai as genai
from typing import Dict, List, Optional, Any
import json
import logging
from config.config import Config

logger = logging.getLogger(__name__)

class HealthcareAIAgent:
    """
    Core AI agent for healthcare kiosk using Google AI Studio (Gemini)
    Handles conversational interactions, vitals analysis, and preliminary diagnosis
    """
    
    def __init__(self):
        """Initialize the AI agent with Google AI Studio"""
        try:
            Config.validate_config()
            genai.configure(api_key=Config.GOOGLE_API_KEY)
            
            # Initialize the Gemini model
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            
            # System prompt for healthcare context
            self.system_prompt = self._build_system_prompt()
            
            logger.info("Healthcare AI Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI Agent: {str(e)}")
            raise
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for healthcare context"""
        return """
        You are an AI healthcare assistant for the Intel AI Healthcare Kiosk. Your role is to:
        
        1. PROVIDE PRELIMINARY HEALTH ASSESSMENTS based on vital signs and symptoms
        2. OFFER FIRST AID GUIDANCE for common health issues
        3. SUPPORT MULTIPLE LANGUAGES: English, Hindi, and Kannada
        4. MAINTAIN A COMPASSIONATE, PROFESSIONAL TONE
        
        CRITICAL MEDICAL DISCLAIMERS:
        - You provide PRELIMINARY assessments only, NOT medical diagnoses
        - Always recommend consulting a qualified healthcare professional
        - In emergencies, advise immediate medical attention
        - Do not prescribe medications or treatments
        - Acknowledge limitations of AI in healthcare
        
        CAPABILITIES:
        - Analyze 28 different vital signs
        - Provide health risk assessments
        - Suggest when to seek medical care
        - Offer basic first aid instructions
        - Support health monitoring guidance
        
        LANGUAGE SUPPORT:
        - Respond in the user's preferred language (English/Hindi/Kannada)
        - If unsure of language, ask for preference
        - Maintain medical accuracy across all languages
        
        VITAL SIGNS YOU CAN ANALYZE:
        Heart rate, blood pressure, respiratory rate, temperature, oxygen saturation,
        blood glucose, cholesterol levels, BMI, and 20 other health metrics.
        
        Always prioritize user safety and emphasize the importance of professional medical consultation.
        """
    
    async def generate_response(
        self, 
        user_input: str, 
        vitals_data: Optional[Dict[str, Any]] = None,
        language: str = 'en',
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Generate AI response based on user input and vitals data
        
        Args:
            user_input: User's question or concern
            vitals_data: Dictionary of vital signs and values
            language: Preferred language (en/hi/kn)
            conversation_history: Previous conversation context
            
        Returns:
            Dictionary containing response, assessment, and recommendations
        """
        try:
            # Build comprehensive prompt
            prompt = self._build_prompt(user_input, vitals_data, language, conversation_history)
            
            # Generate response using Gemini
            response = self.model.generate_content(prompt)
            
            # Parse and structure the response
            structured_response = self._parse_response(response.text, vitals_data, language)
            
            return structured_response
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return self._error_response(language)
    
    def _build_prompt(
        self, 
        user_input: str, 
        vitals_data: Optional[Dict], 
        language: str,
        conversation_history: Optional[List[Dict]]
    ) -> str:
        """Build comprehensive prompt for the AI model"""
        
        language_names = {'en': 'English', 'hi': 'Hindi', 'kn': 'Kannada'}
        lang_name = language_names.get(language, 'English')
        
        prompt = f"{self.system_prompt}\n\n"
        prompt += f"RESPONSE LANGUAGE: {lang_name}\n\n"
        
        # Add vitals data if available
        if vitals_data:
            prompt += "CURRENT VITAL SIGNS:\n"
            for vital, value in vitals_data.items():
                if value is not None:
                    prompt += f"- {vital}: {value}\n"
            prompt += "\n"
        
        # Add conversation history
        if conversation_history:
            prompt += "CONVERSATION HISTORY:\n"
            for entry in conversation_history[-3:]:  # Last 3 exchanges
                prompt += f"User: {entry.get('user', '')}\n"
                prompt += f"Assistant: {entry.get('assistant', '')}\n"
            prompt += "\n"
        
        prompt += f"USER QUESTION/CONCERN: {user_input}\n\n"
        
        prompt += """
        Please provide a structured response in JSON format with the following fields:
        {
            "response": "Your conversational response to the user",
            "health_assessment": "Preliminary health assessment based on available data",
            "risk_level": "low/moderate/high/emergency",
            "recommendations": ["List of actionable recommendations"],
            "next_steps": "What the user should do next",
            "medical_disclaimer": "Reminder about professional consultation",
            "language": "Response language code"
        }
        """
        
        return prompt
    
    def _parse_response(self, ai_response: str, vitals_data: Optional[Dict], language: str) -> Dict[str, Any]:
        """Parse and structure AI response"""
        try:
            # Try to extract JSON from response
            if '{' in ai_response and '}' in ai_response:
                json_start = ai_response.find('{')
                json_end = ai_response.rfind('}') + 1
                json_str = ai_response[json_start:json_end]
                parsed_response = json.loads(json_str)
            else:
                # Fallback if JSON parsing fails
                parsed_response = {
                    "response": ai_response,
                    "health_assessment": "Assessment based on provided information",
                    "risk_level": "moderate",
                    "recommendations": ["Consult with a healthcare professional"],
                    "next_steps": "Schedule an appointment with your doctor",
                    "medical_disclaimer": "This is a preliminary assessment. Please consult a qualified healthcare professional.",
                    "language": language
                }
            
            # Add vitals summary if available
            if vitals_data:
                parsed_response["vitals_summary"] = self._summarize_vitals(vitals_data)
            
            return parsed_response
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response, using fallback")
            return self._fallback_response(ai_response, language)
    
    def _summarize_vitals(self, vitals_data: Dict[str, Any]) -> Dict[str, str]:
        """Summarize vital signs data"""
        summary = {}
        
        # Define normal ranges for key vitals
        normal_ranges = {
            'heart_rate': (60, 100),
            'blood_pressure_systolic': (90, 120),
            'blood_pressure_diastolic': (60, 80),
            'body_temperature': (36.1, 37.2),
            'oxygen_saturation': (95, 100),
            'respiratory_rate': (12, 20)
        }
        
        for vital, value in vitals_data.items():
            if value is not None and vital in normal_ranges:
                min_val, max_val = normal_ranges[vital]
                if min_val <= float(value) <= max_val:
                    summary[vital] = "Normal"
                elif float(value) < min_val:
                    summary[vital] = "Below Normal"
                else:
                    summary[vital] = "Above Normal"
        
        return summary
    
    def _fallback_response(self, ai_response: str, language: str) -> Dict[str, Any]:
        """Fallback response structure"""
        disclaimers = {
            'en': "This is a preliminary assessment. Please consult a qualified healthcare professional.",
            'hi': "यह एक प्रारंभिक मूल्यांकन है। कृपया किसी योग्य स्वास्थ्य सेवा पेशेवर से सलाह लें।",
            'kn': "ಇದು ಪ್ರಾಥಮಿಕ ಮೌಲ್ಯಮಾಪನವಾಗಿದೆ. ದಯವಿಟ್ಟು ಅರ್ಹ ಆರೋಗ್ಯ ಸೇವಾ ವೃತ್ತಿಪರರನ್ನು ಸಂಪರ್ಕಿಸಿ."
        }
        
        return {
            "response": ai_response,
            "health_assessment": "Basic assessment provided",
            "risk_level": "moderate",
            "recommendations": ["Consult healthcare professional"],
            "next_steps": "Schedule medical appointment",
            "medical_disclaimer": disclaimers.get(language, disclaimers['en']),
            "language": language
        }
    
    def _error_response(self, language: str) -> Dict[str, Any]:
        """Generate error response"""
        error_messages = {
            'en': "I'm sorry, I'm experiencing technical difficulties. Please try again or consult a healthcare professional.",
            'hi': "क्षमा करें, मुझे तकनीकी समस्याओं का सामना कर रहा हूँ। कृपया फिर से कोशिश करें या किसी स्वास्थ्य सेवा पेशेवर से सलाह लें।",
            'kn': "ಕ್ಷಮಿಸಿ, ನಾನು ತಾಂತ್ರಿಕ ತೊಂದರೆಗಳನ್ನು ಅನುಭವಿಸುತ್ತಿದ್ದೇನೆ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ ಅಥವಾ ಆರೋಗ್ಯ ಸೇವಾ ವೃತ್ತಿಪರರನ್ನು ಸಂಪರ್ಕಿಸಿ."
        }
        
        return {
            "response": error_messages.get(language, error_messages['en']),
            "health_assessment": "Unable to assess",
            "risk_level": "unknown",
            "recommendations": ["Try again or seek medical help"],
            "next_steps": "Contact healthcare provider",
            "medical_disclaimer": "Please consult a qualified healthcare professional.",
            "language": language,
            "error": True
        }

    def analyze_vitals_trend(self, historical_vitals: List[Dict]) -> Dict[str, Any]:
        """Analyze trends in vital signs over time"""
        # This would analyze patterns in vitals data
        # Implementation for trend analysis
        pass
    
    def get_first_aid_guidance(self, condition: str, language: str = 'en') -> Dict[str, Any]:
        """Get first aid guidance for specific conditions"""
        prompt = f"""
        Provide first aid guidance for: {condition}
        Language: {language}
        
        Include:
        1. Immediate steps to take
        2. Warning signs requiring emergency care
        3. What NOT to do
        4. When to call emergency services
        
        Maintain appropriate medical disclaimers.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_response(response.text, None, language)
        except Exception as e:
            logger.error(f"Error getting first aid guidance: {str(e)}")
            return self._error_response(language)
