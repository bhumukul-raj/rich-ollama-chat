from typing import List, Dict, Optional, Any
from pathlib import Path
import json
import time
from datetime import datetime
from .config import CONFIG_DIR

class Conversation:
    """A class to manage chat conversations and history."""
    
    def __init__(self, title: Optional[str] = None):
        """Initialize a new conversation.
        
        Args:
            title: Optional title for the conversation. If not provided, timestamp will be used.
        """
        self.messages: List[Dict[str, str]] = []
        self.title = title or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.model: str = ""
        self.created_at = time.time()
        self.updated_at = time.time()
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation.
        
        Args:
            role: The role of the message sender ('user' or 'assistant')
            content: The content of the message
        """
        self.messages.append({"role": role, "content": content})
        self.updated_at = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary format.
        
        Returns:
            Dict containing conversation data
        """
        return {
            "title": self.title,
            "messages": self.messages,
            "model": self.model,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conversation':
        """Create a conversation instance from dictionary data.
        
        Args:
            data: Dictionary containing conversation data
            
        Returns:
            New Conversation instance
        """
        conv = cls(title=data["title"])
        conv.messages = data["messages"]
        conv.model = data.get("model", "")
        conv.created_at = data.get("created_at", time.time())
        conv.updated_at = data.get("updated_at", time.time())
        return conv

class ConversationManager:
    """Manages saving, loading, and listing conversations."""
    
    def __init__(self):
        """Initialize the conversation manager."""
        self.history_dir = CONFIG_DIR / "history"
        self.history_dir.mkdir(parents=True, exist_ok=True)
    
    def save_conversation(self, conversation: Conversation) -> Path:
        """Save a conversation to disk.
        
        Args:
            conversation: The conversation to save
            
        Returns:
            Path where the conversation was saved
        """
        file_path = self.history_dir / f"{conversation.title}.json"
        with open(file_path, 'w') as f:
            json.dump(conversation.to_dict(), f, indent=4)
        return file_path
    
    def load_conversation(self, title: str) -> Optional[Conversation]:
        """Load a conversation from disk.
        
        Args:
            title: The title of the conversation to load
            
        Returns:
            Loaded conversation or None if not found
        """
        file_path = self.history_dir / f"{title}.json"
        if not file_path.exists():
            return None
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        return Conversation.from_dict(data)
    
    def list_conversations(self) -> List[Dict[str, Any]]:
        """List all saved conversations.
        
        Returns:
            List of conversation metadata
        """
        conversations = []
        for file_path in self.history_dir.glob("*.json"):
            with open(file_path, 'r') as f:
                data = json.load(f)
                conversations.append({
                    "title": data["title"],
                    "message_count": len(data["messages"]),
                    "model": data.get("model", "unknown"),
                    "created_at": datetime.fromtimestamp(data["created_at"]).strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": datetime.fromtimestamp(data["updated_at"]).strftime("%Y-%m-%d %H:%M:%S")
                })
        return sorted(conversations, key=lambda x: x["updated_at"], reverse=True)
    
    def delete_conversation(self, title: str) -> bool:
        """Delete a conversation from disk.
        
        Args:
            title: The title of the conversation to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        file_path = self.history_dir / f"{title}.json"
        if file_path.exists():
            file_path.unlink()
            return True
        return False 