"""Rich Ollama Chat - A beautiful terminal-based chat interface.

This module provides the core functionality for the chat interface, including:
- Real-time response streaming with rich formatting
- Code block detection and syntax highlighting
- Adaptive width based on terminal size
- CPU/GPU configuration handling
- Chat history management
"""

from typing import List, Dict, Optional, Any, Union
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.console import Console
from rich.syntax import Syntax
from rich.status import Status
from rich.theme import Theme
from rich.progress import Progress, SpinnerColumn, TextColumn
import ollama
import time
import os
import shutil
from .config import get_config
from .conversation import Conversation, ConversationManager

# Detect if we're running in Jupyter
try:
    from IPython import get_ipython
    from IPython.display import clear_output, display, HTML
    is_jupyter = get_ipython().__class__.__name__ == 'ZMQInteractiveShell'
except ImportError:
    is_jupyter = False

# Custom theme with semantic color mappings for different message types
custom_theme = Theme({
    "user": "bold cyan",          # User messages in cyan
    "assistant": "italic chartreuse3",  # AI responses in green
    "system": "dim yellow",       # System messages in yellow
    "code": "grey70 on grey7",    # Code blocks with dark background
    "warning": "bold red",        # Warnings in red
    "highlight": "bold yellow on dark_red"  # Important highlights
})

# Create console with appropriate settings for environment
if is_jupyter:
    console = Console(theme=custom_theme, record=True)
else:
    console = Console(theme=custom_theme)

def clear_display():
    """Clear the display in either Jupyter or terminal environment."""
    if is_jupyter:
        clear_output(wait=True)
    else:
        console.clear()

def display_output(content, live_display: Optional[Live] = None):
    """Display content in either Jupyter or terminal environment.
    
    Args:
        content: The content to display
        live_display: Optional Live display for terminal updates
    """
    if is_jupyter:
        display(HTML(console.export_html(content)))
    elif live_display:
        live_display.update(content)
    else:
        console.print(content)

def check_ollama_connection(model: str) -> bool:
    """Check if Ollama is running and the specified model is available.
    
    Attempts to make a test request to Ollama with the specified model.
    Displays a status indicator during the check.
    
    Args:
        model: Name of the model to check (e.g., "mistral", "llama2")
        
    Returns:
        bool: True if connection is successful and model is available,
              False if connection fails or model is not available
    """
    try:
        with Status("[yellow]Checking Ollama connection...[/]"):
            ollama.chat(model=model, messages=[{"role": "user", "content": "test"}], stream=False)
        return True
    except Exception as e:
        console.print(f"[warning]Error connecting to Ollama: {str(e)}[/]", style="warning")
        return False

def get_panel_width() -> int:
    """Calculate optimal panel width based on environment."""
    if is_jupyter:
        return 120  # Fixed width for Jupyter
    
    terminal_width = console.width
    screen_width = shutil.get_terminal_size().columns
    
    if terminal_width >= screen_width * 0.9:
        return min(int(terminal_width * 0.8), terminal_width - 4)
    else:
        return terminal_width - 4

