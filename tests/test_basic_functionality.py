import unittest
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from vitals_system import VitalsCollectionSystem
from multilingual_support import MultilingualSupport

class TestVitalsSystem(unittest.TestCase):
    """Test cases for the vitals collection system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.vitals_system = VitalsCollectionSystem()
    
    def test_collect_valid_vital(self):
        """Test collecting a valid vital sign"""
        vital_sign = self.vitals_system.collect_vital('heart_rate', 75)
        
        self.assertEqual(vital_sign.value, 75)
        self.assertEqual(vital_sign.status, 'normal')
        self.assertEqual(vital_sign.unit, 'bpm')
    
    def test_collect_high_vital(self):
        """Test collecting a high vital sign"""
        vital_sign = self.vitals_system.collect_vital('heart_rate', 120)
        
        self.assertEqual(vital_sign.value, 120)
        self.assertEqual(vital_sign.status, 'high')
    
    def test_collect_low_vital(self):
        """Test collecting a low vital sign"""
        vital_sign = self.vitals_system.collect_vital('heart_rate', 45)
        
        self.assertEqual(vital_sign.value, 45)
        self.assertEqual(vital_sign.status, 'low')
    
    def test_invalid_vital_name(self):
        """Test collecting an invalid vital sign"""
        with self.assertRaises(ValueError):
            self.vitals_system.collect_vital('invalid_vital', 100)
    
    def test_health_score_calculation(self):
        """Test health score calculation"""
        # Collect some normal vitals
        self.vitals_system.collect_vital('heart_rate', 75)
        self.vitals_system.collect_vital('body_temperature', 36.5)
        
        health_score = self.vitals_system.get_health_score()
        
        self.assertGreater(health_score['score'], 80)
        self.assertEqual(health_score['grade'], 'Excellent')
    
    def test_bmi_calculation(self):
        """Test BMI calculation"""
        # Collect height and weight
        self.vitals_system.collect_vital('height', 170)  # 170 cm
        self.vitals_system.collect_vital('weight', 70)   # 70 kg
        
        # Calculate derived vitals
        derived = self.vitals_system.calculate_derived_vitals()
        
        self.assertIn('bmi', derived)
        # BMI = 70 / (1.7)^2 = 24.22
        self.assertAlmostEqual(derived['bmi'].value, 24.22, places=1)

class TestMultilingualSupport(unittest.TestCase):
    """Test cases for multilingual support"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.multilingual = MultilingualSupport()
    
    def test_get_translation_english(self):
        """Test getting English translation"""
        translation = self.multilingual.get_translation('medical_disclaimer', 'en')
        self.assertIn('preliminary assessment', translation.lower())
    
    def test_get_translation_hindi(self):
        """Test getting Hindi translation"""
        translation = self.multilingual.get_translation('medical_disclaimer', 'hi')
        self.assertIn('प्रारंभिक', translation)
    
    def test_get_translation_kannada(self):
        """Test getting Kannada translation"""
        translation = self.multilingual.get_translation('medical_disclaimer', 'kn')
        self.assertIn('ಪ್ರಾಥಮಿಕ', translation)
    
    def test_unsupported_language(self):
        """Test fallback for unsupported language"""
        translation = self.multilingual.get_translation('medical_disclaimer', 'fr')
        # Should fallback to English
        self.assertIn('preliminary assessment', translation.lower())
    
    def test_language_detection(self):
        """Test language detection"""
        # Test English
        lang = self.multilingual.detect_language("Hello, how are you?")
        self.assertEqual(lang, 'en')
    
    def test_supported_languages(self):
        """Test supported languages"""
        languages = self.multilingual.get_language_preferences()
        
        self.assertIn('en', languages)
        self.assertIn('hi', languages)
        self.assertIn('kn', languages)
        self.assertEqual(languages['en'], 'English')

if __name__ == '__main__':
    unittest.main()
