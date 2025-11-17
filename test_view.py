"""
Media file serving view
"""

import os
import mimetypes
from django.http import FileResponse, Http404
from django.conf import settings


def serve_media_file(request, path):
    """Serve media files from /media/ URL"""

    # Build full path
    file_path = os.path.join(settings.MEDIA_ROOT, path.replace('/', os.sep))

    # Security check - ensure file is within MEDIA_ROOT
    real_path = os.path.realpath(file_path)
    media_root_real = os.path.realpath(settings.MEDIA_ROOT)

    if not real_path.startswith(media_root_real):
        raise Http404("Access denied")

    # Check if file exists
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise Http404(f"File not found: {path}")

    # Determine content type
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        content_type = 'application/octet-stream'

    # Serve the file
    return FileResponse(
        open(file_path, 'rb'),
        content_type=content_type,
        as_attachment=False
    )


def test_media_file(request):
    """Test serving the RFI file directly"""

    # The file we want to serve
    relative_path = "inspection/2025/November/avonlea_farm_cc/rfi/FSA-RFI-DU-251117.pdf"

    # Build full path
    file_path = os.path.join(settings.MEDIA_ROOT, relative_path.replace('/', os.sep))

    print(f"\n{'='*100}")
    print("TEST VIEW - Attempting to serve file")
    print(f"{'='*100}")
    print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print(f"Relative path: {relative_path}")
    print(f"Full path: {file_path}")
    print(f"File exists: {os.path.exists(file_path)}")
    print(f"Is file: {os.path.isfile(file_path)}")

    if os.path.exists(file_path):
        print(f"File size: {os.path.getsize(file_path):,} bytes")
        print(f"{'='*100}\n")

        # Serve the file
        return FileResponse(
            open(file_path, 'rb'),
            content_type='application/pdf',
            as_attachment=False,
            filename='FSA-RFI-DU-251117.pdf'
        )
    else:
        print(f"ERROR: File not found!")
        print(f"{'='*100}\n")
        raise Http404("File not found in test view")