def stream_chat_with_formatting(
    messages: List[Dict[str, str]], 
    model: Optional[str] = None, 
    code_theme: Optional[str] = None,
    conversation: Optional[Conversation] = None
) -> Optional[str]:
    """Stream chat responses with rich formatting and real-time display."""
    config = get_config()
    model = model or config['model']
    code_theme = code_theme or config['code_theme']
    panel_width = get_panel_width()
    
    if not check_ollama_connection(model):
        return None
    
    if conversation:
        conversation.add_message("user", messages[-1]['content'])
        conversation.model = model
    
    # User message formatting
    user_content = Markdown(f"**🗨️ {messages[-1]['content']}**")
    user_panel = Panel.fit(
        user_content,
        title="[user]You[/]",
        border_style="user",
        style="user",
        width=panel_width
    )
    display_output(user_panel)
    
    accumulated_response = ""
    code_blocks = []
    current_code = None
    token_count = 0
    was_interrupted = False
    
    try:
        start_time = time.time()
        options = {
            "num_ctx": config["num_ctx"],
            "num_thread": config["num_thread"],
            "seed": config["seed"],
            "temperature": config["temperature"],
            "repeat_penalty": config["repeat_penalty"],
            "top_k": config["top_k"],
            "top_p": config["top_p"]
        }
        
        if config.get("use_gpu", False):
            options["num_gpu"] = config["num_gpu"]
        
        response_chunks = ollama.chat(
            model=model,
            messages=messages,
            stream=True,
            options=options
        )
        
        # Initialize live display for terminal
        live = None if is_jupyter else Live(
            Panel("", 
                title="[assistant]AI Assistant[/] 🤖", 
                border_style="assistant", 
                style="assistant", 
                subtitle=f"Model: {model}",
                width=panel_width
            ),
            console=console,
            refresh_per_second=10
        )
        
        if live:
            live.start()
        
        try:
            for chunk in response_chunks:
                chunk_content = chunk['message']['content']
                accumulated_response += chunk_content
                token_count += 1
                
                if '```' in chunk_content:
                    if current_code is None:
                        current_code = {'start': len(accumulated_response) - len(chunk_content)}
                    else:
                        current_code['end'] = len(accumulated_response)
                        code_blocks.append(current_code)
                        current_code = None
                
                # Update display
                formatted_content = []
                last_pos = 0
                for code in code_blocks:
                    formatted_content.append(Markdown(accumulated_response[last_pos:code['start']]))
                    code_text = accumulated_response[code['start']:code['end']]
                    formatted_content.append(Syntax(
                        code_text.replace('```python', '').replace('```', ''),
                        "python",
                        theme=code_theme,
                        line_numbers=True,
                        background_color="default"
                    ))
                    last_pos = code['end']
                formatted_content.append(Markdown(accumulated_response[last_pos:]))
                
                response_panel = Panel(
                    *formatted_content,
                    title="[assistant]AI Assistant[/] 🤖",
                    border_style="assistant",
                    style="assistant",
                    subtitle=f"Model: {model}",
                    width=panel_width
                )
                
                if is_jupyter:
                    clear_output(wait=True)
                    display_output(user_panel)
                    display_output(response_panel)
                else:
                    display_output(response_panel, live)
                    
        except KeyboardInterrupt:
            was_interrupted = True
            display_output("[warning]Response interrupted by user.[/]")
        
        if live:
            live.stop()
        
        if conversation and accumulated_response:
            conversation.add_message("assistant", accumulated_response)
        
        elapsed_time = time.time() - start_time
        status = "interrupted" if was_interrupted else "completed"
        display_output(f"[system]Response {status} in {elapsed_time:.2f}s[/]")
        return accumulated_response
        
    except Exception as e:
        display_output(f"[warning]Error: {str(e)}[/]")
        return None

def interactive_chat(
    initial_conversation: Optional[Conversation] = None,
    save_history: bool = True
) -> None:
    """Start an interactive chat session with history management."""
    conversation = initial_conversation or Conversation()
    conversation_manager = ConversationManager() if save_history else None
    messages = conversation.messages if initial_conversation else []
    
    # Welcome message with environment-specific instructions
    welcome_text = "[bold]Welcome to Rich Ollama Chat![/]\n"
    if is_jupyter:
        welcome_text += (
            "- Type your message in the input cell below\n"
            "- Use [bold cyan]Interrupt Kernel[/] to stop the current response\n"
        )
    else:
        welcome_text += (
            "- Type your message and press Enter to send\n"
            "- Press [bold cyan]Ctrl+C[/] to stop the current response\n"
            "- Press [bold cyan]Ctrl+C twice[/] to exit session\n"
        )
    welcome_text += "- Type [bold cyan]q[/] or [bold cyan]quit[/] to exit"
    
    welcome_panel = Panel.fit(
        welcome_text,
        title="Instructions",
        border_style="yellow"
    )
    display_output(welcome_panel)
    
    last_interrupt_time = 0
    DOUBLE_INTERRUPT_THRESHOLD = 1.0  # seconds
    
    while True:
        try:
            if is_jupyter:
                # In Jupyter, we'll use IPython's input
                from IPython.display import display, HTML
                display(HTML("<div style='margin: 10px 0;'><strong style='color: cyan;'>💬 You (q to quit): </strong></div>"))
                user_input = input()
            else:
                user_input = console.input("[user]\n💬 You (q to quit): [/]")
                
            if user_input.lower() in ('q', 'quit'):
                break
                
            messages.append({'role': 'user', 'content': user_input})
            response = stream_chat_with_formatting(messages, conversation=conversation)
            
            if response:
                messages.append({'role': 'assistant', 'content': response})
                if conversation_manager:
                    conversation_manager.save_conversation(conversation)
                    
        except KeyboardInterrupt:
            if is_jupyter:
                display_output("[system]Response interrupted. Ready for next message...[/]")
                continue
            else:
                # Terminal mode: handle double Ctrl+C
                current_time = time.time()
                if current_time - last_interrupt_time < DOUBLE_INTERRUPT_THRESHOLD:
                    display_output("\n[warning]Session ended by user (double Ctrl+C).[/]")
                    break
                last_interrupt_time = current_time
                display_output("\n[system]Ready for next message (Ctrl+C again to exit)...[/]")
                continue
    
    if conversation_manager and len(conversation.messages) > 0:
        conversation_manager.save_conversation(conversation) 