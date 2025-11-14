import os
import sys
import django
import zipfile
import tempfile
from datetime import datetime
import re

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
from main.models import FoodSafetyAgencyInspection

def find_existing_documents(inspection_ids):
    """Find existing documents for specific inspection IDs in the media folder."""
    print(f"🔍 Looking for existing documents for inspections: {inspection_ids}")
    
    # Get specific inspections
    inspections = FoodSafetyAgencyInspection.objects.filter(remote_id__in=inspection_ids)
    
    if not inspections.exists():
        print(f"❌ No inspections found with IDs: {inspection_ids}")
        return None, None
    
    print(f"✅ Found {inspections.count()} inspections")
    
    all_documents = []
    base_paths = set()
    
    for inspection in inspections:
        print(f"\n🔍 Processing inspection {inspection.remote_id} - Commodity: {inspection.commodity}")
        
        # Build the expected folder path
        date_str = inspection.date_of_inspection.strftime('%Y%m%d')
        year_folder = date_str[:4]
        month_num = int(date_str[4:6]) if len(date_str) >= 6 else int(datetime.now().strftime('%m'))
        month_folder = datetime.strptime(f"2023-{month_num:02d}-01", "%Y-%m-%d").strftime("%B")
        
        client_folder = re.sub(r'[^a-zA-Z0-9_]', '', inspection.client_name)
        client_folder = re.sub(r'_+', '_', client_folder).strip('_')
        
        base_path = os.path.join(settings.MEDIA_ROOT, 'inspection', year_folder, month_folder, client_folder)
        base_paths.add(base_path)
        
        print(f"📂 Looking for documents in: {base_path}")
        
        if not os.path.exists(base_path):
            print(f"❌ Folder does not exist: {base_path}")
            continue
        
        # Look for all document types
        document_types = ['Compliance', 'rfi', 'invoice', 'lab', 'retest']
        
        for doc_type in document_types:
            doc_path = os.path.join(base_path, doc_type)
            if os.path.exists(doc_path):
                print(f"✅ Found {doc_type} folder")
                
                # Walk through all subdirectories and files
                for root, dirs, files in os.walk(doc_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, base_path)
                        all_documents.append({
                            'path': file_path,
                            'relative_path': relative_path,
                            'type': doc_type,
                            'inspection_id': inspection.remote_id
                        })
                        print(f"📎 Found document: {relative_path}")
            else:
                print(f"❌ No {doc_type} folder found")
    
    return all_documents, list(base_paths)

def create_document_zip(documents, base_paths):
    """Create a zip file with all found documents."""
    print("📦 Creating document package...")
    
    if not documents:
        print("❌ No documents found to zip")
        return None
    
    # Create temporary zip file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"Ascend_Investment_Holding_Documents_{timestamp}.zip"
    zip_path = os.path.join(tempfile.gettempdir(), zip_filename)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for doc in documents:
            try:
                zipf.write(doc['path'], doc['relative_path'])
                print(f"📎 Added to zip: {doc['relative_path']}")
            except Exception as e:
                print(f"❌ Error adding {doc['relative_path']}: {e}")
    
    print(f"✅ Created zip file: {zip_path}")
    print(f"📊 Total documents included: {len(documents)}")
    return zip_path

def send_email_with_attachment(zip_path, recipient_email):
    """Send email with attachment using Gmail API."""
    print(f"📧 Sending email to {recipient_email}...")
    
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        import base64
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.base import MIMEBase
        from email import encoders
        import pickle
        
        # Gmail API scopes
        SCOPES = ['https://www.googleapis.com/auth/gmail.send']
        
        # Get Gmail service
        creds = None
        token_path = 'token.gmail.pickle'
        credentials_path = 'credentials.json'
        
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=8081, redirect_uri_trailing_slash=True)
            
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        service = build('gmail', 'v1', credentials=creds)
        
        # Create email
        message = MIMEMultipart('mixed')
        message['to'] = recipient_email
        message['subject'] = f'Food Safety Agency - Ascend Investment Holding Documents - {datetime.now().strftime("%d/%m/%Y")}'
        
        # Email body
        body = f"""
Good day,

We trust this email finds you well.

Please find attached the documentation pertaining to the inspection(s) conducted at Ascend Investment Holding (PTY) LTD/ Xing Xing facility.

Inspection Overview:
- Client: Ascend Investment Holding (PTY) LTD/ Xing Xing
- Account Code: FA-IND-EGG-NA-0014
- Commodities Inspected: EGGS
- Inspection IDs: 16372, 16370
- Date: 2025-09-03

Commodity Breakdown:
EGGS (Regulation R.1283 of 4 October 2019)
   - Status: Compliant
   - Attachments: Compliance documents

Compliance Summary:
All commodities are compliant.

Included in this email:
- Compliance Certificate
- Request for Information (if available)
- Laboratory Analysis Report (if available)
- Invoice (if available)

Please take note:
- Should a direction have been issued, a follow-up inspection will be scheduled in line with the specified rectification timeframe.
- That our fees have been gazetted and of our appointment by the Minister of Agriculture.

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
        """.strip()
        
        # Add text part
        text_part = MIMEText(body, 'plain')
        message.attach(text_part)
        
        # Add attachment
        with open(zip_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {os.path.basename(zip_path)}'
        )
        message.attach(part)
        
        # Encode and send
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        sent_message = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        print(f"✅ Email sent successfully! Message ID: {sent_message['id']}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

def main():
    """Main function to find existing documents and send them via email."""
    inspection_ids = [16372, 16370]  # The specific inspections you mentioned
    recipient_email = "ethansevenster621@gmail.com"
    
    print("🚀 Starting document collection and email process...")
    print(f"📧 Target email: {recipient_email}")
    print(f"🔍 Target inspections: {inspection_ids}")
    
    # Find existing documents
    documents, base_paths = find_existing_documents(inspection_ids)
    
    if not documents:
        print("❌ No documents found")
        return
    
    print(f"✅ Found {len(documents)} documents")
    
    # Create zip file
    zip_path = create_document_zip(documents, base_paths)
    
    if not zip_path:
        print("❌ Failed to create zip file")
        return
    
    # Send email
    success = send_email_with_attachment(zip_path, recipient_email)
    
    if success:
        print("🎉 Process completed successfully!")
        print(f"📧 Email sent to: {recipient_email}")
        print(f"📎 Attachment: {os.path.basename(zip_path)}")
    else:
        print("❌ Failed to send email")
    
    # Clean up
    try:
        os.remove(zip_path)
        print(f"🗑️ Cleaned up temporary file: {os.path.basename(zip_path)}")
    except:
        pass

if __name__ == "__main__":
    main()
