from typing import Optional
import click
from rich.panel import Panel
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown
from .chat import interactive_chat, custom_theme
from .config import get_config, update_config
from .conversation import ConversationManager, Conversation

console = Console(theme=custom_theme)

# Create conversation manager at module level
_conversation_manager = None

def get_conversation_manager():
    """Get the conversation manager instance.
    
    This function ensures we use the same conversation manager instance
    throughout the application, while allowing tests to override it.
    """
    global _conversation_manager
    if _conversation_manager is None:
        _conversation_manager = ConversationManager()
    return _conversation_manager

def set_conversation_manager(manager: ConversationManager):
    """Set the conversation manager instance.
    
    This function is primarily used in tests to inject a test-specific
    conversation manager.
    """
    global _conversation_manager
    _conversation_manager = manager

@click.group()
def cli():
    """Rich Ollama Chat - A beautiful terminal chat interface"""
    pass

@cli.command()
@click.option('--model', help='Model to use for chat')
@click.option('--theme', help='Code theme to use')
@click.option('--no-history', is_flag=True, help='Disable chat history saving')
@click.option('--continue', 'continue_chat', help='Continue a previous conversation by title')
def chat(model: Optional[str], theme: Optional[str], no_history: bool, continue_chat: Optional[str]):
    """Start an interactive chat session"""
    console.print(Panel.fit(
        "[bold]🚀 AI Chat Interface[/]\n[dim]Powered by Ollama & Rich[/]",
        style="bold yellow on dark_red"
    ))
    
    if model or theme:
        updates = {}
        if model:
            updates['model'] = model
        if theme:
            updates['code_theme'] = theme
        update_config(updates)
    
    initial_conversation = None
    if continue_chat:
        initial_conversation = get_conversation_manager().load_conversation(continue_chat)
        if not initial_conversation:
            console.print(f"[warning]Conversation '{continue_chat}' not found.[/]")
            return
        
        console.print(f"[green]Continuing conversation: {continue_chat}[/]")
    
    interactive_chat(
        initial_conversation=initial_conversation,
        save_history=not no_history
    )

@cli.command()
@click.option('--model', help='Set default model')
@click.option('--theme', help='Set default code theme')
def config(model: Optional[str], theme: Optional[str]):
    """View or update configuration"""
    current_config = get_config()
    
    if model or theme:
        updates = {}
        if model:
            updates['model'] = model
        if theme:
            updates['code_theme'] = theme
        current_config = update_config(updates)
        console.print("[green]Configuration updated successfully![/]")
    
    console.print(Panel.fit(
        "\n".join([f"[cyan]{k}:[/] {v}" for k, v in current_config.items()]),
        title="[yellow]Current Configuration[/]"
    ))

@cli.group()
def history():
    """Manage chat history"""
    pass

@history.command(name="list")
def list_history():
    """List all saved conversations"""
    conversations = get_conversation_manager().list_conversations()
    
    if not conversations:
        console.print("[yellow]No saved conversations found.[/]")
        return
    
    table = Table(
        "Title", "Messages", "Model", "Created", "Last Updated",
        title="Saved Conversations",
        show_header=True,
        header_style="bold magenta"
    )
    
    for conv in conversations:
        table.add_row(
            conv["title"],
            str(conv["message_count"]),
            conv["model"],
            conv["created_at"],
            conv["updated_at"]
        )
    
    console.print(table)

@history.command()
@click.argument('title')
def show(title: str):
    """Show a specific conversation"""
    conversation = get_conversation_manager().load_conversation(title)
    if not conversation:
        console.print(f"[warning]Conversation '{title}' not found.[/]")
        return
    
    for msg in conversation.messages:
        if msg["role"] == "user":
            console.print(Panel.fit(
                Markdown(msg["content"]),
                title="[user]You[/]",
                border_style="user"
            ))
        else:
            console.print(Panel.fit(
                Markdown(msg["content"]),
                title="[assistant]AI Assistant[/]",
                border_style="assistant"
            ))

@history.command()
@click.argument('title')
def delete(title: str):
    """Delete a conversation"""
    if get_conversation_manager().delete_conversation(title):
        console.print(f"[green]Conversation '{title}' deleted successfully.[/]")
    else:
        console.print(f"[warning]Conversation '{title}' not found.[/]")

def main():
    cli() 