# Writing Assistant with Fine-Tuned Qwen2.5-7B

A terminal-based AI writing assistant powered by a fine-tuned Qwen2.5-7B model that helps improve your writing with personalized feedback, style suggestions, and grammar corrections.

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Features

- ✨ **Interactive Chat Interface**: Natural conversation-based writing assistance
- 📝 **Multiple Writing Modes**: Academic, creative, business, and specialized Nuno style
- 🎯 **Nuno Writing Style**: Paper outline drafting and proofreading with specific commands
- 👤 **User Sessions**: Separate sessions for different users with full conversation logging
- 🎨 **Rich Terminal UI**: Beautiful interface with markdown support and syntax highlighting
- ⚙️ **Flexible Configuration**: YAML-based configuration for easy customization

## Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
  - [Basic Usage](#basic-usage)
  - [Writing Modes](#writing-modes)
  - [Interactive Commands](#interactive-commands)
  - [Nuno Mode Special Commands](#nuno-mode-special-commands)
- [Configuration](#configuration)
- [Session Management](#session-management)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [License](#license)

## Quick Start

```bash
# 1. Setup (first time only)
./setup.sh

# 2. Activate virtual environment
source llm_venv/bin/activate

# 3. Start a session
python main.py start --username YOUR_NAME

# 4. Use the assistant
You: Can you help me improve this paragraph? [paste your text]
Assistant: [provides feedback and suggestions]

You: /quit
```

## Installation

### Prerequisites

- Python 3.8 or higher
- 16GB+ RAM (for CPU mode) or 8GB+ VRAM (for GPU mode)
- CUDA-capable GPU (optional, for faster inference)

### Setup Steps

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd writing_llm
```

#### 2. Run Setup Script

```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Create a Python virtual environment (`llm_venv`)
- Install all required dependencies
- Configure the system

#### 3. Activate Virtual Environment

```bash
source llm_venv/bin/activate  # On Linux/Mac
# or
llm_venv\Scripts\activate  # On Windows
```

#### 4. Configure Model

Edit `config.yaml` to specify your model:

```yaml
model:
  # Option 1: Use HuggingFace cache (auto-download on first use)
  name: "Qwen/Qwen2.5-7B-Instruct"

  # Option 2: Use local fine-tuned model
  # name: "/path/to/models/qwen2.5-7b-finetuned"
```

**First-time model download**: The model (~15GB) will be downloaded automatically on first use if using HuggingFace cache.

## Usage

### Basic Usage

Start a new session:

```bash
python main.py start --username YOUR_NAME
```

With a specific writing mode:

```bash
python main.py start --username YOUR_NAME --mode nuno-writing-style
```

With custom instructions:

```bash
python main.py start --username YOUR_NAME --instructions "Focus on academic writing"
```

### Writing Modes

The assistant includes several built-in modes for different writing tasks:

#### Nuno Writing Style

**Command**: `--mode nuno-writing-style`

Specialized for academic paper writing with two core functions:

1. **Paper Outline Draft** (`!outline` command)
   - Provide project details, research context, section order
   - Receive comprehensive outline with detailed section descriptions
   - Includes purpose, key topics, data/examples needed, flow, transitions

2. **Writing Improvement** (`!proofread` command)
   - Corrects grammar and punctuation errors
   - Rephrases for clarity while preserving meaning
   - Applies Nuno's writing style principles:
     * Clear, direct language
     * Active voice preference
     * Concise expressions
     * Logical structure
     * Academic formality without jargon
     * Evidence-based reasoning

**Example**:
```bash
python main.py start --username john --mode nuno-writing-style
```

#### Other Modes

- **Academic** (`--mode academic`): Formal scholarly writing
- **Creative** (`--mode creative`): Narrative and creative writing
- **Business** (`--mode business`): Professional business communication

### Interactive Commands

During a session, use these commands:

#### General Commands

| Command | Description |
|---------|-------------|
| `/help` | Show detailed help and tips |
| `/clear` | Clear conversation history |
| `/nuno` | Switch to Nuno writing style mode |
| `/mode <name>` | Switch to any mode (academic, creative, business) |
| `/quit` or `/exit` | End session and save |

**Example**:
```
You: /nuno
✓ Switched to mode: nuno-writing-style
Previous conversation history cleared (0 messages)

Nuno Writing Style Mode Activated
Available commands:
  • !outline - Paper outline drafting mode
  • !proofread - Writing improvement mode
  • General writing help and questions
```

### Nuno Mode Special Commands

These commands only work in `nuno-writing-style` mode:

#### !outline - Paper Outline Drafting

```
You: !outline
✓ Activated: OUTLINE MODE
📋 Paper Outline Drafting
Provide your project details, research question, and desired sections.

You: I'm writing a paper on mass spectrometry-based proteomics...
     [provide project details and desired sections]Assistant: [Creates comprehensive outline with sections and subsections]
```

#### !proofread - Writing Improvement

```
You: !proofread
✓ Activated: PROOFREAD MODE
✏️  Writing Improvement & Proofreading
Paste your text and I'll improve grammar, style, and clarity.

You: [Paste your text]
     "The data was analyzed using machine learning algorithms..."

Assistant: [Provides improved version with corrections and explanations]
```

**Important**: These commands only work after entering Nuno mode with `/nuno` or starting with `--mode nuno-writing-style`.

## Configuration

### Model Configuration

Edit `config.yaml` to customize the model and behavior:

```yaml
model:
  name: "Qwen/Qwen2.5-7B-Instruct"  # Model name or path
  device: "auto"                     # auto, cuda, or cpu
  max_length: 4096                   # Max response length
  temperature: 0.7                   # Generation temperature (0.0-1.0)
  top_p: 0.9                        # Nucleus sampling
  repetition_penalty: 1.1           # Penalty for repetition

prompts:
  system_prompt: "..."              # Base system prompt
  writing_style: "..."              # Default writing style
  working_instructions: "..."       # Working guidelines

session:
  log_directory: "users"            # Where to store session logs
  auto_save: true                   # Auto-save conversations
  max_history: 50                   # Max messages in memory
```

### Downloading the Fine-Tuned Model

The project supports a fine-tuned Qwen2.5-7B model optimized for writing assistance.

**Download Link**: `MODEL_DOWNLOAD_LINK_HERE` *(will be provided upon release)*

**Installation Steps**:

```bash
# Create models directory if it doesn't exist
mkdir -p models

# Download the fine-tuned model (replace URL with actual link)
wget <MODEL_DOWNLOAD_URL> -O models/qwen2.5-7b-finetuned.tar.gz

# Or using curl
curl -L <MODEL_DOWNLOAD_URL> -o models/qwen2.5-7b-finetuned.tar.gz

# Extract the model
cd models
tar -xzf qwen2.5-7b-finetuned.tar.gz
cd ..
```

**Update config.yaml** to use the fine-tuned model:

```yaml
model:
  name: "./models/qwen2.5-7b-finetuned"
```

**Note**: The fine-tuned model is approximately 15GB. Ensure you have sufficient disk space.

### Model Options

1. **Fine-tuned model (recommended)**: Download from provided link above
   - Optimized for writing assistance tasks
   - Best performance for this application

2. **Base model from HuggingFace**: Auto-download on first use
   - Use `"Qwen/Qwen2.5-7B-Instruct"` in config
   - Good baseline performance

3. **Custom fine-tuned model**: Use your own model
   - Place in `models/` directory
   - Update config with path

## Session Management

### Viewing Session History

List all sessions for a user:

```bash
python main.py list-sessions --username YOUR_NAME
```

View a specific session:

```bash
python main.py view-session --username YOUR_NAME --session-id 20250124_143022
```

### Session Logs

Each session creates two files in `users/YOUR_NAME/`:

1. **JSONL Log** (`session_YYYYMMDD_HHMMSS.jsonl`): Structured data
2. **Text Summary** (`session_YYYYMMDD_HHMMSS.txt`): Human-readable conversation

Example: `users/john/session_20250124_143022.jsonl`

## Examples

### Example 1: Basic Writing Improvement

```bash
python main.py start -u alice

You: Can you improve this sentence: "The dog was running very fast in the park."
Assistant: Here are some improved versions:
  1. "The dog sprinted through the park."
  2. "The dog raced swiftly across the park."
  ...

You: /quit
```

### Example 2: Academic Paper Outlining

```bash
python main.py start -u bob --mode nuno-writing-style

You: !outline

You: I'm writing a paper on machine learning for proteomics.
     Research question: How can we improve peptide identification?
     Sections: Introduction, Methods, Results, Discussion, Conclusion
Assistant: [Provides comprehensive outline]

You: /quit
```

### Example 3: Mode Switching

```bash
python main.py start -u carol

You: /mode academic
You: Improve: "The study was good"
Assistant: [improves with academic tone]

You: /nuno
You: \!proofread
You: [Paste text to improve]
Assistant: [Improves following Nuno style]
```

## Troubleshooting

### Model Issues

**Out of Memory**:
- Set `device: "cpu"` in config.yaml
- Reduce `max_length` value
- Close other applications

**Model Won't Load**:
- Check model path in config.yaml
- Verify model files exist
- Try using HuggingFace cache instead

### Command Issues

**Commands Not Working**:
- Check spelling (commands are case-insensitive)
- Ensure you're in the correct mode for mode-specific commands
- Use `/help` to see available commands

**Nuno Commands (\!outline, \!proofread) Not Working**:
- These only work in nuno-writing-style mode
- Use `/nuno` first to enter the mode

## Development

For developers who want to contribute or modify the project, see [README_DEV.md](README_DEV.md) for:

- Project structure and architecture
- Development setup
- Adding new modes and features
- Testing guidelines
- Code style and best practices

## Requirements

- Python 3.8+
- CUDA-capable GPU (recommended) or CPU
- 16GB+ RAM for model loading
- ~15GB disk space for model

## License

This project is provided as-is for personal and educational use.

## Contributing

Contributions are welcome\! Please see [README_DEV.md](README_DEV.md) for development guidelines.

## Acknowledgments

- Built with [Qwen2.5-7B](https://huggingface.co/Qwen) by Alibaba Cloud
- Uses [Transformers](https://github.com/huggingface/transformers) library
- Terminal UI powered by [Rich](https://github.com/Textualize/rich)

---

**Last Updated**: 2025-01-24
