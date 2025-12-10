import re
from pathlib import Path

file_path = Path("/data_hdd_16t/vuongchu/nxGREG/ctc-data-en/simple/yuusyou-kihon/functions/register-contract/function-overview-en.md")

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Try different patterns
patterns = [
    r'###\s+4\.2\.\s+Database Tables Used(.*?)(?=\n#{1,3}\s+|\*\*Notes:\*\*|\Z)',
    r'### 4\.2\. Database Tables Used(.*?)(?=\*\*Notes:\*\*|\Z)',
    r'4\.2\. Database Tables Used(.*?)(?=\*\*Notes:\*\*)',
]

for i, pattern in enumerate(patterns):
    print(f"\n=== Pattern {i+1} ===")
    print(f"Pattern: {pattern}")
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    if match:
        print("MATCHED!")
        print(f"Content length: {len(match.group(1))}")
        print(f"First 200 chars:\n{match.group(1)[:200]}")
    else:
        print("NO MATCH")

# Also check if the section exists at all
if "4.2. Database Tables Used" in content:
    print("\n=== Section exists in file ===")
    idx = content.index("4.2. Database Tables Used")
    print(f"Found at position: {idx}")
    print(f"Context:\n{content[idx:idx+500]}")
