# Rich Ollama Chat

A beautiful terminal-based chat interface for Ollama using Rich formatting.

## Features

- 🎨 Beautiful terminal UI with syntax highlighting
- 📝 Markdown support
- 💻 Code block formatting with line numbers
- ⏱️ Response time tracking
- 🎯 Custom theme support
- 🔄 Live streaming responses

## Prerequisites

- Python 3.7 or higher
- Ollama installed and running on your system

## Installation

You can install this package in several ways:

### 1. From PyPI (recommended)
```bash
pip install rich-ollama-chat
```

Note: This method will work only after the package is published to PyPI. If the package is not yet published, use the GitHub installation method below.

### 2. From GitHub
You can install the latest version directly from GitHub using pip:

```bash
# Using HTTPS
pip install git+https://github.com/bhumukul-raj/rich-ollama-chat.git

# Using SSH (if you have SSH access configured)
pip install git+ssh://git@github.com/bhumukul-raj/rich-ollama-chat.git
```

Note: When installing from GitHub, pip will automatically:
- Clone the repository
- Build the package
- Install all required dependencies
- Install the built package
No manual build steps are required for users installing from GitHub.

### 3. From Source
Clone the repository and install in development mode:
```bash
git clone https://github.com/bhumukul-raj/rich-ollama-chat.git
cd rich-ollama-chat
pip install -e .
```

### 4. From Distribution Files
Download the wheel or tarball from the releases and install:
```bash
# For wheel file
pip install rich_ollama_chat-0.1.0-py3-none-any.whl

# For source distribution
pip install rich_ollama_chat-0.1.0.tar.gz
```

## Usage

### 1. Command Line Interface
After installation, you can start the chat interface by running:
```bash
rich-ollama-chat
```

### 2. Python API
You can also use it in your Python code:
```python
from rich_ollama_chat import stream_chat_with_formatting

messages = [{"role": "user", "content": "Hello, how are you?"}]
response = stream_chat_with_formatting(messages, model="mistral")
```

## Configuration

The chat interface uses the following default settings:
- Model: mistral
- Code theme: dracula
- Custom theme for different message types

## Building the Package

If you want to build the package yourself:

1. Install build tools:
```bash
pip install build twine
```

2. Build the package:
```bash
python -m build
```

This will create two files in the `dist` directory:
- `rich_ollama_chat-0.1.0-py3-none-any.whl` (Wheel distribution)
- `rich_ollama_chat-0.1.0.tar.gz` (Source distribution)

3. To install the locally built package:
```bash
pip install dist/rich_ollama_chat-0.1.0-py3-none-any.whl
```

## Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install in development mode:
```bash
pip install -e .
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Publishing to PyPI

To make this package available for installation via `pip install rich-ollama-chat`, you need to publish it to PyPI:

1. Create an account on PyPI (https://pypi.org)

2. Install build tools:
```bash
pip install build twine
```

3. Build the distribution:
```bash
python -m build
```

4. Upload to PyPI:
```bash
python -m twine upload dist/*
```

You'll need to enter your PyPI username and password when uploading. 