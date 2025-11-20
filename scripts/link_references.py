
import re

file_path = r"d:\Hobby\github\hobbytp.github.io\books\ai_native\0.1-什么是AI原生.md"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Split content into body and references
parts = content.split("## 参考文献")
if len(parts) != 2:
    print("Error: Could not find '## 参考文献' section or found multiple.")
    exit(1)

body = parts[0]
references_raw = parts[1].strip().split('\n')

# Process references
references = []
ref_map = {}
current_index = 1

formatted_refs = []

for line in references_raw:
    line = line.strip()
    if not line:
        continue
    
    # Create anchor and formatted line
    anchor = f"ref-{current_index}"
    # Check if line already has a number (unlikely based on inspection but good to be safe)
    # The lines look like "Title - Source, Date, Link"
    
    formatted_line = f'{current_index}. <a id="{anchor}"></a>{line}'
    formatted_refs.append(formatted_line)
    current_index += 1

# Process body to replace superscripts with links
# Map of superscript chars to digits
super_map = {
    '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
    '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9'
}

def replace_superscript(match):
    sup_str = match.group(0)
    normal_str = "".join(super_map.get(c, c) for c in sup_str)
    try:
        ref_num = int(normal_str)
        return f'[{sup_str}](#ref-{ref_num})'
    except ValueError:
        return sup_str

# Regex to find superscript numbers (one or more)
# We need to be careful not to match other things, but the superscripts are distinct.
sup_regex = re.compile(r'[⁰¹²³⁴⁵⁶⁷⁸⁹]+')

new_body = sup_regex.sub(replace_superscript, body)

# Reconstruct file
new_content = new_body + "## 参考文献\n\n" + "\n".join(formatted_refs) + "\n"

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Successfully updated references and links.")
