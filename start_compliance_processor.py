#!/usr/bin/env python
"""
Background Compliance Document Processor
========================================

This script runs the compliance document processor in the background.
It finds and downloads compliance documents from Google Drive every 5 minutes.

Usage:
    python start_compliance_processor.py

The process will:
1. Check for recent inspections (last 7 days)
2. Find matching compliance documents in Google Drive
3. Download them to organized folders: media/inspection/YYYY/Month/ClientName/Compliance/COMMODITY
4. Repeat every 5 minutes

Press Ctrl+C to stop the process.
"""

import os
import sys
import django

# Setup Django
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    django.setup()
    
    from django.core.management import execute_from_command_line
    
    print("🚀 Starting Compliance Document Background Processor")
    print("=" * 60)
    print("📋 Processing recent inspections every 5 minutes")
    print("📁 Organizing documents by: media/inspection/YYYY/Month/ClientName/Compliance/COMMODITY")
    print("⏹️  Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        # Run the management command continuously
        execute_from_command_line([
            'manage.py', 
            'process_compliance_documents',
            '--batch-size=100'
        ])
    except KeyboardInterrupt:
        print("\n⏹️ Background processor stopped")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
