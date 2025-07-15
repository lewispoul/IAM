#!/usr/bin/env python3

import sys
sys.path.append('/home/lppou/IAM/IAM_GUI')
from backend import patch_molblock

# Test file content
mol_content = '''  -INDIGO-07162507472D
  6  6  0  0  0  0  0  0  0  0999 V2000
    1.7848   -3.1751    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    3.5152   -3.1746    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
M  END'''

print("Original content:")
print(repr(mol_content))
print("\nLines:")
lines = mol_content.splitlines()
for i, line in enumerate(lines):
    print(f"Line {i}: {repr(line)}")

print("\nTesting patch_molblock...")
try:
    patched = patch_molblock(mol_content)
    print("SUCCESS! Patched content:")
    print(repr(patched))
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
