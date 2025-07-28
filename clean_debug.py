#!/usr/bin/env python3
"""
Script to remove all debugging output from google_drive_utils.py
"""

import re

def clean_debugging_output():
    with open('google_drive_utils.py', 'r') as f:
        content = f.read()
    
    # Remove all st.success, st.info, st.warning, st.error lines that are debug messages
    debug_patterns = [
        r'\s*st\.success\(f"✅.*?\)\n',
        r'\s*st\.info\(\s*"📁.*?\)\n',
        r'\s*st\.info\(\s*"🔍.*?\)\n', 
        r'\s*st\.info\(\s*"📄.*?\)\n',
        r'\s*st\.info\(\s*"💡.*?\)\n',
        r'\s*st\.warning\("⚠️.*?\)\n',
        r'\s*st\.warning\("📂.*?\)\n',
        r'\s*st\.error\("❌.*?\)\n',
        # Multi-line st.info blocks
        r'\s*st\.info\(\s*\n\s*"📁.*?" \+\s*\n\s*"\\n"\.join\(.*?\)\s*\n\s*\)\n',
        r'\s*st\.info\(\s*\n\s*"📄.*?" \+\s*\n\s*"\\n"\.join\(.*?\)\s*\n\s*\)\n',
        # Other debug messages
        r'\s*st\.success\(f"📁.*?\)\n',
        r'\s*st\.success\(f"🎯.*?\)\n',
        r'\s*st\.warning\(f"⚠️.*?\)\n',
        r'\s*st\.info\(f"ℹ️.*?\)\n',
        r'\s*st\.error\(f"❌.*?\)\n',
    ]
    
    for pattern in debug_patterns:
        content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    # Clean up any remaining debug-specific messages
    lines = content.split('\n')
    cleaned_lines = []
    
    skip_next = False
    for i, line in enumerate(lines):
        if skip_next:
            skip_next = False
            continue
            
        # Skip debug-related lines
        if any(debug_phrase in line for debug_phrase in [
            'st.success(f"✅', 
            'st.info("📁', 
            'st.info("🔍', 
            'st.info("📄',
            'st.info("💡',
            'st.warning("⚠️',
            'st.warning("📂',
            'st.error("❌',
            'st.success(f"📁',
            'st.success(f"🎯',
            'st.info(f"ℹ️'
        ]):
            # Check if it's a multi-line statement
            if '(' in line and ')' not in line:
                # Skip until we find the closing parenthesis
                j = i + 1
                while j < len(lines) and ')' not in lines[j]:
                    j += 1
                if j < len(lines):
                    # Skip all lines including the one with closing )
                    for _ in range(j - i + 1):
                        skip_next = True
                        break
            continue
            
        cleaned_lines.append(line)
    
    cleaned_content = '\n'.join(cleaned_lines)
    
    with open('google_drive_utils.py', 'w') as f:
        f.write(cleaned_content)
    
    print("✅ Debugging output removed from google_drive_utils.py")

if __name__ == "__main__":
    clean_debugging_output()
