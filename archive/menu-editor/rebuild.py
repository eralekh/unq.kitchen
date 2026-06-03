"""
UNQ Kitchen Package Editor — Rebuild Script
============================================
Run from the unq-kitchen-site/ folder:
    python3 menu-editor/rebuild.py

Re-embeds the current data.json and template.html into index.html
so the editor works correctly when opened as a local file.
"""

import json, re, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))

def read(name):
    with open(os.path.join(BASE, name), encoding='utf-8') as f:
        return f.read()

def write(name, content):
    with open(os.path.join(BASE, name), 'w', encoding='utf-8') as f:
        f.write(content)

print('UNQ Kitchen Package Editor — Rebuild')
print('=====================================')

# 1. Read source files
data_str = read('data.json')
tmpl_str = read('template.html')
editor   = read('index.html')

# Validate JSON
try:
    json.loads(data_str)
    print(f'✓  data.json valid ({len(data_str):,} bytes)')
except json.JSONDecodeError as e:
    print(f'✗  data.json is invalid JSON: {e}')
    sys.exit(1)

# Check template placeholders
if '{{PAGES}}' not in tmpl_str:
    print('✗  template.html is missing {{PAGES}} placeholder')
    sys.exit(1)
if '{{VENUE_PAGE}}' not in tmpl_str:
    print('✗  template.html is missing {{VENUE_PAGE}} placeholder')
    sys.exit(1)
print(f'✓  template.html valid ({len(tmpl_str):,} bytes)')

# 2. JSON-encode as JS strings
data_js = json.dumps(data_str)
tmpl_js  = json.dumps(tmpl_str)

# 3. Replace the embedded constants in index.html
pattern = r'(const _EMBEDDED_DATA\s*=\s*)(?:"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\');'
if not re.search(pattern, editor):
    print('✗  Could not find _EMBEDDED_DATA constant in index.html')
    sys.exit(1)
editor = re.sub(pattern, lambda m: m.group(1) + data_js + ';', editor)

pattern2 = r'(const _EMBEDDED_TEMPLATE\s*=\s*)(?:"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\');'
if not re.search(pattern2, editor):
    print('✗  Could not find _EMBEDDED_TEMPLATE constant in index.html')
    sys.exit(1)
editor = re.sub(pattern2, lambda m: m.group(1) + tmpl_js + ';', editor)

# 4. Write updated index.html
write('index.html', editor)
print(f'✓  index.html updated ({len(editor):,} bytes)')
print()
print('Done. Open menu-editor/index.html in your browser.')
