import pytest
from pathlib import Path
import tempfile
import shutil
from rich_ollama_chat.config import CONFIG_DIR
from rich_ollama_chat.conversation import ConversationManager

@pytest.fixture
def temp_config_dir():
    """Create a temporary config directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        original_config_dir = CONFIG_DIR
        temp_config_path = Path(temp_dir) / "rich-ollama-chat"
        temp_config_path.mkdir(parents=True)
        
        # Mock the CONFIG_DIR
        import rich_ollama_chat.config
        rich_ollama_chat.config.CONFIG_DIR = temp_config_path
        import rich_ollama_chat.conversation
        rich_ollama_chat.conversation.CONFIG_DIR = temp_config_path
        
        yield temp_config_path
        
        # Restore original CONFIG_DIR
        rich_ollama_chat.config.CONFIG_DIR = original_config_dir
        rich_ollama_chat.conversation.CONFIG_DIR = original_config_dir

@pytest.fixture
def conversation_manager(temp_config_dir):
    """Create a ConversationManager instance with temporary directory."""
    return ConversationManager()

@pytest.fixture
def mock_ollama_response():
    """Mock Ollama chat response."""
    return [
        {"message": {"content": "Hello"}},
        {"message": {"content": " world"}},
        {"message": {"content": "!"}}
    ] 