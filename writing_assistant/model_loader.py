"""QWen3-8b Model Loader"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import Optional, Dict, Any
import yaml


class QWenModelLoader:
    """Load and manage QWen3-8b model for writing assistance"""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the model loader with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.model_config = self.config['model']
        self.prompts_config = self.config['prompts']
        self.model = None
        self.tokenizer = None
        self.device = None

    def load_model(self) -> None:
        """Load the QWen model and tokenizer"""
        print(f"Loading model: {self.model_config['name']}...")

        model_path = self.model_config['name']

        # Determine if this is a local path or HuggingFace model name
        is_local = ('/' in model_path and not model_path.startswith('http'))

        # Load tokenizer
        tokenizer_kwargs = {'use_fast': False}  # Workaround for local loading bug
        if not is_local or 'Qwen' in model_path or 'qwen' in model_path.lower():
            tokenizer_kwargs['trust_remote_code'] = True

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            **tokenizer_kwargs
        )

        # Determine device
        if self.model_config['device'] == 'auto':
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = self.model_config['device']

        # Load model
        model_kwargs = {
            'dtype': torch.float16 if self.device == 'cuda' else torch.float32,
            'device_map': 'auto' if self.device == 'cuda' else None,
        }

        if not is_local or 'Qwen' in model_path:
            model_kwargs['trust_remote_code'] = True

        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            **model_kwargs
        )

        if self.device == 'cpu':
            self.model = self.model.to(self.device)

        print(f"Model loaded successfully on {self.device}")

    def get_system_prompt(self, custom_instructions: Optional[str] = None) -> str:
        """Get the system prompt with optional custom instructions"""
        base_prompt = self.prompts_config['system_prompt']
        style = self.prompts_config['writing_style']
        instructions = self.prompts_config['working_instructions']

        system_prompt = f"{base_prompt}\n\n## Writing Style\n{style}\n\n## Working Instructions\n{instructions}"

        if custom_instructions:
            system_prompt += f"\n\n## Additional Instructions\n{custom_instructions}"

        return system_prompt

    def generate_response(
        self,
        messages: list,
        max_length: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None
    ) -> str:
        """Generate a response from the model"""
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        # Use config defaults if not specified
        max_length = max_length or self.model_config['max_length']
        temperature = temperature or self.model_config['temperature']
        top_p = top_p or self.model_config['top_p']

        # Apply chat template
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        # Tokenize input
        inputs = self.tokenizer([text], return_tensors="pt").to(self.device)

        # Generate response
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_length,
                temperature=temperature,
                top_p=top_p,
                repetition_penalty=self.model_config.get('repetition_penalty', 1.1),
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )

        # Decode response
        response = self.tokenizer.decode(
            outputs[0][inputs['input_ids'].shape[1]:],
            skip_special_tokens=True
        )

        return response.strip()

    def unload_model(self) -> None:
        """Unload the model to free memory"""
        if self.model is not None:
            del self.model
            self.model = None
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        print("Model unloaded successfully")
