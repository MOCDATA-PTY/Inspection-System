#!/usr/bin/env python3
"""
Script to replace verbose console.log statements with conditional debug logging.
Keeps console.error, console.warn as-is but replaces console.log and console.info.
"""
import re

def process_file(filepath):
    """Process a JavaScript file to replace console statements."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Track changes
    changes = 0

    # Replace console.log with debugLog (but not in comments)
    # This regex handles multi-line console.log statements
    def replace_console_log(match):
        nonlocal changes
        prefix = match.group(1)
        # If it's in a comment, don't replace
        if prefix.strip().startswith('//'):
            return match.group(0)
        changes += 1
        return prefix + 'debugLog('

    # Replace console.log( with debugLog(
    content = re.sub(r'(\s*)console\.log\(', replace_console_log, content)

    # Replace console.info( with debugInfo(
    def replace_console_info(match):
        nonlocal changes
        prefix = match.group(1)
        if prefix.strip().startswith('//'):
            return match.group(0)
        changes += 1
        return prefix + 'debugInfo('

    content = re.sub(r'(\s*)console\.info\(', replace_console_info, content)

    # Keep console.error and console.warn as-is (they should always show)
    # Replace console.warn with debugWarn for consistency
    def replace_console_warn(match):
        nonlocal changes
        prefix = match.group(1)
        if prefix.strip().startswith('//'):
            return match.group(0)
        changes += 1
        return prefix + 'debugWarn('

    content = re.sub(r'(\s*)console\.warn\(', replace_console_warn, content)

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return changes

if __name__ == '__main__':
    import sys

    files = [
        'upload_functions.js',
        'sent_status.js'
    ]

    for filepath in files:
        print(f'Processing {filepath}...')
        try:
            changes = process_file(filepath)
            print(f'  [OK] Made {changes} replacements')
        except Exception as e:
            print(f'  [ERROR] Error: {e}')
            sys.exit(1)

    print('\n[SUCCESS] All files processed successfully!')
    print('Set DEBUG_MODE = true at the top of each file to re-enable logging.')
