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

# Custom theme with semantic color mappings for different message types
custom_theme = Theme({
    "user": "bold cyan",          # User messages in cyan
    "assistant": "italic chartreuse3",  # AI responses in green
    "system": "dim yellow",       # System messages in yellow
    "code": "grey70 on grey7",    # Code blocks with dark background
    "warning": "bold red",        # Warnings in red
    "highlight": "bold yellow on dark_red"  # Important highlights
})
console = Console(theme=custom_theme)

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
    """Calculate optimal panel width based on terminal size.
    
    Uses different width calculations based on whether the terminal
    is in full screen mode or windowed mode:
    - Full screen (>90% of screen width): Uses 80% of width
    - Windowed: Uses full available width minus padding
    
    Returns:
        int: Calculated panel width in characters
    """
    terminal_width = console.width
    screen_width = shutil.get_terminal_size().columns
    
    # If terminal width is close to screen width (full screen/maximized)
    if terminal_width >= screen_width * 0.9:  # Using 90% as threshold
        return min(int(terminal_width * 0.8), terminal_width - 4)
    else:
        return terminal_width - 4  # Use full width with minimal padding

def stream_chat_with_formatting(
    messages: List[Dict[str, str]], 
    model: Optional[str] = None, 
    code_theme: Optional[str] = None,
    conversation: Optional[Conversation] = None
) -> Optional[str]:
    """Stream chat responses with rich formatting and real-time display.
    
    This function handles:
    - Real-time streaming of responses
    - Code block detection and syntax highlighting
    - Markdown formatting
    - Adaptive width based on terminal size
    - Response time tracking
    - Chat history management
    - Response interruption (Ctrl+C to stop)
    
    Args:
        messages: List of message dictionaries with 'role' and 'content'
        model: Optional model name (defaults to config)
        code_theme: Optional code theme name (defaults to config)
        conversation: Optional conversation object for history
        
    Returns:
        Optional[str]: The complete response text, or partial text if interrupted,
                      or None if an error occurred
    """
    config = get_config()
    model = model or config['model']
    code_theme = code_theme or config['code_theme']
    
    # Calculate panel width based on terminal size
    panel_width = get_panel_width()
    
    if not check_ollama_connection(model):
        return None
    
    # Add message to conversation if provided
    if conversation:
        conversation.add_message("user", messages[-1]['content'])
        conversation.model = model
    
    # User message formatting with width
    user_content = Markdown(f"**🗨️ {messages[-1]['content']}**")
    console.print(
        Panel.fit(
            user_content,
            title="[user]You[/]",
            border_style="user",
            style="user",
            width=panel_width
        )
    )
    
    # Stream response with enhanced formatting
    accumulated_response = ""
    code_blocks = []
    current_code = None
    token_count = 0
    was_interrupted = False
    
    try:
        start_time = time.time()
        # Prepare options dict based on config
        options = {
            "num_ctx": config["num_ctx"],
            "num_thread": config["num_thread"],
            "seed": config["seed"],
            "temperature": config["temperature"],
            "repeat_penalty": config["repeat_penalty"],
            "top_k": config["top_k"],
            "top_p": config["top_p"]
        }
        
        # Only add GPU settings if use_gpu is True
        if config.get("use_gpu", False):
            options["num_gpu"] = config["num_gpu"]
        
        response_chunks = ollama.chat(
            model=model,
            messages=messages,
            stream=True,
            options=options
        )
        
        # Initialize live display with width
        live = Live(
            Panel("", 
                title="[assistant]AI Assistant[/] 🤖", 
                border_style="assistant", 
                style="assistant", 
                subtitle=f"Model: {model}",
                width=panel_width
            ),
            console=console,
            refresh_per_second=10  # Increase refresh rate
        )
        live.start()
        
        # Process chunks as they arrive
        try:
            for chunk in response_chunks:
                chunk_content = chunk['message']['content']
                accumulated_response += chunk_content
                token_count += 1
                
                # Detect code blocks
                if '```' in chunk_content:
                    if current_code is None:
                        current_code = {'start': len(accumulated_response) - len(chunk_content)}
                    else:
                        current_code['end'] = len(accumulated_response)
                        code_blocks.append(current_code)
                        current_code = None
                
                # Update display with current content
                try:
                    # Create formatted content
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
                    live.update(response_panel)
                except Exception as e:
                    # Handle Live display error in tests
                    pass
                    
        except KeyboardInterrupt:
            was_interrupted = True
            console.print("\n[warning]Response interrupted by user.[/]")
        
        # Stop live display
        live.stop()
        
        # Add response to conversation if provided
        if conversation and accumulated_response:
            conversation.add_message("assistant", accumulated_response)
        
        elapsed_time = time.time() - start_time
        status = "interrupted" if was_interrupted else "completed"
        console.print(f"\n[system]Response {status} in {elapsed_time:.2f}s[/]")
        return accumulated_response
        
    except Exception as e:
        console.print(f"[warning]Error: {str(e)}[/]", style="warning")
        return None

