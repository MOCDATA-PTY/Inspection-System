# OneDrive Auto-Upload Feature

This feature automatically uploads inspection files to OneDrive after they have been marked as sent for 3+ days.

## 🚀 Features

- **Automatic Upload**: Uploads inspection files to OneDrive after 3 days of being marked as sent
- **Organized Structure**: Creates organized folder structure by year/month/inspection
- **File Collection**: Collects all related files (compliance docs, RFI, inspection files)
- **Background Processing**: Runs as a background service
- **Error Handling**: Robust error handling and logging
- **Summary Files**: Creates summary files with inspection details

## 📁 Folder Structure

OneDrive will be organized as follows:
```
Food Safety Agency/
├── 2025/
│   ├── 01-January 2025/
│   │   ├── Inspection_12345_ClientName/
│   │   │   ├── compliance_doc1.pdf
│   │   │   ├── rfi_document.pdf
│   │   │   ├── inspection_files/
│   │   │   └── inspection_summary.txt
│   │   └── Inspection_12346_AnotherClient/
│   └── 02-February 2025/
└── 2026/
```

## 🛠️ Setup

### 1. Database Migration
First, apply the database migration for the new OneDrive tracking fields:
```bash
python manage.py migrate
```

### 2. OneDrive Connection
Ensure OneDrive is connected by running:
```bash
python check_onedrive_status.py
```

If not connected, complete the OAuth flow using the authorization URL.

## 🚀 Usage

### Manual Upload
Run the upload process once:
```bash
python manage.py onedrive_auto_upload
```

### Dry Run
See what would be uploaded without actually uploading:
```bash
python manage.py onedrive_auto_upload --dry-run
```

### Statistics
View upload statistics:
```bash
python manage.py onedrive_auto_upload --stats
```

### Background Scheduler
Run as a background service that checks every hour:
```bash
python manage.py run_onedrive_scheduler
```

Or use the Windows batch file:
```bash
start_onedrive_scheduler.bat
```

## 🔧 Configuration

### Scheduler Options
- `--interval`: Set check interval in seconds (default: 3600 = 1 hour)
- `--max-runs`: Set maximum number of runs (0 = unlimited)

Example:
```bash
python manage.py run_onedrive_scheduler --interval 1800 --max-runs 10
```

## 📊 Monitoring

### Upload Statistics
The system tracks:
- Total inspections marked as sent
- Total uploaded to OneDrive
- Pending uploads
- Upload completion percentage

### Logging
All operations are logged with timestamps and status messages.

## 🧪 Testing

Run the test suite:
```bash
python test_onedrive_auto_upload.py
```

This will test:
- OneDrive connection
- Inspection queries
- Dry run functionality
- Optional actual upload test

## 📋 File Collection

The system collects files from:
1. **Compliance Documents**: From `compliance_documents` relationship
2. **RFI Documents**: From `rfi_documents` relationship  
3. **Inspection Files**: From `media/inspections/{inspection_id}/`
4. **Main Files**: From `media/inspection_files/{inspection_id}/`

## 🔄 Process Flow

1. **Query**: Find inspections marked as sent 3+ days ago
2. **Group**: Group by month for organized folder structure
3. **Create Folders**: Create year/month/inspection folder structure
4. **Collect Files**: Gather all related files for each inspection
5. **Upload**: Upload files to OneDrive
6. **Update Status**: Mark inspection as uploaded
7. **Summary**: Create inspection summary file

## ⚠️ Requirements

- OneDrive must be connected (OAuth completed)
- Inspections must be marked as sent (`sent_status=True`)
- Inspections must have been sent 3+ days ago
- Files must exist in the expected directories

## 🐛 Troubleshooting

### OneDrive Connection Issues
```bash
python check_onedrive_status.py
```

### No Inspections Found
- Check if inspections are marked as sent
- Verify sent dates are 3+ days ago
- Check database for inspection data

### Upload Failures
- Check OneDrive permissions
- Verify file paths exist
- Check network connectivity
- Review error logs

## 📝 Database Fields

New fields added to `FoodSafetyAgencyInspection`:
- `onedrive_uploaded`: Boolean flag for upload status
- `onedrive_upload_date`: Timestamp of upload
- `onedrive_folder_id`: OneDrive folder ID for reference

## 🔒 Security

- Uses OAuth 2.0 for secure OneDrive access
- Tokens are stored securely in `onedrive_tokens.json`
- Automatic token refresh when needed
- No sensitive data in logs

## 📈 Performance

- Processes inspections in monthly batches
- Handles large file uploads efficiently
- Background processing doesn't block main application
- Configurable intervals for resource management
