#!/usr/bin/env python3
"""Fix the indentation issues in google_drive_utils.py"""

# Read the file
with open('google_drive_utils.py', 'r') as f:
    lines = f.readlines()

# Fix specific problematic lines
for i, line in enumerate(lines):
    # Comment out the debugging messages but preserve indentation
    if 'st.warning("📂 **No folders accessible to Service Account**")' in line:
        lines[i] = line.replace('st.warning("📂 **No folders accessible to Service Account**")', '# st.warning("📂 **No folders accessible to Service Account**")')
    elif 'st.error("❌ **No items accessible to Service Account' in line:
        lines[i] = line.replace('st.error("❌ **No items accessible to Service Account', '# st.error("❌ **No items accessible to Service Account')
    elif 'st.info("💡 **Creating virtual' in line:
        lines[i] = line.replace('st.info("💡 **Creating virtual', '# st.info("💡 **Creating virtual')
    elif 'st.success(f"✅ **Found' in line:
        lines[i] = line.replace('st.success(f"✅ **Found', '# st.success(f"✅ **Found')
    elif line.strip().startswith('st.info(') and 'Accessible folders:' in line:
        lines[i] = line.replace('st.info(', '# st.info(')
    elif line.strip().startswith('st.info(') and 'Accessible files:' in line:
        lines[i] = line.replace('st.info(', '# st.info(')

# Add pass statements where needed
fixed_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    fixed_lines.append(line)
    
    # Check for empty else blocks
    if line.strip().endswith('else:'):
        # Look ahead to see if the next non-comment line is properly indented
        j = i + 1
        found_content = False
        while j < len(lines) and (lines[j].strip().startswith('#') or lines[j].strip() == ''):
            if lines[j].strip().startswith('#'):
                fixed_lines.append(lines[j])
                j += 1
            else:
                fixed_lines.append(lines[j])
                j += 1
        
        # Check if we need to add a pass statement
        if j < len(lines):
            next_line = lines[j]
            current_indent = len(line) - len(line.lstrip())
            next_indent = len(next_line) - len(next_line.lstrip())
            
            # If the next line is not properly indented for the else block, add pass
            if next_indent <= current_indent + 4:
                fixed_lines.append(' ' * (current_indent + 8) + 'pass\n')
        else:
            # End of file, add pass
            fixed_lines.append(' ' * (len(line) - len(line.lstrip()) + 8) + 'pass\n')
        
        i = j - 1
    
    i += 1

# Write the fixed file
with open('google_drive_utils.py', 'w') as f:
    f.writelines(fixed_lines)

print("✅ Fixed indentation issues in google_drive_utils.py")
