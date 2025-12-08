#!/usr/bin/env python
"""
Scan media folder and show all files organized by client
Can filter by client name pattern (e.g., clients starting with "New")
"""
import os
import sys
from pathlib import Path
from collections import defaultdict

def scan_media_folder(media_path='media', filter_pattern=None):
    """
    Scan media folder and organize files by client.

    Args:
        media_path: Path to media folder
        filter_pattern: Optional string to filter clients (e.g., "New" to find clients starting with "New")
    """

    if not os.path.exists(media_path):
        print(f"ERROR: Media folder not found at: {media_path}")
        return

    print("="*100)
    print("MEDIA FOLDER SCANNER")
    print("="*100)
    print(f"Scanning: {os.path.abspath(media_path)}")
    if filter_pattern:
        print(f"Filter: Clients containing '{filter_pattern}'")
    print("="*100)

    # Dictionary to store client -> files mapping
    client_files = defaultdict(list)
    total_files = 0
    total_size = 0

    # Walk through media folder
    for root, dirs, files in os.walk(media_path):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, media_path)

            # Extract client name from path (assuming structure: media/ClientName/...)
            path_parts = rel_path.split(os.sep)
            if len(path_parts) > 0:
                client_name = path_parts[0]

                # Get file info
                try:
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    total_files += 1

                    client_files[client_name].append({
                        'name': file,
                        'path': rel_path,
                        'size': file_size,
                        'full_path': file_path
                    })
                except Exception as e:
                    print(f"Warning: Could not read {file_path}: {e}")

    # Filter clients if pattern provided
    if filter_pattern:
        filtered_clients = {
            client: files for client, files in client_files.items()
            if filter_pattern.lower() in client.lower()
        }
        client_files = filtered_clients

    # Sort clients alphabetically
    sorted_clients = sorted(client_files.items())

    # Display results
    print(f"\n{'='*100}")
    print(f"RESULTS: Found {len(sorted_clients)} clients with {total_files} total files ({format_size(total_size)})")
    print(f"{'='*100}\n")

    for client_name, files in sorted_clients:
        total_client_size = sum(f['size'] for f in files)
        print(f"\n[{client_name}]")
        print(f"  Files: {len(files)} ({format_size(total_client_size)})")
        print("-" * 100)

        # Sort files by path
        sorted_files = sorted(files, key=lambda x: x['path'])

        for file_info in sorted_files:
            print(f"  - {file_info['path']}")
            print(f"    Size: {format_size(file_info['size'])}")

    # Summary
    print(f"\n{'='*100}")
    print("SUMMARY")
    print(f"{'='*100}")
    print(f"Total Clients: {len(sorted_clients)}")
    print(f"Total Files: {total_files}")
    print(f"Total Size: {format_size(total_size)}")

    # Show clients with no files
    empty_clients = [client for client, files in sorted_clients if len(files) == 0]
    if empty_clients:
        print(f"\nClients with NO files: {len(empty_clients)}")
        for client in empty_clients:
            print(f"  - {client}")

    # Show clients starting with "New"
    new_clients = [client for client in client_files.keys() if client.lower().startswith('new')]
    if new_clients and not filter_pattern:
        print(f"\nClients starting with 'New': {len(new_clients)}")
        for client in sorted(new_clients):
            file_count = len(client_files[client])
            client_size = sum(f['size'] for f in client_files[client])
            print(f"  - {client}: {file_count} files ({format_size(client_size)})")

    print(f"{'='*100}\n")

    return client_files

def format_size(size_bytes):
    """Format bytes into human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def save_to_file(client_files, output_file='media_scan_report.txt'):
    """Save scan results to a text file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("MEDIA FOLDER SCAN REPORT\n")
        f.write("="*100 + "\n\n")

        for client_name, files in sorted(client_files.items()):
            f.write(f"\n[{client_name}] - {len(files)} files\n")
            f.write("-" * 100 + "\n")
            for file_info in sorted(files, key=lambda x: x['path']):
                f.write(f"  {file_info['path']} ({format_size(file_info['size'])})\n")

    print(f"Report saved to: {output_file}")

if __name__ == '__main__':
    # Check for command line arguments
    filter_pattern = None
    save_report = False

    if len(sys.argv) > 1:
        if sys.argv[1] == '--help' or sys.argv[1] == '-h':
            print("Usage:")
            print("  python scan_media_files.py                    # Scan all files")
            print("  python scan_media_files.py New                # Filter clients containing 'New'")
            print("  python scan_media_files.py New --save         # Filter and save report to file")
            print("  python scan_media_files.py --save             # Scan all and save report")
            sys.exit(0)

        if '--save' in sys.argv:
            save_report = True
            sys.argv.remove('--save')

        if len(sys.argv) > 1:
            filter_pattern = sys.argv[1]

    # Scan media folder
    client_files = scan_media_folder('media', filter_pattern)

    # Save report if requested
    if save_report and client_files:
        report_name = f'media_scan_report{"_" + filter_pattern if filter_pattern else ""}.txt'
        save_to_file(client_files, report_name)
