"""Configuration management for Rich Ollama Chat.

This module handles loading, saving, and updating configuration settings.
Configuration is stored in JSON format at ~/.config/rich-ollama-chat/config.json.

Default configuration includes:
- Model selection
- Code theme settings
- Performance parameters (CPU/GPU)
- Response generation parameters
- Context window settings
"""

from pathlib import Path
import json
import os

# Default configuration with detailed parameter descriptions
DEFAULT_CONFIG = {
    # Model and display settings
    "model": "mistral",           # Default language model to use
    "code_theme": "dracula",      # Theme for code block syntax highlighting
    
    # Context and response settings
    "max_context_length": 4096,   # Maximum number of tokens in context window
    "temperature": 0.7,           # Randomness in response generation (0.0-1.0)
    "num_ctx": 4096,             # Context window size for token processing
    
    # Performance settings
    "num_thread": 8,             # Number of CPU threads for parallel processing
    "use_gpu": False,            # Whether to use GPU acceleration
    "num_gpu": 0,               # Number of GPUs to use (0 for CPU only)
    
    # Generation parameters
    "seed": 42,                 # Random seed for reproducible responses
    "repeat_penalty": 1.1,      # Penalty for repeating tokens (>1.0 reduces repetition)
    "top_k": 40,               # Number of tokens to consider for sampling
    "top_p": 0.9,             # Cumulative probability threshold for sampling
    
    # Available models (can be extended)
    "available_models": [
        "mistral",      # General purpose model
        "llama2",       # Meta's language model
        "codellama",    # Specialized for code
        "neural-chat"   # Optimized for chat
    ]
}

# Configuration paths
CONFIG_DIR = Path.home() / ".config" / "rich-ollama-chat"
CONFIG_FILE = CONFIG_DIR / "config.json"

def load_config() -> dict:
    """Load configuration from file or create with defaults.
    
    Reads configuration from ~/.config/rich-ollama-chat/config.json.
    If file doesn't exist, creates it with default settings.
    
    Returns:
        dict: Configuration dictionary with all settings
    """
    if not CONFIG_FILE.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    
    with open(CONFIG_FILE, 'r') as f:
        return {**DEFAULT_CONFIG, **json.load(f)}

def save_config(config: dict) -> None:
    """Save configuration to file.
    
    Args:
        config: Configuration dictionary to save
        
    Example:
        >>> config = load_config()
        >>> config['model'] = 'llama2'
        >>> save_config(config)
    """
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def get_config() -> dict:
    """Get current configuration.
    
    Returns:
        dict: Current configuration settings
        
    Example:
        >>> config = get_config()
        >>> model = config['model']
    """
    return load_config()

def update_config(updates: dict) -> dict:
    """Update configuration with new values.
    
    Args:
        updates: Dictionary of settings to update
        
    Returns:
        dict: Updated configuration
        
    Example:
        >>> update_config({'model': 'llama2', 'temperature': 0.8})
    """
    config = load_config()
    config.update(updates)
    save_config(config)
    return config 