# OneDrive Setup Instructions

## Step 1: Get Your Application (client) ID

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Find your app: **OneDriveAppIntegration**
4. Click on it to open the Overview page
5. Copy the **Application (client) ID** (it looks like: `12345678-1234-1234-1234-123456789abc`)

## Step 2: Update Settings

Replace `your_client_id_here` in `mysite/settings.py` with your actual Client ID:

```python
ONEDRIVE_CLIENT_ID = 'your-actual-client-id-here'
```

## Step 3: Test the Setup

Run the test script:
```bash
python test_onedrive_setup.py
```

This will:
- Verify your configuration
- Generate the authorization URL
- Open it in your browser
- Guide you through the OAuth flow

## Step 4: Complete OAuth Flow

1. The script will open a browser window
2. Sign in with your Microsoft account
3. Grant permissions to the app
4. You'll be redirected to: `http://localhost:8000/onedrive/callback`
5. Check for `onedrive_tokens.json` file in the project root

## Current Configuration Status

✅ Client Secret: Set  
✅ Redirect URI: http://localhost:8000/onedrive/callback  
✅ OneDrive Enabled: True  
❌ Client ID: Needs to be set  

## What Happens After Setup

Once you complete the OAuth flow:
- `onedrive_tokens.json` will be created with access and refresh tokens
- Your app will be able to upload/download files to/from OneDrive
- The integration will be fully functional
