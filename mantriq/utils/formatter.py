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

def get_pixel_title(text: str, color: str = "bright_yellow"):
    """Generates a pixel-style ASCII art title."""
    fig = pyfiglet.Figlet(font='block') # 'block' or 'banner' for thicker pixel look
    ascii_art = fig.renderText(text)
    return Text(ascii_art, style=color)

def generate_kilo_dashboard(active_agent: str, backend: str = "Local", tip_text: str = None):
    """Generates the centered unique dashboard matching the reference image."""
    layout = Layout()
    
    # Header: Pixel Title
    title_art = get_pixel_title("MANTRIQ", color="bright_yellow")
    header = Align.center(title_art, vertical="middle")
    
    # Central Box (Dark Grey Panel)
    search_prompt = Text("Ask anything... \"What is the tech stack of this project?\"", style="grey37")
    
    # Agents list with active highlight
    agents = ["Chat", "Explain", "Debug", "Review", "Optimize"]
    agent_row = Text()
    for agent in agents:
        if agent == active_agent:
            agent_row.append(f"{agent} ", style="agent.active")
        else:
            agent_row.append(f"{agent} ", style="grey50")
            
    central_content = Text.assemble(
        search_prompt, "\n\n",
        ("Code  ", "bright_blue"), agent_row
    )
    
    central_panel = Panel(
        Align.left(central_content),
        box=box.SQUARE,
        border_style="grey23",
        width=80,
        padding=(1, 2),
        style="on grey11"
    )
    
    # Shortcuts
    shortcuts = Text.assemble(
        ("tab", "shortcut.key"), (" agents  ", "shortcut.label"),
        ("ctrl+q", "shortcut.key"), (" commands", "shortcut.label")
    )
    
    # Tip
    if not tip_text:
        tip_text = f"Switch to {active_agent} agent to get suggestions for your code"
        
    tip = Text.assemble(
        ("● Tip ", "tip.bullet"),
        (tip_text, "tip.text")
    )
    
    # Build the full view
    full_view = Table.grid(expand=True)
    full_view.add_column(justify="center")
    full_view.add_row("\n" * 4)
    full_view.add_row(header)
    full_view.add_row("\n")
    full_view.add_row(Align.center(central_panel))
    full_view.add_row(Align.center(shortcuts))
    full_view.add_row("\n" * 2)
    full_view.add_row(Align.center(tip))
    
    return full_view

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
