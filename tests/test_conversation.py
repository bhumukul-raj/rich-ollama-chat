import pytest
from datetime import datetime
import time
from rich_ollama_chat.conversation import Conversation, ConversationManager

def test_conversation_initialization():
    """Test conversation initialization with and without title."""
    # Test with custom title
    conv = Conversation(title="test_chat")
    assert conv.title == "test_chat"
    assert isinstance(conv.messages, list)
    assert len(conv.messages) == 0
    
    # Test without title (should use timestamp)
    conv = Conversation()
    assert datetime.strptime(conv.title, "%Y%m%d_%H%M%S")
    
def test_conversation_add_message():
    """Test adding messages to conversation."""
    conv = Conversation("test_chat")
    
    # Add user message
    conv.add_message("user", "Hello")
    assert len(conv.messages) == 1
    assert conv.messages[0] == {"role": "user", "content": "Hello"}
    
    # Add assistant message
    conv.add_message("assistant", "Hi there!")
    assert len(conv.messages) == 2
    assert conv.messages[1] == {"role": "assistant", "content": "Hi there!"}
    
def test_conversation_serialization():
    """Test conversation serialization to/from dict."""
    conv = Conversation("test_chat")
    conv.add_message("user", "Hello")
    conv.model = "test_model"
    
    # Test to_dict
    data = conv.to_dict()
    assert data["title"] == "test_chat"
    assert len(data["messages"]) == 1
    assert data["model"] == "test_model"
    assert "created_at" in data
    assert "updated_at" in data
    
    # Test from_dict
    new_conv = Conversation.from_dict(data)
    assert new_conv.title == conv.title
    assert new_conv.messages == conv.messages
    assert new_conv.model == conv.model
    assert new_conv.created_at == conv.created_at
    assert new_conv.updated_at == conv.updated_at

def test_conversation_manager_save_load(conversation_manager):
    """Test saving and loading conversations."""
    # Create and save conversation
    conv = Conversation("test_chat")
    conv.add_message("user", "Hello")
    save_path = conversation_manager.save_conversation(conv)
    assert save_path.exists()
    
    # Load conversation
    loaded_conv = conversation_manager.load_conversation("test_chat")
    assert loaded_conv is not None
    assert loaded_conv.title == conv.title
    assert loaded_conv.messages == conv.messages
    
    # Test loading non-existent conversation
    assert conversation_manager.load_conversation("non_existent") is None

def test_conversation_manager_list(conversation_manager):
    """Test listing conversations."""
    # Create some test conversations
    conv1 = Conversation("chat1")
    conv1.add_message("user", "Hello 1")
    conv2 = Conversation("chat2")
    conv2.add_message("user", "Hello 2")
    
    # Save conversations
    conversation_manager.save_conversation(conv1)
    time.sleep(0.1)  # Ensure different timestamps
    conversation_manager.save_conversation(conv2)
    
    # List conversations
    conversations = conversation_manager.list_conversations()
    assert len(conversations) == 2
    # Should be sorted by updated_at (most recent first)
    assert conversations[0]["title"] == "chat2"
    assert conversations[1]["title"] == "chat1"

def test_conversation_manager_delete(conversation_manager):
    """Test deleting conversations."""
    # Create and save a conversation
    conv = Conversation("test_chat")
    conv.add_message("user", "Hello")
    conversation_manager.save_conversation(conv)
    
    # Delete existing conversation
    assert conversation_manager.delete_conversation("test_chat") is True
    assert conversation_manager.load_conversation("test_chat") is None
    
    # Try to delete non-existent conversation
    assert conversation_manager.delete_conversation("non_existent") is False 