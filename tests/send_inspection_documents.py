import os
import zipfile
import argparse
from datetime import datetime
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service(credentials_path, token_path):
    """Get Gmail service with authentication."""
    creds = None
    
    # Load existing token
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=8081, redirect_uri_trailing_slash=True)
        
        # Save the credentials for the next run
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('gmail', 'v1', credentials=creds)

def create_zip_file(inspection_id, output_filename):
    """Create a zip file containing all inspection documents."""
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add all document files
        files_to_add = [
            f'RFI_{inspection_id}.txt',
            f'Lab_Results_{inspection_id}.txt',
            f'Invoice_{inspection_id}.txt',
            f'Compliance_{inspection_id}.txt'
        ]
        
        for filename in files_to_add:
            if os.path.exists(filename):
                zipf.write(filename, filename)
                print(f"✅ Added {filename} to zip")
            else:
                print(f"⚠️  Warning: {filename} not found")
    
    print(f"✅ Created zip file: {output_filename}")
    return output_filename

def send_email_with_attachment(service, to_email, subject, body, attachment_path):
    """Send email with attachment using Gmail API."""
    try:
        # Create message
        message = MIMEMultipart('mixed')
        message['to'] = to_email
        message['subject'] = subject
        
        # Create the related part for HTML and inline images
        related_part = MIMEMultipart('related')
        message.attach(related_part)
        
        # Create the alternative part for text and HTML
        alternative_part = MIMEMultipart('alternative')
        related_part.attach(alternative_part)
        
        # Add text version
        text_part = MIMEText(body, 'plain')
        alternative_part.attach(text_part)
        
        # Create HTML version with signature image
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <p>{body.replace(chr(10), '<br>')}</p>
        <br><br>
        <img src="cid:signature" alt="Food Safety Agency Signature" style="max-width: 500px; width: 100%; display: block; margin: 20px 0;">
        </body>
        </html>
        """
        
        # Add HTML version
        html_text_part = MIMEText(html_body, 'html')
        alternative_part.attach(html_text_part)
        
        # Add signature image as inline
        if os.path.exists('main/download.png'):
            with open('main/download.png', 'rb') as img:
                img_part = MIMEBase('image', 'png')
                img_part.set_payload(img.read())
            
            encoders.encode_base64(img_part)
            img_part.add_header('Content-ID', '<signature>')
            img_part.add_header('Content-Disposition', 'inline', filename='signature.png')
            related_part.attach(img_part)
            print("✅ Signature image embedded successfully")
        else:
            print("⚠️  Warning: Signature image not found at main/download.png")
        
        # Add attachment separately
        with open(attachment_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {os.path.basename(attachment_path)}'
        )
        message.attach(part)
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Send email
        sent_message = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        return sent_message
        
    except HttpError as error:
        print(f'❌ An error occurred: {error}')
        return None

def main():
    parser = argparse.ArgumentParser(description='Send inspection documents via email')
    parser.add_argument('--inspection-id', required=True, help='Inspection ID')
    parser.add_argument('--to', required=True, help='Recipient email address')
    parser.add_argument('--subject', default='Food Safety Agency Inspection Documents', 
                       help='Email subject')
    parser.add_argument('--inspection-date', help='Date of inspection (DD/MM/YYYY format)')
    parser.add_argument('--commodity', default='RAW', help='Commodity type (RAW, PMP, POULTRY, EGGS)')
    parser.add_argument('--credentials', default='credentials.json', 
                       help='Path to credentials.json file')
    parser.add_argument('--token', default='token.gmail.pickle', 
                       help='Path to token pickle file')
    
    args = parser.parse_args()
    
    # Create zip file
    zip_filename = f'Inspection_Documents_{args.inspection_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
    zip_path = create_zip_file(args.inspection_id, zip_filename)
    
    # Get Gmail service
    print("🔐 Authenticating with Gmail API...")
    service = get_gmail_service(args.credentials, args.token)
    
    # Email content
    email_body = f"""
Good day,

We trust this email finds you well.

Please find attached the documentation pertaining to the inspection(s) conducted at your facility on the {args.inspection_date if hasattr(args, 'inspection_date') else datetime.now().strftime('%d/%m/%Y')}:

Inspection Overview:
- Test ID:              {args.inspection_id}
- Date Inspected:        {args.inspection_date if hasattr(args, 'inspection_date') else datetime.now().strftime('%d/%m/%Y')}
- Commodities Inspected: {args.commodity if hasattr(args, 'commodity') else 'RAW'}

Commodity Breakdown:

{args.commodity if hasattr(args, 'commodity') else 'RAW'} (Regulation R.1283 of 4 October 2019)
   - Status: Compliant
   - Attachments: 4
   - Direction: 0

Compliance Summary:
All commodities are compliant.

Included in this email:
- Request for Information
- Laboratory Analysis Report
- Invoice
- Compliance Certificate

Please take note:

Should a direction have been issued, a follow-up inspection will be scheduled in line with the specified rectification timeframe.
That our fees have been gazetted and of our appointment by the Minister of Agriculture.

For any queries related to this inspection, invoicing, or to provide feedback, please don't hesitate to contact our team:

Manager: Agricultural Products Standards
Ms. Palesa Mpana: palesa.mpana@fsa-pty.co.za

Manager: Compliance
Ms. Nicole Bergh: nicole.bergh@fsa-pty.co.za

General Enquiries:
Email: Info@afsq.co.za / Call: (012) 361-1937

We trust that you will find the attached and above in order and appreciate your cooperation towards greater quality standards.

Kind regards,
The Food Safety Agency (Pty) Ltd
www.foodsafetyagency.co.za
"""
    
    # Send email
    print(f"📧 Sending email to {args.to}...")
    result = send_email_with_attachment(
        service, 
        args.to, 
        args.subject, 
        email_body, 
        zip_path
    )
    
    if result:
        print(f"✅ Email sent successfully! Message ID: {result['id']}")
        print(f"📎 Attachment: {zip_filename}")
    else:
        print("❌ Failed to send email")
    
    # Clean up zip file
    if os.path.exists(zip_path):
        os.remove(zip_path)
        print(f"🗑️  Cleaned up temporary file: {zip_filename}")

if __name__ == "__main__":
    main()
