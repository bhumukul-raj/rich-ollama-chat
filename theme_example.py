from rich_ollama_chat import stream_chat_with_formatting

def try_different_themes():
    # Message that will generate a code response
    messages = [{
        "role": "user",
        "content": "Write a simple Python function to calculate factorial"
    }]
    
    # Try different themes
    themes = ["dracula", "monokai", "github-dark", "solarized-dark"]
    
    for theme in themes:
        print(f"\nTrying theme: {theme}")
        response = stream_chat_with_formatting(
            messages=messages,
            model="mistral",
            code_theme=theme
        )

if __name__ == "__main__":
    try_different_themes() 