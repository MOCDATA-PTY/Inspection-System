#!/usr/bin/env python3
"""
Analyze the structure of Script Section 4 to find where the unmatched braces and parentheses are
"""

import re
import os

def analyze_script_structure():
    template_path = 'main/templates/main/shipment_list_clean.html'
    
    if not os.path.exists(template_path):
        print(f"Error: Template file not found at {template_path}")
        return
    
    print("Reading template file...")
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find Script Section 4
    script_pattern = r'<script[^>]*>(.*?)</script>'
    scripts = re.findall(script_pattern, content, re.DOTALL)
    
    if len(scripts) < 4:
        print("Error: Could not find Script Section 4")
        return
    
    script_4 = scripts[3]
    print(f"Script Section 4 length: {len(script_4)} characters")
    
    # Count braces and parentheses
    open_braces = script_4.count('{')
    close_braces = script_4.count('}')
    open_parens = script_4.count('(')
    close_parens = script_4.count(')')
    
    print(f"Braces: {open_braces} open, {close_braces} close, diff: {open_braces - close_braces}")
    print(f"Parentheses: {open_parens} open, {close_parens} close, diff: {open_parens - close_parens}")
    
    # Let's analyze the script line by line to find where the imbalance occurs
    lines = script_4.split('\n')
    
    # Track brace and parenthesis balance as we go through the lines
    brace_balance = 0
    paren_balance = 0
    
    print(f"\nAnalyzing script line by line...")
    print(f"{'Line':<6} {'Braces':<8} {'Parens':<8} {'Content'}")
    print("-" * 80)
    
    problem_lines = []
    
    for i, line in enumerate(lines, 1):
        line_braces = line.count('{') - line.count('}')
        line_parens = line.count('(') - line.count(')')
        
        brace_balance += line_braces
        paren_balance += line_parens
        
        # Show lines where balance becomes negative (indicating problems)
        if brace_balance < 0 or paren_balance < 0:
            problem_lines.append((i, line.strip(), brace_balance, paren_balance))
            print(f"{i:<6} {brace_balance:<8} {paren_balance:<8} {line.strip()}")
    
    if problem_lines:
        print(f"\nFound {len(problem_lines)} lines with negative balance:")
        for line_num, content, brace_bal, paren_bal in problem_lines:
            print(f"Line {line_num}: braces={brace_bal}, parens={paren_bal} - {content}")
    else:
        print("\nNo lines with negative balance found")
    
    # Let's also check for specific patterns that might be problematic
    print(f"\nChecking for common syntax issues...")
    
    # Check for unmatched quotes
    single_quotes = script_4.count("'")
    double_quotes = script_4.count('"')
    
    if single_quotes % 2 != 0:
        print(f"❌ Unmatched single quotes: {single_quotes} total")
    else:
        print(f"✅ Single quotes balanced: {single_quotes} total")
    
    if double_quotes % 2 != 0:
        print(f"❌ Unmatched double quotes: {double_quotes} total")
    else:
        print(f"✅ Double quotes balanced: {double_quotes} total")
    
    # Check for common malformed patterns
    malformed_patterns = [
        r';\s*;',  # Double semicolons
        r'}\s*{',  # Missing semicolon between statements
        r'\)\s*\(',  # Missing operator between function calls
        r'function\s*\(',  # Anonymous function without proper syntax
    ]
    
    for pattern in malformed_patterns:
        matches = re.findall(pattern, script_4)
        if matches:
            print(f"❌ Found malformed pattern '{pattern}': {len(matches)} occurrences")
            for match in matches[:3]:  # Show first 3 examples
                print(f"   Example: {repr(match)}")
        else:
            print(f"✅ No malformed pattern '{pattern}' found")
    
    # Let's look at the end of the script more carefully
    print(f"\nLast 20 lines of script:")
    for i, line in enumerate(lines[-20:], len(lines)-19):
        print(f"{i:4d}: {line}")
    
    # Check if the script ends properly
    last_line = lines[-1].strip()
    if last_line.endswith('}') or last_line.endswith(');') or last_line.endswith('};'):
        print(f"✅ Script appears to end properly")
    else:
        print(f"❌ Script may not end properly - last line: {repr(last_line)}")

if __name__ == "__main__":
    analyze_script_structure()
