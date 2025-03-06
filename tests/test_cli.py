import pytest
from click.testing import CliRunner
from rich.console import Console
from rich.theme import Theme
from rich_ollama_chat.cli import cli, chat, config, history, set_conversation_manager, console
from rich_ollama_chat.conversation import Conversation, ConversationManager
import time
from pathlib import Path

# Test theme with required styles
test_theme = Theme({
    "user": "blue",
    "assistant": "green",
    "system": "yellow",
    "warning": "red",
    "highlight": "red"
})

@pytest.fixture(autouse=True)
def mock_console(monkeypatch):
    """Replace the console with a test version that has required styles."""
    test_console = Console(theme=test_theme)
    monkeypatch.setattr('rich_ollama_chat.cli.console', test_console)
    monkeypatch.setattr('rich_ollama_chat.chat.console', test_console)
    return test_console

@pytest.fixture
def cli_runner():
    """Create a Click CLI test runner."""
    return CliRunner()

@pytest.fixture(autouse=True)
def setup_conversation_manager(temp_config_dir):
    """Set up a test conversation manager before each test."""
    manager = ConversationManager()
    set_conversation_manager(manager)
    yield manager
    set_conversation_manager(None)

def test_cli_help(cli_runner):
    """Test CLI help command."""
    result = cli_runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'Rich Ollama Chat' in result.output

def test_config_command(cli_runner, temp_config_dir):
    """Test configuration command."""
    # Test viewing config
    result = cli_runner.invoke(config)
    assert result.exit_code == 0
    assert 'model' in result.output
    assert 'code_theme' in result.output
    
    # Test updating config
    result = cli_runner.invoke(config, ['--model', 'test_model'])
    assert result.exit_code == 0
    assert 'Configuration updated successfully' in result.output
    
    # Verify update
    result = cli_runner.invoke(config)
    assert 'test_model' in result.output

def test_history_list_empty(cli_runner):
    """Test history list command with no conversations."""
    result = cli_runner.invoke(history, ['list'])
    assert result.exit_code == 0
    assert 'No saved conversations found' in result.output

def test_history_commands(cli_runner, setup_conversation_manager):
    """Test history commands with sample conversation."""
    # Create a test conversation
    conv = Conversation("test_chat")
    conv.add_message("user", "Hello")
    conv.add_message("assistant", "Hi there!")
    
    # Save conversation and ensure it's written to disk
    save_path = setup_conversation_manager.save_conversation(conv)
    assert save_path.exists()
    
    # Test list command
    result = cli_runner.invoke(history, ['list'])
    assert result.exit_code == 0
    assert 'test_chat' in result.output
    assert '2' in result.output  # 2 messages
    
    # Test show command
    result = cli_runner.invoke(history, ['show', 'test_chat'])
    assert result.exit_code == 0
    assert 'Hello' in result.output
    assert 'Hi there!' in result.output
    
    # Test delete command
    result = cli_runner.invoke(history, ['delete', 'test_chat'])
    assert result.exit_code == 0
    assert 'deleted successfully' in result.output
    
    # Verify deletion
    result = cli_runner.invoke(history, ['show', 'test_chat'])
    assert 'not found' in result.output

def test_history_nonexistent(cli_runner):
    """Test history commands with non-existent conversation."""
    result = cli_runner.invoke(history, ['show', 'nonexistent'])
    assert result.exit_code == 0
    assert 'not found' in result.output
    
    result = cli_runner.invoke(history, ['delete', 'nonexistent'])
    assert result.exit_code == 0
    assert 'not found' in result.output 