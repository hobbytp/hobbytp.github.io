import re
import os
import argparse

parser = argparse.ArgumentParser(description="Fix markdown references in a file.")
parser.add_argument("file_path", help="Path to the markdown file to process.")
args = parser.parse_args()
file_path = args.file_path

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    exit(1)

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Split into body and references
# Assuming "## 参考文献" is the separator
if "## 参考文献" not in content:
    print("References section not found.")
    exit(1)

# We find the index of the last "## 参考文献"
last_ref_index = content.rfind("## 参考文献")
body = content[:last_ref_index]
ref_part = content[last_ref_index + len("## 参考文献"):]

# Parse references
# Skip the header line (already skipped by split/slicing)
ref_lines = ref_part.strip().split('\n')
ref_lines = [line.strip() for line in ref_lines if line.strip()]

# Create a map of index to reference line
refs = {}
for i, line in enumerate(ref_lines):
    refs[i+1] = line

# Reconstruct references section
new_references = "## 参考文献\n\n"
for i in range(1, len(refs) + 1):
    new_references += f"[^{i}]: {refs[i]}\n"

# Replace superscripts in body
superscript_map = {
    '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
    '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9'
}

def replace_superscript(match):
    s = match.group(0)
    num_str = "".join(superscript_map.get(c, c) for c in s)
    return f"[^{num_str}]"

# Regex to match one or more superscript digits
superscript_pattern = r"[" + "".join(superscript_map.keys()) + r"]+"

new_body = re.sub(superscript_pattern, replace_superscript, body)

# Combine
new_content = new_body + new_references

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"Processed {len(refs)} references.")
