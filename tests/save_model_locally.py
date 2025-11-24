#!/usr/bin/env python3
"""Save the downloaded model to local models directory"""

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os

print("=" * 60)
print("Saving Model Locally")
print("=" * 60)

model_name = "Qwen/Qwen2.5-7B-Instruct"
local_path = "models/qwen2.5-7b-instruct"

print(f"\nSource: {model_name} (from HuggingFace cache)")
print(f"Destination: {local_path}")
print("\nThis will copy the model to the local directory...")
print("(This may take a few minutes)\n")

try:
    # Load tokenizer from cache
    print("Loading tokenizer from cache...")
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        trust_remote_code=True
    )

    # Load model from cache
    print("Loading model from cache...")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        dtype=torch.float16,
        device_map="cpu",  # Keep on CPU for saving
        trust_remote_code=True
    )

    # Save tokenizer locally
    print(f"\nSaving tokenizer to {local_path}...")
    tokenizer.save_pretrained(local_path)
    print("✓ Tokenizer saved")

    # Save model locally
    print(f"\nSaving model to {local_path}...")
    model.save_pretrained(local_path)
    print("✓ Model saved")

    # Check saved files
    saved_files = os.listdir(local_path)
    print(f"\n✓ Successfully saved {len(saved_files)} files to {local_path}")

    print("\n" + "=" * 60)
    print("Save Complete!")
    print("=" * 60)
    print(f"\nModel is now available at: ./{local_path}")
    print("You can delete the HuggingFace cache if needed to save space.")
    print(f"Cache location: ~/.cache/huggingface/hub/models--Qwen--Qwen2.5-7B-Instruct\n")

except Exception as e:
    print(f"\n✗ Error saving model: {str(e)}")
    exit(1)
