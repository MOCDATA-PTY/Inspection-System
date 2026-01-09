"""
Create token.pickle using the authorization code from the OAuth callback
"""
import json
import pickle
import requests
from google.oauth2.credentials import Credentials

# Authorization code from the server logs
AUTH_CODE = '4/0Ab32j91qVpmRSoPBkO7bz8Z7qDe3Z59IWBKNyVPvkVPcRcLMQz9_L_gnY5rGMibzz1Q4bg'
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.pickle'
REDIRECT_URI = 'http://127.0.0.1:8000/google-sheets/oauth2callback/'

print("\n" + "="*80)
print("Creating token.pickle")
print("="*80 + "\n")

# Load credentials
with open(CREDENTIALS_FILE, 'r') as f:
    creds_data = json.load(f)

if 'web' in creds_data:
    client_config = creds_data['web']
elif 'installed' in creds_data:
    client_config = creds_data['installed']
else:
    print("[ERROR] Invalid credentials.json")
    exit(1)

client_id = client_config['client_id']
client_secret = client_config['client_secret']
token_uri = client_config['token_uri']

print(f"[INFO] Exchanging authorization code for tokens...")

# Exchange code for tokens
response = requests.post(token_uri, data={
    'code': AUTH_CODE,
    'client_id': client_id,
    'client_secret': client_secret,
    'redirect_uri': REDIRECT_URI,
    'grant_type': 'authorization_code'
})

if response.status_code != 200:
    print(f"[ERROR] Failed: {response.text}")
    exit(1)

token_response = response.json()
print("[SUCCESS] Obtained tokens!")

# Create credentials
creds = Credentials(
    token=token_response['access_token'],
    refresh_token=token_response.get('refresh_token'),
    token_uri=token_uri,
    client_id=client_id,
    client_secret=client_secret,
    scopes=token_response.get('scope', '').split()
)

# Save
with open(TOKEN_FILE, 'wb') as token:
    pickle.dump(creds, token)

print(f"[SUCCESS] token.pickle created!")
print(f"[INFO] File location: {TOKEN_FILE}")
print("\n" + "="*80)
print("DONE! Google Sheets authentication is now configured.")
print("="*80 + "\n")
