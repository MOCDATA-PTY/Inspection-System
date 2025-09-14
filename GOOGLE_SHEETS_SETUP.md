# Google Sheets API Setup Guide

## Overview
This guide will help you set up Google Sheets API access to fetch data from your spreadsheet.

## Step 1: Enable Google Sheets API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click on it and press "Enable"

## Step 2: Create Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Desktop application" as the application type
4. Give it a name (e.g., "Food Safety Agency Sheets Access")
5. Click "Create"
6. Download the JSON file and rename it to `credentials.json`

## Step 3: Place Credentials File

1. Place the `credentials.json` file in your project root directory (same level as `manage.py`)
2. The file structure should look like:
   ```
   your-project/
   ├── manage.py
   ├── credentials.json  ← Place here
   ├── main/
   ├── mysite/
   └── ...
   ```

## Step 4: First Run Authentication

1. Start your Django server: `python manage.py runserver`
2. Navigate to the Client Allocation page: `/client-allocation/`
3. On first visit, a browser window will open for Google authentication
4. Sign in with your Google account and grant permissions
5. A `token.pickle` file will be created automatically

## Step 5: Verify Access

1. The Client Allocation page should now display data from your Google Sheet
2. Data will be fetched from columns H and J starting from row 2
3. The page shows:
   - Total row count
   - Data source information
   - Table with row numbers, column H values, and column J values

## Troubleshooting

### "credentials.json not found" Error
- Ensure the file is in the project root directory
- Check the file name spelling (must be exactly `credentials.json`)

### Authentication Errors
- Delete the `token.pickle` file and try again
- Ensure your Google account has access to the spreadsheet
- Check that the Google Sheets API is enabled

### Permission Errors
- Make sure the spreadsheet is shared with your Google account
- Verify the spreadsheet ID is correct in the code

## Security Notes

- Keep your `credentials.json` file secure and don't commit it to version control
- The `token.pickle` file contains your access tokens and should also be kept secure
- Consider using environment variables for production deployments

## API Limits

- Google Sheets API has quotas and rate limits
- Free tier allows 100 requests per 100 seconds per user
- Monitor usage in Google Cloud Console if you expect high traffic
