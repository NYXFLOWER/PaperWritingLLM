#!/usr/bin/env python3
"""Test script for Nuno mode commands (!outline and !proofread)"""

import yaml
from pathlib import Path

def test_nuno_yaml_structure():
    """Test that nuno-writing-style.yaml has the correct structure"""
    yaml_file = Path("prompts/nuno-writing-style.yaml")

    print("Testing nuno-writing-style.yaml structure...")

    if not yaml_file.exists():
        print(f"❌ File not found: {yaml_file}")
        return False

    with open(yaml_file, 'r') as f:
        config = yaml.safe_load(f)

    # Check required fields
    required_fields = ['custom_instructions', 'outline', 'proofread']
    missing_fields = [field for field in required_fields if field not in config]

    if missing_fields:
        print(f"❌ Missing fields: {missing_fields}")
        return False

    print(f"✓ Found all required fields: {required_fields}")

    # Check that each field has content
    for field in required_fields:
        content = config[field]
        if not content or not content.strip():
            print(f"❌ Field '{field}' is empty")
            return False
        print(f"✓ Field '{field}' has {len(content)} characters")

    # Check outline prompt content
    outline_content = config['outline'].lower()
    if 'outline' not in outline_content or 'paper' not in outline_content:
        print("⚠ Warning: 'outline' field might not have proper outline instructions")
    else:
        print("✓ Outline prompt looks good")

    # Check proofread prompt content
    proofread_content = config['proofread'].lower()
    if 'proofread' not in proofread_content and 'grammar' not in proofread_content:
        print("⚠ Warning: 'proofread' field might not have proper proofread instructions")
    else:
        print("✓ Proofread prompt looks good")

    print("\n✅ All tests passed!")
    return True

def show_command_examples():
    """Show example usage of the commands"""
    print("\n" + "="*60)
    print("EXAMPLE USAGE")
    print("="*60)

    print("\n1. Start with Nuno mode:")
    print("   python main.py start --username flower --mode nuno-writing-style")

    print("\n2. Use !outline command:")
    print("   You: !outline")
    print("   System: [Activates OUTLINE MODE]")
    print("   You: I need to write a paper on proteomics...")

    print("\n3. Use !proofread command:")
    print("   You: !proofread")
    print("   System: [Activates PROOFREAD MODE]")
    print("   You: [Paste your text to improve]")

    print("\n4. Switch between modes:")
    print("   You: !outline   → Outline mode")
    print("   You: !proofread → Proofread mode")
    print("   You: /nuno      → Reset to general Nuno mode")

    print("\n5. Commands only work in nuno-writing-style mode!")
    print("   - If you're in academic/creative/business mode")
    print("   - Use /nuno first to switch to nuno-writing-style")
    print("   - Then use !outline or !proofread")

if __name__ == '__main__':
    success = test_nuno_yaml_structure()

    if success:
        show_command_examples()
    else:
        print("\n❌ Tests failed! Please check the YAML file structure.")
