from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich import box
import pyfiglet
import os

console = Console()

def get_pixel_title(text: str, color: str = "bright_blue"):
    """Generates a pixel-style ASCII art title."""
    fig = pyfiglet.Figlet(font='small') # 'small' or 'slant' or 'block'
    ascii_art = fig.renderText(text)
    return Text(ascii_art, style=color)

def format_response(agent_name: str, response: str):
    """Formats the AI response using Rich panels and markdown."""
    title = f"MANTRIQ {agent_name} Report"
    md = Markdown(response)
    panel = Panel(
        md,
        title=f"[bold blue]{title}[/bold blue]",
        border_style="bright_blue",
        box=box.ROUNDED,
        padding=(1, 2)
    )
    console.print(panel)

def format_help():
    """Displays help information in a table."""
    table = Table(title="MANTRIQ CLI Commands & Shortcuts", box=box.SIMPLE)
    table.add_column("Command/Key", style="cyan")
    table.add_column("Description", style="white")

    table.add_row("load <file>", "Load code from a file")
    table.add_row("paste", "Paste multi-line code (Alt+Enter to finish)")
    table.add_row("analyze", "Run active agent on loaded code")
    table.add_row("<text>", "Chat with MANTRIQ directly")
    table.add_row("clear", "Clear terminal screen")
    table.add_row("refresh", "Redraw the TUI header")
    table.add_row("agent", "Show current active agent")
    table.add_row("help", "Show this help menu")
    table.add_row("exit", "Exit MANTRIQ CLI")
    
    table.add_section()
    table.add_row("TAB / Shift+TAB", "Cycle agents")
    table.add_row("Ctrl+E", "Switch to Explain Agent")
    table.add_row("Ctrl+D", "Switch to Debug Agent")
    table.add_row("Ctrl+R", "Switch to Review Agent")
    table.add_row("Ctrl+O", "Switch to Optimize Agent")
    table.add_row("Ctrl+Q", "Exit MANTRIQ")
    
    console.print(table)

def print_header(active_agent: str, backend: str = "Local"):
    """Prints the centralized TUI header matching the reference image."""
    console.clear()
    
    # 1. Pixel Title
    title_text = get_pixel_title("MANTRIQ", color="bright_blue")
    console.print(Align.center(title_text))
    
    # 2. Main Search/Status Box (Simplified look)
    # Matching the dark grey box in the image
    status_content = Text.assemble(
        ("Type anything to chat... ", "grey50"),
        ("\"Explain the logic of this code\"", "grey37")
    )
    
    agent_row = Text.assemble(
        ("Active Agent: ", "white"),
        (active_agent, "bright_cyan bold"),
        ("  Backend: ", "white"),
        (backend, "bright_yellow")
    )

    main_panel = Panel(
        Align.center(Text.assemble(status_content, "\n\n", agent_row)),
        box=box.ROUNDED,
        border_style="grey23",
        width=80,
        padding=(1, 2),
        style="on grey11"
    )
    console.print(Align.center(main_panel))
    
    # 3. Quick Shortcuts Hint
    shortcuts = Text.assemble(
        ("tab", "bright_blue"), (" agents  ", "grey50"),
        ("ctrl+q", "bright_blue"), (" commands", "grey50")
    )
    console.print(Align.center(shortcuts))
    
    console.print("\n")
    
    # 4. Tip at the bottom
    tip = Text.assemble(
        ("● Tip ", "bright_yellow"),
        (f"Use ", "grey50"),
        ("'load'", "white"),
        (" to add files to session context before ", "grey50"),
        ("'analyze'", "white")
    )
    console.print(Align.center(tip))
    console.print("\n" + "─" * console.width, style="grey15")
