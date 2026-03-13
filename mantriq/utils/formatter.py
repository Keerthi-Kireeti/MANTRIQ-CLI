from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.theme import Theme
from rich import box
import pyfiglet
import os

# Custom theme for an exceptionally clean look
custom_theme = Theme({
    "markdown.header": "bold bright_blue",
    "markdown.code": "cyan",
    "markdown.item": "white",
    "markdown.block_quote": "dim white",
    "markdown.link": "bright_blue underline",
    "agent.name": "bold bright_cyan",
    "backend.info": "bright_yellow",
    "tip.bullet": "bright_blue",
    "tip.text": "grey50"
})

console = Console(theme=custom_theme)

def get_pixel_title(text: str, color: str = "bright_blue"):
    """Generates a pixel-style ASCII art title."""
    fig = pyfiglet.Figlet(font='small')
    ascii_art = fig.renderText(text)
    return Text(ascii_art, style=color)

def print_header(active_agent: str, backend: str = "Local"):
    """Prints a clean, simple, and elegant header."""
    console.clear()
    
    # 1. Pixel Title
    title_text = get_pixel_title("MANTRIQ", color="bright_blue")
    console.print(Align.center(title_text))
    
    # 2. Simple Status Row
    status_row = Text.assemble(
        ("Agent: ", "white"),
        (active_agent, "agent.name"),
        ("  |  ", "grey23"),
        ("Backend: ", "white"),
        (backend, "backend.info")
    )
    console.print(Align.center(status_row))
    console.print(Align.center(Text("─" * 40, style="grey15")))
    console.print("\n")

def format_response(agent_name: str, response: str):
    """Formats AI response with exceptional clarity and spacing."""
    # Use a simple, elegant panel for the response
    md = Markdown(response)
    
    # Header for the response
    console.print(f"\n[bold bright_blue]● {agent_name} Analysis[/bold bright_blue]")
    console.print(Text("─" * 30, style="grey15"))
    
    # Print the markdown content directly for a cleaner "text-first" look
    # but wrapped in a subtle margin for readability
    console.print(md)
    console.print("\n" + "─" * console.width, style="grey11")

def format_help():
    """Displays simplified help information."""
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    table.add_column("Key", style="bright_blue bold")
    table.add_column("Action", style="white")

    table.add_row("TAB", "Cycle Agents")
    table.add_row("load <file>", "Import File")
    table.add_row("analyze", "Run Analysis")
    table.add_row("clear", "Clear Screen")
    table.add_row("exit", "Quit")
    
    console.print("\n[bold white]COMMANDS[/bold white]")
    console.print(table)
    console.print("\n[grey50]Type any message directly to chat with MANTRIQ.[/grey50]\n")
