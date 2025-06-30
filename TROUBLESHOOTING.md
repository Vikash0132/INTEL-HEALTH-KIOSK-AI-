# Troubleshooting Guide - Intel AI Healthcare Kiosk

## Common Issues and Solutions

### 🔑 API Key Issues

**Problem**: "Failed to initialize AI agent" or "GOOGLE_API_KEY is required"
**Solution**:

1. Ensure `.env` file exists in the project root
2. Check that `GOOGLE_API_KEY` is set correctly in `.env`
3. Get your API key from: <https://makersuite.google.com/app/apikey>
4. Verify the key is not wrapped in quotes unless needed

**Example `.env` file**:

```
GOOGLE_API_KEY=AIzaSyA_example_api_key_here
```

### 📦 Package Installation Issues

**Problem**: Import errors or missing packages
**Solution**:

```bash
# Update pip first
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# For specific package issues:
pip install google-generativeai streamlit pandas plotly
```

**Problem**: `googletrans` installation fails
**Solution**:

```bash
pip install googletrans==3.1.0a0
# or
pip install googletrans4
```

### 🌐 Streamlit Issues

**Problem**: Streamlit won't start or shows errors
**Solution**:

1. Check if port 8501 is available
2. Try running with a different port:

   ```bash
   streamlit run app.py --server.port 8502
   ```

3. Clear Streamlit cache:

   ```bash
   streamlit cache clear
   ```

**Problem**: "Address already in use" error
**Solution**:

```bash
# Windows - kill process on port 8501
netstat -ano | findstr :8501
taskkill /PID <process_id> /F

# Then restart
streamlit run app.py
```

### 🤖 AI Response Issues

**Problem**: AI responses are empty or error out
**Solution**:

1. Verify Google AI Studio API key is valid
2. Check internet connection
3. Ensure the API key has proper permissions
4. Try the demo script to test AI functionality:

   ```bash
   python demo.py --quick
   ```

**Problem**: AI responses are in wrong language
**Solution**:

1. Check language selection in the UI
2. Clear browser cache and cookies
3. Restart the Streamlit application

### 📊 Vitals Collection Issues

**Problem**: Vitals validation errors
**Solution**:

1. Check that values are within reasonable ranges
2. Ensure numeric inputs (no text in number fields)
3. Review the validation ranges in `src/vitals_system.py`

**Problem**: BMI or derived vitals not calculating
**Solution**:

1. Ensure both height and weight are entered
2. Check that values are positive numbers
3. Height should be in cm, weight in kg

### 🗣️ Multilingual Issues

**Problem**: Text not translating properly
**Solution**:

1. Check internet connection (Google Translate requires internet)
2. Verify language codes are correct (en, hi, kn)
3. Some medical terms may not translate perfectly

### 💾 Data Export Issues

**Problem**: Export buttons not working
**Solution**:

1. Ensure vitals data has been collected first
2. Check browser settings for download permissions
3. Try refreshing the page and re-collecting data

### 🐛 General Debugging

**Enable Debug Mode**:

1. Set `DEBUG=True` in `.env` file
2. Check browser console for JavaScript errors
3. Check terminal/command prompt for Python errors

**Clear All Data**:

1. Use "Clear Session" button in the sidebar
2. Or restart the application completely

**Reset Application**:

1. Stop the Streamlit app (Ctrl+C)
2. Clear cache: `streamlit cache clear`
3. Restart: `streamlit run app.py`

## Performance Optimization

### 🚀 Speed Up AI Responses

1. Use shorter, more specific prompts
2. Limit conversation history
3. Check internet connection speed

### 💻 Reduce Memory Usage

1. Clear vitals session regularly
2. Restart app periodically for long sessions
3. Close unnecessary browser tabs

## Security Best Practices

### 🔒 Protect API Keys

1. Never commit `.env` file to version control
2. Use different API keys for development/production
3. Regularly rotate API keys

### 🛡️ Patient Data Protection

1. Data is processed locally by default
2. No patient data is stored permanently
3. Clear sessions after each patient
4. Follow HIPAA guidelines for healthcare data

## Getting Help

### 📞 Support Contacts

- Technical Issues: Check project documentation
- Medical Accuracy: Consult healthcare professionals
- API Issues: Google AI Studio support

### 🔍 Useful Commands

```bash
# Test basic functionality
python demo.py --quick

# Full feature demonstration
python demo.py

# Check Python/package versions
python --version
pip list

# Test network connectivity
ping google.com

# Check if port is in use
netstat -an | findstr 8501
```

### 📝 Logging and Debugging

- Application logs appear in the terminal/command prompt
- Browser developer tools (F12) show frontend errors
- Add `print()` statements for custom debugging

## Environment Setup Verification

Run this checklist to verify your setup:

```bash
# 1. Check Python version (should be 3.8+)
python --version

# 2. Check if required packages are installed
python -c "import streamlit, google.generativeai, pandas; print('✅ Core packages OK')"

# 3. Check if .env file exists and has API key
python -c "from config.config import Config; Config.validate_config(); print('✅ Configuration OK')"

# 4. Test vitals system
python -c "from src.vitals_system import VitalsCollectionSystem; vs = VitalsCollectionSystem(); print('✅ Vitals system OK')"

# 5. Run quick demo
python demo.py --quick
```

If all checks pass, the system should work correctly!

---

**Need more help?** Check the main README.md for additional setup instructions and project details.
