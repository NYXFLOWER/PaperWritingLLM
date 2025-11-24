# Developer Documentation

This document provides technical information for developers who want to contribute to or modify the Writing Assistant project.

## Table of Contents

- [Project Structure](#project-structure)
- [Development Setup](#development-setup)
- [Architecture](#architecture)
- [Adding New Features](#adding-new-features)
- [Testing](#testing)
- [Model Management](#model-management)
- [Contributing](#contributing)

## Project Structure

```
writing_llm/
├── writing_assistant/          # Main package
│   ├── __init__.py
│   ├── cli.py                 # CLI interface and command handling
│   ├── model_loader.py        # Model loading and inference
│   └── session_manager.py     # Session and conversation logging
├── prompts/                    # Mode configuration files
│   ├── nuno-writing-style.yaml
│   ├── academic.yaml
│   ├── creative.yaml
│   └── business.yaml
├── models/                     # Model storage (excluded from git)
│   ├── README.md              # Model documentation
│   ├── qwen2.5-7b-finetuned/  # Fine-tuned model (local)
│   └── qwen2.5-7b-instruct/   # Base model (local)
├── users/                      # User session logs (excluded from git)
├── config.yaml                 # Configuration file
├── main.py                     # Entry point
├── requirements.txt            # Python dependencies
├── setup.sh                    # Setup script
└── README.md                   # User documentation
```

## Development Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd writing_llm
```

### 2. Create Virtual Environment

```bash
python -m venv llm_venv
source llm_venv/bin/activate  # On Linux/Mac
# or
llm_venv\Scripts\activate      # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download Models

**Option 1: Use HuggingFace cache (automatic download)**

The model will be downloaded automatically on first use. Edit `config.yaml`:

```yaml
model:
  name: "Qwen/Qwen2.5-7B-Instruct"
```

**Option 2: Download to local directory**

```bash
python download_model.py
```

This downloads the model to `models/qwen2.5-7b-instruct/` (15GB).

**Option 3: Use your own fine-tuned model**

Place your fine-tuned model in `models/qwen2.5-7b-finetuned/` and update `config.yaml`:

```yaml
model:
  name: "/path/to/writing_llm/models/qwen2.5-7b-finetuned"
```

### 5. Test the Installation

```bash
python test_model.py
```

## Architecture

### Core Components

#### 1. Model Loader (`model_loader.py`)

**Purpose**: Handles model loading, tokenization, and text generation.

**Key Methods**:
- `load_model()`: Loads the Qwen model and tokenizer
- `generate_response(messages)`: Generates responses from conversation history
- `get_system_prompt(custom_instructions)`: Constructs system prompts
- `unload_model()`: Cleans up model from memory

**Device Handling**:
- Auto-detects CUDA availability
- Uses `float16` on GPU, `float32` on CPU
- Handles local and remote model loading

**Workarounds**:
- Uses `use_fast=False` for local model loading to avoid transformers bug
- Conditional `trust_remote_code` based on model source

#### 2. CLI (`cli.py`)

**Purpose**: Command-line interface and interactive session management.

**Key Classes**:
- `WritingAssistant`: Main application class
  - Manages model and session lifecycle
  - Handles user input and commands
  - Implements mode switching

**Command System**:

**General Commands** (work in all modes):
- `/help`: Show help panel
- `/clear`: Clear conversation history
- `/quit` or `/exit`: End session
- `/nuno`: Switch to nuno-writing-style mode
- `/mode <name>`: Switch to any mode

**Nuno-Specific Commands** (only in nuno-writing-style):
- `!outline`: Activate outline drafting mode
- `!proofread`: Activate proofreading mode

**Mode Switching Logic**:
```python
def switch_mode(self, mode_name: str):
    # Load mode config from prompts/<mode_name>.yaml
    # Update system prompt
    # Clear conversation history
    # Show activation message
```

**Submode Activation Logic**:
```python
def activate_nuno_submode(self, submode: str):
    # Validate we're in nuno-writing-style mode
    # Load submode prompt from YAML
    # Update system prompt
    # Clear history for focused work
```

#### 3. Session Manager (`session_manager.py`)

**Purpose**: Manages user sessions and conversation logging.

**Features**:
- Per-user session directories
- Dual log format (JSONL + human-readable TXT)
- Timestamp tracking
- Conversation history management

**Log Format**:

*JSONL* (`session_YYYYMMDD_HHMMSS.jsonl`):
```json
{"role": "user", "content": "...", "timestamp": "2025-01-24 14:30:22"}
{"role": "assistant", "content": "...", "timestamp": "2025-01-24 14:30:25"}
```

*TXT* (`session_YYYYMMDD_HHMMSS.txt`):
```
Session started: 2025-01-24 14:30:00
Username: alice
Mode: nuno-writing-style

[14:30:22] USER:
...

[14:30:25] ASSISTANT:
...
```

### Configuration System

**`config.yaml` Structure**:

```yaml
model:
  name: "<model-path-or-name>"
  device: "auto"  # auto, cuda, or cpu
  max_length: 4096
  temperature: 0.7
  top_p: 0.9
  repetition_penalty: 1.1

prompts:
  system_prompt: "..."
  writing_style: "..."
  working_instructions: "..."

session:
  log_directory: "users"
  auto_save: true
  max_history: 50
```

### Mode System

**Mode Files** (`prompts/*.yaml`):

Each mode has a YAML file with `custom_instructions`:

```yaml
custom_instructions: |
  You are a specialized writing assistant...
  [mode-specific instructions]
```

**Nuno Mode** (`prompts/nuno-writing-style.yaml`):

Special structure with submodes:

```yaml
custom_instructions: |
  [General Nuno style instructions]

outline: |
  [Outline drafting specific instructions]

proofread: |
  [Proofreading specific instructions]
```

## Adding New Features

### Adding a New Mode

1. **Create mode file**:

```bash
touch prompts/mymode.yaml
```

2. **Define instructions**:

```yaml
custom_instructions: |
  You are a specialized writing assistant for [purpose].

  Your task is to:
  - [Capability 1]
  - [Capability 2]
  - [Capability 3]

  Style guidelines:
  - [Guideline 1]
  - [Guideline 2]
```

3. **Test the mode**:

```bash
python main.py start -u testuser --mode mymode
```

### Adding Submodes (like !outline and !proofread)

1. **Update mode YAML** with submode sections:

```yaml
custom_instructions: |
  [General instructions]
  Available commands: !submode1, !submode2

submode1: |
  [Specific instructions for submode1]

submode2: |
  [Specific instructions for submode2]
```

2. **Add command handlers** in `cli.py`:

```python
elif user_input.lower() == '!submode1':
    self.activate_nuno_submode('submode1')
    continue
```

3. **Update help text and documentation**

### Adding New Commands

1. **Edit `cli.py`** in the command handling section:

```python
elif user_input.lower() == '/mycommand':
    # Your command logic
    console.print("[green]Command executed![/green]")
    continue
```

2. **Update help text** in `show_help()` method

3. **Document in README.md**

## Testing

### Test Scripts

**`test_model.py`**: Basic model loading and inference test
```bash
python test_model.py
```

**`test_nuno_mode.py`**: Validates nuno-writing-style.yaml structure
```bash
python test_nuno_mode.py
```

**`test_nuno_commands.py`**: Tests !outline and !proofread commands
```bash
python test_nuno_commands.py
```

**`test_interactive_commands.py`**: Tests command parsing logic
```bash
python test_interactive_commands.py
```

### Writing New Tests

Example test structure:

```python
#!/usr/bin/env python3
"""Test description"""

def test_feature():
    """Test a specific feature"""
    # Setup
    # Execute
    # Assert
    print("✓ Test passed")

if __name__ == '__main__':
    test_feature()
```

### Manual Testing Checklist

- [ ] Model loads successfully
- [ ] Basic inference works
- [ ] All modes accessible
- [ ] Commands work correctly
- [ ] Session logs created
- [ ] Mode switching clears history
- [ ] Error messages are clear
- [ ] Help text is accurate

## Model Management

### Downloading Models

**Script**: `download_model.py`

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "Qwen/Qwen2.5-7B-Instruct"
save_directory = "models/qwen2.5-7b-instruct"

# Download
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True)

# Save locally
tokenizer.save_pretrained(save_directory)
model.save_pretrained(save_directory)
```

### Saving Models Locally

**Script**: `save_model_locally.py`

Saves a model from HuggingFace cache to local directory.

### Fine-tuning Models

Fine-tuning is outside the scope of this project, but the structure supports it:

1. Fine-tune your model using standard HuggingFace methods
2. Save to `models/qwen2.5-7b-finetuned/`
3. Update `config.yaml` to point to your model
4. Test with `python test_model.py`

### Model Compatibility

**Tested with**:
- Qwen2.5-7B-Instruct (base model)
- Qwen2.5-7B fine-tuned variants

**Requirements**:
- Transformers library with Qwen support
- PyTorch with CUDA (optional, for GPU)
- 16GB+ RAM (CPU mode) or 8GB+ VRAM (GPU mode)

**Known Issues**:
- Local model loading requires `use_fast=False` workaround (transformers 4.57.2 bug)
- Some models may require `trust_remote_code=True`

## Code Style and Best Practices

### Python Style

- Follow PEP 8
- Use type hints where beneficial
- Document functions with docstrings
- Keep functions focused and small

### Error Handling

- Use try/except for external operations (model loading, file I/O)
- Provide clear error messages to users
- Log errors for debugging
- Don't crash the application unnecessarily

### User Experience

- Show progress indicators for long operations
- Provide clear feedback for all commands
- Use colors and formatting (via Rich library)
- Keep prompts concise but informative

### Git Workflow

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes
3. Test thoroughly
4. Commit with clear messages: `git commit -m "Add feature X"`
5. Push and create pull request

## Debugging

### Enable Verbose Logging

Add logging to `cli.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Issues

**Model won't load**:
- Check model path in `config.yaml`
- Verify model files exist
- Try `use_fast=False` for tokenizer
- Check CUDA availability: `torch.cuda.is_available()`

**Out of memory**:
- Set `device: "cpu"` in config
- Reduce `max_length`
- Close other applications

**Commands not working**:
- Check command spelling (case-insensitive)
- Verify you're in the correct mode
- Check command handler logic in `cli.py`

### Profiling

For performance analysis:

```python
import cProfile
cProfile.run('your_function()')
```

## Contributing

### Areas for Contribution

- **New modes**: Academic fields, creative writing genres, professional domains
- **UI improvements**: Better formatting, progress bars, color themes
- **Features**: Export conversations, search history, model selection
- **Documentation**: Examples, tutorials, translations
- **Testing**: Unit tests, integration tests, performance tests
- **Optimization**: Speed improvements, memory efficiency

### Pull Request Guidelines

1. **Description**: Clearly describe what your PR does
2. **Tests**: Include tests for new features
3. **Documentation**: Update README and relevant docs
4. **Style**: Follow existing code style
5. **Small PRs**: Keep changes focused and reviewable

### Reporting Issues

Use GitHub issues with:
- Clear title
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version, GPU)
- Error messages or logs

## License

This project is provided as-is for personal and educational use.

## Contact

For questions or discussions, open an issue on GitHub.

---

**Last Updated**: 2025-01-24
