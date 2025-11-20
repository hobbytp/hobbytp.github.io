import re
import os

file_path = r"d:\Hobby\github\hobbytp.github.io\books\ai_native\0.1-什么是AI原生.md"

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

parts = content.split("## 参考文献")
body = parts[0]
# The rest is references. If "## 参考文献" appears multiple times, this might be an issue, but unlikely.
# We take the last part as references if we split by it? No, split returns list.
# Usually references are at the end.
# Let's assume the last section is references.
# But wait, split will return 2 parts if it appears once.
# If it appears multiple times, we might have issues.
# Let's assume it appears once.

ref_part = parts[-1]
# If there were multiple splits, we should join the previous ones back to body?
# Actually, let's find the index of the last "## 参考文献"
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
