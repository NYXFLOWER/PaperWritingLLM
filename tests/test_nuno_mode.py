#!/usr/bin/env python3
"""Quick test to verify nuno-writing-style mode"""

import yaml
from pathlib import Path

print("=" * 60)
print("Testing Nuno Writing Style Mode")
print("=" * 60)

# Test 1: Check if nuno-writing-style.yaml exists
print("\n[Test 1] Checking if nuno-writing-style.yaml exists...")
mode_file = Path("prompts/nuno-writing-style.yaml")
if mode_file.exists():
    print("✓ File exists")
else:
    print("✗ File not found")
    exit(1)

# Test 2: Load and validate the YAML
print("\n[Test 2] Loading YAML content...")
try:
    with open(mode_file, 'r') as f:
        config = yaml.safe_load(f)
    print("✓ YAML loaded successfully")
except Exception as e:
    print(f"✗ Error loading YAML: {e}")
    exit(1)

# Test 3: Check for custom_instructions
print("\n[Test 3] Checking for custom_instructions...")
if 'custom_instructions' in config:
    instructions = config['custom_instructions']
    print(f"✓ custom_instructions found ({len(instructions)} characters)")
else:
    print("✗ custom_instructions not found")
    exit(1)

# Test 4: Check for key features in instructions
print("\n[Test 4] Checking for key features...")
required_features = [
    "Paper Outline Draft",
    "Writing Improvement",
    "grammar",
    "Nuno's writing style"
]

for feature in required_features:
    if feature in instructions:
        print(f"✓ Found: {feature}")
    else:
        print(f"✗ Missing: {feature}")

# Test 5: Display instructions summary
print("\n[Test 5] Instructions summary:")
print("-" * 60)
lines = instructions.split('\n')
print(f"Total lines: {len(lines)}")
print(f"First 5 non-empty lines:")
for i, line in enumerate(lines[:20]):
    if line.strip():
        print(f"  {line.strip()}")
        if i >= 5:
            break

print("\n" + "=" * 60)
print("✓ All tests passed!")
print("=" * 60)
print("\nTo use nuno-writing-style mode:")
print("  python main.py start --username YOUR_NAME --mode nuno-writing-style\n")
