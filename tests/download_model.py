#!/usr/bin/env python3
"""Download Qwen2.5-7B-Instruct model"""

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

print("=" * 60)
print("Downloading Qwen2.5-7B-Instruct Model")
print("=" * 60)
print("\nThis may take a while depending on your internet connection...")
print("Model size: ~15GB\n")

model_name = "Qwen/Qwen2.5-7B-Instruct"

try:
    print(f"Downloading tokenizer from {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        trust_remote_code=True
    )
    print("✓ Tokenizer downloaded successfully\n")

    print(f"Downloading model from {model_name}...")
    print("(This will take several minutes...)\n")

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True
    )
    print("\n✓ Model downloaded successfully\n")

    print("=" * 60)
    print("Download Complete!")
    print("=" * 60)
    print(f"\nModel cached to: {model.config._name_or_path}")
    print("You can now use the writing assistant with:")
    print("  python main.py start --username YOUR_NAME\n")

except Exception as e:
    print(f"\n✗ Error downloading model: {str(e)}")
    print("\nPlease check:")
    print("  1. Internet connection")
    print("  2. Sufficient disk space (~20GB free)")
    print("  3. HuggingFace access\n")
    exit(1)
