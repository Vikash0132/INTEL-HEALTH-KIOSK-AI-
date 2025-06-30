# Intel AI Healthcare Kiosk

An intelligent healthcare kiosk system that provides preliminary health assessments, first aid guidance, and multilingual support using Google AI Studio (Gemini).

## 🎯 Project Goals

### Phase 1: AI Core (Current Implementation)

1. **Conversational AI Agent** - Assisted first aid and health consultation
2. **Preliminary Diagnosis** - AI-powered health assessment based on vital signs
3. **Multilingual Support** - English, Hindi, and Kannada language support
4. **Vital Signs Collection** - Comprehensive system for 28 different vital signs

### Phase 2: Doctor Integration (Future)

1. **Appointment Scheduling** - Integration with healthcare providers
2. **Video Consultation** - Remote doctor consultations
3. **Treatment Plan Sharing** - Export AI assessments for doctor review

## 🏥 Features

### Current Features

- **28 Vital Signs Collection**: Heart rate, blood pressure, temperature, glucose, cholesterol, BMI, and more
- **AI Health Assistant**: Conversational agent powered by Google Gemini
- **Preliminary Health Assessment**: Risk analysis and recommendations
- **First Aid Guidance**: Emergency response instructions
- **Multilingual Interface**: Support for English, Hindi, and Kannada
- **Health Score Calculation**: Overall health assessment scoring
- **Data Export**: JSON and CSV export capabilities
- **Medical Disclaimers**: Appropriate warnings and professional consultation recommendations

### Vital Signs Supported

1. **Cardiovascular**: Heart rate, blood pressure (systolic/diastolic), pulse rate, mean arterial pressure
2. **Respiratory**: Respiratory rate, oxygen saturation
3. **Metabolic**: Body temperature, blood glucose
4. **Lipid Profile**: Total cholesterol, LDL, HDL, triglycerides
5. **Hematology**: Hemoglobin, white/red blood cells, platelets
6. **Anthropometric**: Height, weight, BMI, waist/hip circumference
7. **Body Composition**: Body fat percentage, muscle mass, bone density
8. **Sensory**: Vision acuity, hearing threshold

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Google AI Studio API key
- Windows/Linux/macOS

### Setup Instructions

1. **Clone the repository**

   ```bash
   cd c:\Users\vc041\intel-ai-kiosk
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   - Copy `.env.example` to `.env`
   - Add your Google AI Studio API key:

   ```
   GOOGLE_API_KEY=your_google_ai_studio_api_key_here
   ```

4. **Run the application**

   ```bash
   streamlit run app.py
   ```

5. **Access the kiosk**
   - Open your browser to `http://localhost:8501`
   - Select your preferred language
   - Start collecting vitals and chatting with the AI

## 📊 Usage Guide

### 1. Language Selection

- Choose from English, Hindi, or Kannada
- Interface and AI responses adapt to selected language

### 2. Vitals Collection

- Navigate to "Vitals Collection" section
- Enter measurements in organized categories
- System validates input and calculates derived values
- View health score and status summary

### 3. AI Health Chat

- Ask health-related questions
- Get preliminary assessments based on your vitals
- Receive personalized recommendations
- View risk level assessments

### 4. First Aid Guidance

- Select common emergency conditions
- Get step-by-step first aid instructions
- Receive emergency contact recommendations

### 5. Data Export

- Export vitals data as JSON or CSV
- Share with healthcare providers
- Maintain personal health records

## 🛡️ Medical Disclaimers

**IMPORTANT MEDICAL NOTICE:**

- This system provides **PRELIMINARY ASSESSMENTS ONLY**
- NOT a replacement for professional medical diagnosis
- Always consult qualified healthcare professionals
- In emergencies, contact emergency services immediately
- Do not use for life-threatening conditions

## 🏗️ Project Structure

```
intel-ai-kiosk/
├── .github/
│   └── copilot-instructions.md
├── config/
│   └── config.py                 # Configuration management
├── src/
│   ├── ai_agent.py              # Google AI Studio integration
│   ├── vitals_system.py         # Vital signs collection
│   └── multilingual_support.py  # Language support
├── data/                        # Data storage (future)
├── tests/                       # Test files (future)
├── app.py                       # Main Streamlit application
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
└── README.md                    # This file
```

## 🔧 Configuration

### Environment Variables

- `GOOGLE_API_KEY`: Google AI Studio API key (required)
- `APP_NAME`: Application name
- `DEBUG`: Debug mode (True/False)
- `SUPPORTED_LANGUAGES`: Language codes (en,hi,kn)

### Customization

- Modify `config/config.py` for application settings
- Update `src/multilingual_support.py` for additional languages
- Extend `src/vitals_system.py` for new vital signs

## 🧪 Testing

Run tests (when implemented):

```bash
python -m pytest tests/
```

## 📈 Development Roadmap

### Phase 1: AI Core ✅

- [x] Google AI Studio integration
- [x] 28 vital signs collection
- [x] Multilingual support (EN/HI/KN)
- [x] Streamlit web interface
- [x] Health assessment engine
- [x] First aid guidance

### Phase 2: Doctor Integration 🔄

- [ ] Appointment scheduling system
- [ ] Video consultation integration
- [ ] Doctor dashboard
- [ ] Treatment plan sharing
- [ ] Medical history management

### Phase 3: Advanced Features 📋

- [ ] Machine learning diagnosis models
- [ ] Wearable device integration
- [ ] Voice interaction
- [ ] Mobile application
- [ ] Hospital system integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with proper testing
4. Submit a pull request
5. Ensure medical accuracy and safety

## 📄 License

This project is for educational and research purposes. Ensure compliance with healthcare regulations in your jurisdiction.

## 🆘 Support

For technical support or medical guidance integration:

- Check the documentation in `.github/copilot-instructions.md`
- Review configuration in `config/config.py`
- Ensure API keys are properly configured

## ⚠️ Security & Privacy

- Patient data is processed locally
- No data transmitted without explicit consent
- Follow HIPAA/healthcare privacy guidelines
- Secure API key management required

---

**Intel AI Healthcare Kiosk** - Empowering preliminary health assessment with AI technology while emphasizing the importance of professional medical care.