def interactive_chat(
    initial_conversation: Optional[Conversation] = None,
    save_history: bool = True
) -> None:
    """Start an interactive chat session with history management.
    
    Provides a REPL-like interface for chatting with the AI model.
    Features:
    - Command history
    - Session persistence
    - Conversation management
    - Graceful exit handling
    - Response interruption (Ctrl+C to stop current response)
    - Double Ctrl+C to exit session
    
    Args:
        initial_conversation: Optional conversation to continue from
        save_history: Whether to save chat history (default: True)
        
    Example:
        >>> interactive_chat()  # Start new chat
        >>> conv = Conversation("my_chat")
        >>> interactive_chat(conv)  # Continue existing chat
    """
    conversation = initial_conversation or Conversation()
    conversation_manager = ConversationManager() if save_history else None
    
    messages = conversation.messages if initial_conversation else []
    
    # Print welcome message with instructions
    console.print(Panel.fit(
        "[bold]Welcome to Rich Ollama Chat![/]\n"
        "- Type your message and press Enter to send\n"
        "- Press [bold cyan]Ctrl+C[/] to stop the current response\n"
        "- Press [bold cyan]Ctrl+C twice[/] to exit session\n"
        "- Type [bold cyan]q[/] or [bold cyan]quit[/] to exit",
        title="Instructions",
        border_style="yellow"
    ))
    
    last_interrupt_time = 0
    DOUBLE_INTERRUPT_THRESHOLD = 1.0  # seconds
    
    while True:
        try:
            user_input = console.input("[user]\n💬 You (q to quit): [/]")
            if user_input.lower() in ('q', 'quit'):
                break
                
            messages.append({'role': 'user', 'content': user_input})
            try:
                response = stream_chat_with_formatting(messages, conversation=conversation)
                
                if response:
                    messages.append({'role': 'assistant', 'content': response})
                    
                    # Save conversation after each exchange if enabled
                    if conversation_manager:
                        conversation_manager.save_conversation(conversation)
                        
            except KeyboardInterrupt:
                # Check if this is a double interrupt
                current_time = time.time()
                if current_time - last_interrupt_time < DOUBLE_INTERRUPT_THRESHOLD:
                    console.print("\n[warning]Session ended by user (double Ctrl+C).[/]")
                    break
                last_interrupt_time = current_time
                console.print("\n[system]Ready for next message...[/]")
                continue
                    
        except KeyboardInterrupt:
            # Check if this is a double interrupt
            current_time = time.time()
            if current_time - last_interrupt_time < DOUBLE_INTERRUPT_THRESHOLD:
                console.print("\n[warning]Session ended by user (double Ctrl+C).[/]")
                break
            last_interrupt_time = current_time
            console.print("\n[system]Ready for next message...[/]")
            continue
    
    # Final save on exit
    if conversation_manager and len(conversation.messages) > 0:
        conversation_manager.save_conversation(conversation) 