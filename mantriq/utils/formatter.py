from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.theme import Theme
from rich.layout import Layout
from rich import box
import pyfiglet
import os

# Custom theme for the unique Kilo-style look
custom_theme = Theme({
    "markdown.header": "bold bright_blue",
    "markdown.code": "cyan",
    "markdown.item": "white",
    "markdown.block_quote": "dim white",
    "markdown.link": "bright_blue underline",
    "agent.name": "bold white",
    "agent.active": "bright_blue bold",
    "backend.info": "grey37",
    "shortcut.key": "bright_blue",
    "shortcut.label": "grey50",
    "tip.bullet": "bright_yellow",
    "tip.text": "grey50"
})

console = Console(theme=custom_theme)

def get_pixel_title(text: str, color: str = "bright_blue"):
    """Generates a clear pixel-style ASCII art title with separated letters."""
    # 'big' or 'standard' fonts often have better spacing between 'M' and 'A'
    fig = pyfiglet.Figlet(font='big') 
    ascii_art = fig.renderText(text)
    return Text(ascii_art, style=color)

def generate_ide_layout(active_agent: str, loaded_code: str, history: list, status: str = "Ready"):
    """Generates a true IDE-like layout for the terminal."""
    layout = Layout()
    
    # Split into Header, Main (Editor + Sidebar), and Footer
    layout.split(
        Layout(name="header", size=10),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3)
    )
    
    # Main split into Editor (left) and Sidebar (right)
    layout["main"].split_row(
        Layout(name="editor", ratio=2),
        Layout(name="sidebar", ratio=1)
    )
    
    # Header Content
    title_art = get_pixel_title("MANTRIQ", "bright_blue")
    layout["header"].update(
        Panel(Align.center(title_art), border_style="blue", box=box.ROUNDED)
    )
    
    # Editor Content (Code Viewer)
    code_content = loaded_code if loaded_code else "No code loaded. Use 'load <file>' to begin."
    layout["editor"].update(
        Panel(
            Markdown(f"```python\n{code_content}\n```"),
            title="[bold cyan]Editor / Code Context[/bold cyan]",
            border_style="cyan",
            box=box.ROUNDED
        )
    )
    
    # Sidebar Content (Agent + Chat History)
    history_text = Text()
    for agent, msg in history[-5:]: # Show last 5 messages
        history_text.append(f"● {agent}: ", style="bright_blue bold")
        history_text.append(f"{msg[:50]}...\n", style="white")
        
    sidebar_table = Table.grid(padding=1)
    sidebar_table.add_row("[bold cyan]Active Agent:[/bold cyan]", f"[white]{active_agent}[/white]")
    sidebar_table.add_row("[bold cyan]Status:[/bold cyan]", f"[green]{status}[/green]")
    
    layout["sidebar"].split(
        Layout(Panel(sidebar_table, title="[bold blue]Agent Info[/bold blue]", border_style="blue")),
        Layout(Panel(history_text, title="[bold blue]Recent Activity[/bold blue]", border_style="blue"))
    )
    
    # Footer Content
    footer_text = Text.assemble(
        ("TAB", "bright_blue"), (" Next Agent  ", "grey50"),
        ("CTRL+Q", "bright_blue"), (" Exit  ", "grey50"),
        ("LOAD", "bright_blue"), (" Import  ", "grey50"),
        ("FULL", "bright_blue"), (" Fullscreen Toggle", "grey50")
    )
    layout["footer"].update(Panel(Align.center(footer_text), border_style="blue", box=box.MINIMAL))
    
    return layout

def print_header(active_agent: str, backend: str = "Local"):
    """Prints the unique dashboard."""
    console.clear()
    console.print(generate_kilo_dashboard(active_agent, backend))

def format_response_frame(agent_name: str, response_text: str):
    """Returns a panel for the response to be used in Live updates."""
    md = Markdown(response_text)
    return Panel(
        md,
        title=f"[bold bright_blue]● {agent_name} Analysis[/bold bright_blue]",
        border_style="bright_blue",
        box=box.ROUNDED,
        padding=(1, 2)
    )

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
