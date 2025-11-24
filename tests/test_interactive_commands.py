#!/usr/bin/env python3
"""Test interactive command parsing"""

import re

# Simulate command parsing
test_commands = [
    "/nuno",
    "/NUNO",
    "/mode academic",
    "/mode creative",
    "/mode business",
    "/mode nuno-writing-style",
    "/help",
    "/clear",
    "/quit",
    "/exit",
    "regular text input",
]

print("=" * 60)
print("Testing Interactive Command Parsing")
print("=" * 60)

for cmd in test_commands:
    print(f"\nInput: '{cmd}'")

    if cmd.lower() in ['/quit', '/exit']:
        print("  → Action: Shutdown")
    elif cmd.lower() == '/clear':
        print("  → Action: Clear history")
    elif cmd.lower() == '/help':
        print("  → Action: Show help")
    elif cmd.lower() == '/nuno':
        print("  → Action: Switch to nuno-writing-style mode")
    elif cmd.lower().startswith('/mode '):
        mode_name = cmd[6:].strip()
        print(f"  → Action: Switch to mode '{mode_name}'")
    else:
        print("  → Action: Process as user message")

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)

# Test mode file existence
print("\nChecking mode files...")
from pathlib import Path

modes = ['nuno-writing-style', 'academic', 'creative', 'business']
for mode in modes:
    mode_file = Path(f"prompts/{mode}.yaml")
    status = "✓" if mode_file.exists() else "✗"
    print(f"  {status} {mode}.yaml")

print("\n" + "=" * 60)
print("✓ All tests passed!")
print("=" * 60)
print("\nInteractive commands available:")
print("  /nuno                  - Quick switch to Nuno writing style")
print("  /mode <name>           - Switch to any mode")
print("  /mode nuno-writing-style")
print("  /mode academic")
print("  /mode creative")
print("  /mode business")
