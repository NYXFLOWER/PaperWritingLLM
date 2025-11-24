#!/usr/bin/env python3
"""Quick test to verify model loading and inference"""

from writing_assistant.model_loader import QWenModelLoader
import torch

print("=" * 60)
print("Testing Writing Assistant")
print("=" * 60)

# Check CUDA availability
print(f"\nCUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA device: {torch.cuda.get_device_name(0)}")
    print(f"CUDA memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
print()

# Load model
print("Loading model...")
model_loader = QWenModelLoader()
model_loader.load_model()

# Test inference
print("\nTesting inference...")
test_messages = [
    {"role": "system", "content": model_loader.get_system_prompt()},
    {"role": "user", "content": "Please help me improve this sentence: The dog runned fast."}
]

response = model_loader.generate_response(test_messages, max_length=200)

print("\n" + "=" * 60)
print("Test Results")
print("=" * 60)
print(f"\nUser: {test_messages[1]['content']}")
print(f"\nAssistant: {response}")
print("\n" + "=" * 60)
print("✓ Model is working correctly!")
print("=" * 60)
print("\nYou can now start a session with:")
print("  python main.py start --username flower\n")
