#!/usr/bin/env python3
"""
Intel AI Healthcare Kiosk Demo Script
=====================================

This script demonstrates the key features of the Intel AI Healthcare Kiosk:
1. Vitals collection and analysis
2. AI health assessment
3. Multilingual support
4. First aid guidance

Run this script to see the system in action without the UI.
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ai_agent import HealthcareAIAgent
from src.vitals_system import VitalsCollectionSystem
from src.multilingual_support import MultilingualSupport
from config.config import Config

class HealthcareKioskDemo:
    """Demo class to showcase healthcare kiosk functionality"""
    
    def __init__(self):
        """Initialize demo components"""
        print("🏥 Initializing Intel AI Healthcare Kiosk Demo...")
        
        try:
            self.ai_agent = HealthcareAIAgent()
            self.vitals_system = VitalsCollectionSystem()
            self.multilingual = MultilingualSupport()
            print("✅ All components initialized successfully!")
        except Exception as e:
            print(f"❌ Initialization failed: {str(e)}")
            print("🔧 Please ensure your .env file has a valid GOOGLE_API_KEY")
            sys.exit(1)
    
    def load_sample_data(self):
        """Load sample vital signs data"""
        try:
            with open('data/sample_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("⚠️ Sample data file not found, using default values")
            return {
                "sample_vitals": {
                    "normal_patient": {
                        "heart_rate": 72,
                        "blood_pressure_systolic": 110,
                        "blood_pressure_diastolic": 70,
                        "body_temperature": 36.8,
                        "height": 170,
                        "weight": 65
                    }
                }
            }
    
    def demonstrate_vitals_collection(self, patient_data):
        """Demonstrate vitals collection system"""
        print("\n📊 === VITALS COLLECTION DEMO ===")
        print(f"Collecting vitals for sample patient...")
        
        # Collect vitals
        collected_vitals = self.vitals_system.collect_multiple_vitals(patient_data)
        
        print(f"✅ Collected {len(collected_vitals)} vital signs:")
        for vital_name, vital_sign in collected_vitals.items():
            status_emoji = {
                'normal': '✅',
                'high': '🔴',
                'low': '🔵',
                'critical': '🚨'
            }
            emoji = status_emoji.get(vital_sign.status, '❓')
            print(f"  {emoji} {vital_sign.name}: {vital_sign.value} {vital_sign.unit} ({vital_sign.status})")
        
        # Calculate derived vitals
        derived = self.vitals_system.calculate_derived_vitals()
        if derived:
            print(f"\n📈 Calculated {len(derived)} derived vital(s):")
            for vital_name, vital_sign in derived.items():
                print(f"  📊 {vital_sign.name}: {vital_sign.value:.1f} {vital_sign.unit}")
        
        # Get health score
        health_score = self.vitals_system.get_health_score()
        print(f"\n🎯 Health Score: {health_score['score']}/100 - {health_score['grade']}")
        
        # Get summary
        summary = self.vitals_system.get_vitals_summary()
        if summary['critical_vitals']:
            print("🚨 CRITICAL VITALS DETECTED!")
            for vital in summary['critical_vitals']:
                print(f"  ⚠️ {vital['name']}: {vital['value']} {vital['unit']}")
        
        return {name: vs.value for name, vs in collected_vitals.items()}
    
    async def demonstrate_ai_assessment(self, vitals_data, language='en'):
        """Demonstrate AI health assessment"""
        print(f"\n🤖 === AI HEALTH ASSESSMENT DEMO ({language.upper()}) ===")
        
        # Sample health queries
        sample_queries = {
            'en': [
                "What do my vital signs indicate about my health?",
                "Should I be concerned about my blood pressure?",
                "What are the next steps I should take?"
            ],
            'hi': [
                "मेरे जीवन संकेत मेरे स्वास्थ्य के बारे में क्या बताते हैं?",
                "क्या मुझे अपने रक्तचाप के बारे में चिंता करनी चाहिए?"
            ],
            'kn': [
                "ನನ್ನ ಪ್ರಾಣ ಸಂಕೇತಗಳು ನನ್ನ ಆರೋಗ್ಯದ ಬಗ್ಗೆ ಏನು ಸೂಚಿಸುತ್ತವೆ?",
                "ನನ್ನ ರಕ್ತದೊತ್ತಡದ ಬಗ್ಗೆ ನಾನು ಚಿಂತಿಸಬೇಕೇ?"
            ]
        }
        
        queries = sample_queries.get(language, sample_queries['en'])
        
        for i, query in enumerate(queries[:2], 1):  # Limit to 2 queries for demo
            print(f"\n💬 Query {i}: {query}")
            print("🔄 Generating AI response...")
            
            try:
                response = await self.ai_agent.generate_response(
                    user_input=query,
                    vitals_data=vitals_data,
                    language=language
                )
                
                print(f"🤖 AI Response: {response['response']}")
                
                if response.get('health_assessment'):
                    print(f"📋 Assessment: {response['health_assessment']}")
                
                if response.get('risk_level'):
                    risk_emoji = {
                        'low': '🟢',
                        'moderate': '🟡',
                        'high': '🔴',
                        'emergency': '🚨'
                    }
                    emoji = risk_emoji.get(response['risk_level'], '❓')
                    print(f"{emoji} Risk Level: {response['risk_level'].title()}")
                
                if response.get('recommendations'):
                    print("💡 Recommendations:")
                    for rec in response['recommendations']:
                        print(f"  • {rec}")
                
                print("-" * 50)
                
            except Exception as e:
                print(f"❌ Error generating AI response: {str(e)}")
    
    async def demonstrate_first_aid(self, language='en'):
        """Demonstrate first aid guidance"""
        print(f"\n🚑 === FIRST AID GUIDANCE DEMO ({language.upper()}) ===")
        
        conditions = ["Heart Attack", "Choking", "Severe Bleeding"]
        
        for condition in conditions[:1]:  # Demo with one condition
            print(f"\n🆘 Getting first aid guidance for: {condition}")
            try:
                guidance = self.ai_agent.get_first_aid_guidance(
                    condition=condition,
                    language=language
                )
                
                print(f"📋 Guidance: {guidance['response']}")
                
                if guidance.get('recommendations'):
                    print("⚡ Immediate Actions:")
                    for rec in guidance['recommendations']:
                        print(f"  • {rec}")
                
            except Exception as e:
                print(f"❌ Error getting first aid guidance: {str(e)}")
    
    def demonstrate_multilingual_support(self):
        """Demonstrate multilingual capabilities"""
        print("\n🌍 === MULTILINGUAL SUPPORT DEMO ===")
        
        languages = ['en', 'hi', 'kn']
        test_key = 'medical_disclaimer'
        
        for lang in languages:
            lang_name = self.multilingual.supported_languages[lang]
            translation = self.multilingual.get_translation(test_key, lang)
            print(f"\n🗣️ {lang_name} ({lang}):")
            print(f"   {translation}")
        
        # Demo medical terms glossary
        print("\n📚 Medical Terms Glossary:")
        glossary = self.multilingual.get_medical_terms_glossary('en')
        for term, translation in list(glossary.items())[:5]:
            print(f"  • {term}: {translation}")
    
    def demonstrate_data_export(self):
        """Demonstrate data export functionality"""
        print("\n📁 === DATA EXPORT DEMO ===")
        
        # Export as JSON
        json_data = self.vitals_system.export_vitals_data('json')
        print("✅ Vitals data exported as JSON:")
        print(f"   📄 Data size: {len(json_data)} characters")
        
        # Export as CSV
        csv_data = self.vitals_system.export_vitals_data('csv')
        print("✅ Vitals data exported as CSV:")
        print(f"   📊 Data size: {len(csv_data)} characters")
        
        # Show sample of JSON data
        try:
            data_preview = json.loads(json_data)
            print(f"\n📋 Sample JSON data (first entry):")
            first_key = list(data_preview.keys())[0]
            first_entry = data_preview[first_key]
            print(f"   {first_key}: {first_entry['value']} {first_entry['unit']} ({first_entry['status']})")
        except:
            print("   (Data preview unavailable)")
    
    async def run_full_demo(self):
        """Run the complete demo"""
        print("🚀 Starting Intel AI Healthcare Kiosk Full Demo")
        print("=" * 60)
        
        # Load sample data
        sample_data = self.load_sample_data()
        normal_patient = sample_data['sample_vitals']['normal_patient']
        
        # 1. Vitals Collection Demo
        vitals_data = self.demonstrate_vitals_collection(normal_patient)
        
        # 2. Multilingual Support Demo
        self.demonstrate_multilingual_support()
        
        # 3. AI Assessment Demo (English)
        await self.demonstrate_ai_assessment(vitals_data, 'en')
        
        # 4. AI Assessment Demo (Hindi) - if time permits
        print("\n🔄 Testing Hindi language support...")
        await self.demonstrate_ai_assessment(vitals_data, 'hi')
        
        # 5. First Aid Demo
        await self.demonstrate_first_aid('en')
        
        # 6. Data Export Demo
        self.demonstrate_data_export()
        
        # Summary
        print("\n🎉 === DEMO COMPLETE ===")
        print("✅ All major features demonstrated successfully!")
        print("\n📋 Features Showcased:")
        print("  • 28 Vital Signs Collection & Analysis")
        print("  • AI-Powered Health Assessment")
        print("  • Multilingual Support (EN/HI/KN)")
        print("  • First Aid Guidance")
        print("  • Health Score Calculation")
        print("  • Data Export (JSON/CSV)")
        print("  • Medical Disclaimers & Safety")
        
        print(f"\n🌐 To launch the full web interface:")
        print(f"   streamlit run app.py")
        print(f"\n🔧 Or run the setup script:")
        print(f"   python setup.py")

def main():
    """Main demo function"""
    demo = HealthcareKioskDemo()
    
    # Check if this is a quick test or full demo
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        print("🏃‍♀️ Running quick vitals collection test...")
        sample_data = demo.load_sample_data()
        demo.demonstrate_vitals_collection(sample_data['sample_vitals']['normal_patient'])
    else:
        # Run full async demo
        asyncio.run(demo.run_full_demo())

if __name__ == "__main__":
    main()
