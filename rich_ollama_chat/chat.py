from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.console import Console
from rich.syntax import Syntax
from rich.status import Status
from rich.theme import Theme
import ollama
import time

# Custom theme with additional styles
custom_theme = Theme({
    "user": "bold cyan",
    "assistant": "italic chartreuse3",
    "system": "dim yellow",
    "code": "grey70 on grey7",
    "warning": "bold red",
    "highlight": "bold yellow on dark_red"
})
console = Console(theme=custom_theme)

def stream_chat_with_formatting(messages, model='mistral', code_theme="dracula"):
    # User message formatting
    user_content = Markdown(f"**🗨️ {messages[-1]['content']}**")
    console.print(
        Panel.fit(
            user_content,
            title="[user]You[/]",
            border_style="user",
            style="user"
        )
    )
    
    # Stream response with enhanced formatting
    accumulated_response = ""
    code_blocks = []
    current_code = None
    
    try:
        start_time = time.time()
        with Live(auto_refresh=False, console=console) as live:
            for chunk in ollama.chat(
                model=model,
                messages=messages,
                stream=True
            ):
                chunk_content = chunk['message']['content']
                accumulated_response += chunk_content
                
                # Detect code blocks
                if '```' in chunk_content:
                    if current_code is None:
                        current_code = {'start': len(accumulated_response) - len(chunk_content)}
                    else:
                        current_code['end'] = len(accumulated_response)
                        code_blocks.append(current_code)
                        current_code = None
                
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
                    subtitle=f"Model: {model}"
                )
                live.update(response_panel, refresh=True)
        
        console.print(f"\n[system]Response time: {time.time()-start_time:.2f}s[/]")
        return accumulated_response
        
    except Exception as e:
        console.print(f"[warning]Error: {str(e)}[/]", style="warning")
        return None

def interactive_chat():
    messages = []
    while True:
        try:
            user_input = console.input("[user]\n💬 You (q to quit): [/]")
            if user_input.lower() in ('q', 'quit'):
                break
            messages.append({'role': 'user', 'content': user_input})
            response = stream_chat_with_formatting(messages)
            if response:
                messages.append({'role': 'assistant', 'content': response})
        except KeyboardInterrupt:
            console.print("\n[warning]Session ended by user.[/]")
            break 