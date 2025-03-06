# Rich Ollama Chat

A beautiful terminal-based chat interface for Ollama using Rich formatting.

## Features

- 🎨 Beautiful terminal UI with syntax highlighting
- 📝 Markdown support
- 💻 Code block formatting with line numbers
- ⏱️ Response time tracking
- 🎯 Custom theme support
- 🔄 Live streaming responses
- 📐 Adaptive width based on terminal size
- 💾 Chat history management
- ⚙️ Configurable performance settings
- 🖥️ CPU/GPU configuration options

## Prerequisites

- Python 3.7 or higher
- Ollama installed and running on your system

## Installation

You can install this package in several ways:

### 1. From PyPI (recommended)
```bash
pip install rich-ollama-chat
```

### 2. From GitHub
```bash
pip install git+https://github.com/bhumukul-raj/rich-ollama-chat.git
```

### 3. From Source
```bash
git clone https://github.com/bhumukul-raj/rich-ollama-chat.git
cd rich-ollama-chat
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

## Usage

### Basic Usage
```bash
# Start a new chat session
rich-ollama-chat chat

# View configuration
rich-ollama-chat config

# List chat history
rich-ollama-chat history list

# Show a specific conversation
rich-ollama-chat history show <conversation_id>

# Delete a conversation
rich-ollama-chat history delete <conversation_id>
```

### Configuration Options

The chat interface can be configured through the config file (`~/.config/rich-ollama-chat/config.json`):

```json
{
    "model": "mistral",           // Default model to use
    "code_theme": "dracula",      // Theme for code blocks
    "max_context_length": 4096,   // Maximum context length
    "temperature": 0.7,          // Response temperature
    "num_ctx": 4096,            // Context window size
    "num_thread": 8,            // Number of CPU threads
    "use_gpu": false,           // Whether to use GPU
    "num_gpu": 0,              // Number of GPUs (0 for CPU only)
    "repeat_penalty": 1.1,     // Penalty for repeating tokens
    "top_k": 40,              // Top K sampling
    "top_p": 0.9              // Top P sampling
}
```

You can modify these settings using the config command:
```bash
# Change model
rich-ollama-chat config --model llama2

# Change theme
rich-ollama-chat config --theme monokai

# Enable GPU
rich-ollama-chat config --gpu true
```

### Display Features

1. **Adaptive Width**:
   - In full-screen mode: Uses 80% of terminal width for optimal readability
   - In windowed mode: Uses full available width
   - Automatically adjusts when terminal is resized

2. **Code Formatting**:
   - Syntax highlighting for code blocks
   - Line numbers for better reference
   - Multiple theme options

3. **Response Streaming**:
   - Real-time display of responses
   - Progress indicator
   - Response time tracking

### Available Code Themes

- `dracula` (default)
- `monokai`
- `github-dark`
- `solarized-dark`
- `one-dark`
- `nord`
- `gruvbox-dark`
- `vs-dark`
- `zenburn`

### Python API

You can also use the package programmatically:

```python
from rich_ollama_chat import stream_chat_with_formatting, interactive_chat

# Start interactive chat
interactive_chat()

# Or use streaming chat directly
messages = [{"role": "user", "content": "Hello!"}]
response = stream_chat_with_formatting(
    messages,
    model="mistral",
    code_theme="dracula"
)
```

## Performance Optimization

### CPU Configuration
By default, the chat uses CPU-only mode with 8 threads. You can adjust thread count in config:
```bash
rich-ollama-chat config --threads 16
```

### GPU Support
To enable GPU acceleration:
```bash
rich-ollama-chat config --gpu true --num-gpu 1
```

## Development

1. Clone and setup:
```bash
git clone https://github.com/bhumukul-raj/rich-ollama-chat.git
cd rich-ollama-chat
python -m venv venv
source venv/bin/activate
pip install -e ".[test]"
```

2. Run tests:
```bash
pytest
```

3. Format code:
```bash
black rich_ollama_chat
isort rich_ollama_chat
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 