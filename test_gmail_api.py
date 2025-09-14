import os
import base64
import argparse
import pickle
from email.message import EmailMessage

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


# Scope required just to send mail
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def get_gmail_service(credentials_path: str, token_path: str):
    creds = None
    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            # You need to add this redirect URI to your Google Cloud Console:
# http://localhost:8081/
            creds = flow.run_local_server(port=8081, redirect_uri_trailing_slash=True)
        with open(token_path, "wb") as token:
            pickle.dump(creds, token)
    return build("gmail", "v1", credentials=creds)


def send_gmail_message(service, sender: str, to_email: str, subject: str, body: str):
    msg = EmailMessage()
    msg["To"] = to_email
    msg["From"] = sender
    msg["Subject"] = subject
    msg.set_content(body)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return service.users().messages().send(userId="me", body={"raw": raw}).execute()


def main():
    parser = argparse.ArgumentParser(description="Send a test email via Gmail API")
    parser.add_argument("--to", dest="to_email", default="ethansevenster621@gmail.com")
    parser.add_argument("--subject", default="FSA Gmail API Test")
    parser.add_argument("--body", default="This is a test email sent via the Gmail API.")
    parser.add_argument("--sender", default=None, help="Optional explicit From address; defaults to authorized account")
    parser.add_argument("--credentials", default=os.path.join(os.getcwd(), "credentials.json"))
    parser.add_argument("--token", default=os.path.join(os.getcwd(), "token.gmail.pickle"))

    args = parser.parse_args()

    service = get_gmail_service(args.credentials, args.token)

    result = send_gmail_message(
        service,
        sender=args.sender or "me",
        to_email=args.to_email,
        subject=args.subject,
        body=args.body,
    )

    msg_id = result.get("id")
    print(f"✅ Gmail API: message sent to {args.to_email} (id={msg_id})")


if __name__ == "__main__":
    main()


