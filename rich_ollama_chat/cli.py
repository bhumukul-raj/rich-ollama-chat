from rich.panel import Panel
from rich.console import Console
from .chat import interactive_chat

def main():
    console = Console()
    console.print(Panel.fit(
        "[bold]🚀 AI Chat Interface[/]\n[dim]Powered by Ollama & Rich[/]",
        style="bold yellow on dark_red"
    ))
    interactive_chat()

if __name__ == "__main__":
    main() 