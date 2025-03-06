import pytest
from unittest.mock import patch, MagicMock
from rich_ollama_chat.chat import check_ollama_connection, stream_chat_with_formatting
from rich_ollama_chat.conversation import Conversation

@pytest.fixture
def mock_ollama():
    """Mock the ollama module."""
    with patch('rich_ollama_chat.chat.ollama') as mock:
        yield mock

def test_check_ollama_connection_success(mock_ollama):
    """Test successful Ollama connection check."""
    mock_ollama.chat.return_value = {"message": {"content": "test"}}
    assert check_ollama_connection("test_model") is True

def test_check_ollama_connection_failure(mock_ollama):
    """Test failed Ollama connection check."""
    mock_ollama.chat.side_effect = Exception("Connection failed")
    assert check_ollama_connection("test_model") is False

def test_stream_chat_formatting(mock_ollama, mock_ollama_response):
    """Test chat streaming with formatting."""
    # Setup mock to return an iterator
    mock_ollama.chat.return_value = iter(mock_ollama_response)
    
    # Test messages
    messages = [{"role": "user", "content": "Hello"}]
    conversation = Conversation("test_chat")
    
    # Run chat
    response = stream_chat_with_formatting(
        messages=messages,
        model="test_model",
        code_theme="monokai",
        conversation=conversation
    )
    
    # Verify response
    expected_response = "".join(chunk["message"]["content"] for chunk in mock_ollama_response)
    assert response == expected_response
    assert len(conversation.messages) == 2
    assert conversation.messages[0]["role"] == "user"
    assert conversation.messages[1]["role"] == "assistant"
    assert conversation.model == "test_model"

def test_stream_chat_with_code_blocks(mock_ollama):
    """Test chat streaming with code block formatting."""
    # Mock response with code blocks
    mock_response = [
        {"message": {"content": "Here's a Python function:\n```python\n"}},
        {"message": {"content": "def hello():\n    print('Hello!')\n"}},
        {"message": {"content": "```\nThat's all!"}},
    ]
    mock_ollama.chat.return_value = iter(mock_response)
    
    messages = [{"role": "user", "content": "Show me a Python function"}]
    conversation = Conversation("test_chat")
    
    response = stream_chat_with_formatting(
        messages=messages,
        model="test_model",
        code_theme="monokai",
        conversation=conversation
    )
    
    # Verify response contains code block
    expected_response = "".join(chunk["message"]["content"] for chunk in mock_response)
    assert response == expected_response
    assert len(conversation.messages) == 2
    assert "```python" in conversation.messages[1]["content"]
    assert "def hello()" in conversation.messages[1]["content"]

def test_stream_chat_error_handling(mock_ollama):
    """Test error handling in chat streaming."""
    # Setup mock to raise exception
    mock_ollama.chat.side_effect = Exception("Chat error")
    
    messages = [{"role": "user", "content": "Hello"}]
    conversation = Conversation("test_chat")
    
    # Add the user message first
    conversation.add_message("user", "Hello")
    
    response = stream_chat_with_formatting(
        messages=messages,
        model="test_model",
        conversation=conversation
    )
    
    assert response is None
    assert len(conversation.messages) == 1  # Only user message should be present 