# API Key Setup Instructions

## Quick Fix for "StreamlitSecretNotFoundError"

If you're seeing the error `StreamlitSecretNotFoundError: No secrets found`, follow these steps:

### Option 1: Automated Setup (Recommended)

Run the setup script to configure your API key:

```bash
python setup_api_key.py
```

### Option 2: Manual Setup

#### Step 1: Get Google AI Studio API Key

1. Go to [Google AI Studio](https://ai.google.dev/)
2. Click "Get API key in Google AI Studio"
3. Sign in with your Google account
4. Create a new API key
5. Copy the API key

#### Step 2: Configure the API Key

**Method A: Using Streamlit Secrets (Recommended for Streamlit Cloud)**

1. Open `.streamlit/secrets.toml`
2. Replace `your-google-ai-studio-api-key-here` with your actual API key:

   ```toml
   GOOGLE_API_KEY = "your-actual-api-key-here"
   ```

**Method B: Using Environment Variables (Recommended for Local Development)**

1. Open `.env` file
2. Replace `your-google-ai-studio-api-key-here` with your actual API key:

   ```
   GOOGLE_API_KEY=your-actual-api-key-here
   ```

#### Step 3: Run the Application

```bash
streamlit run app.py
```

## Security Notes

- ⚠️ **Never commit your API keys to version control**
- The `.env` and `.streamlit/` files are already in `.gitignore`
- Keep your API keys secure and don't share them publicly

## Troubleshooting

- If you still get errors after setting the API key, restart the Streamlit application
- Make sure there are no extra spaces or quotes around your API key
- Verify your API key is active and has proper permissions in Google AI Studio
