from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.layout import Layout
from rich.live import Live
from rich.spinner import Spinner
from rich import box
import pyfiglet
import os
import time

console = Console()

def get_pixel_title(text: str, color: str = "bright_blue"):
    """Generates a pixel-style ASCII art title."""
    fig = pyfiglet.Figlet(font='small')
    ascii_art = fig.renderText(text)
    return Text(ascii_art, style=color)

class TUIDashboard:
    def __init__(self, active_agent: str, backend: str):
        self.active_agent = active_agent
        self.backend = backend
        self.response_history = []
        self.status_msg = "Ready"
        self.last_load = "None"

    def make_layout(self) -> Layout:
        layout = Layout()
        layout.split(
            Layout(name="header", size=8),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )
        layout["main"].split_row(
            Layout(name="sidebar", size=30),
            Layout(name="body", ratio=1)
        )
        return layout

    def get_header(self) -> Align:
        title = get_pixel_title("MANTRIQ", "bright_blue")
        return Align.center(title)

    def get_sidebar(self) -> Panel:
        table = Table.grid(padding=1)
        table.add_column(style="cyan bold")
        table.add_column(style="white")
        
        table.add_row("Agent:", f"[bright_cyan]{self.active_agent}[/bright_cyan]")
        table.add_row("Backend:", f"[bright_yellow]{self.backend}[/bright_yellow]")
        table.add_row("Status:", f"[green]{self.status_msg}[/green]")
        table.add_row("Loaded:", f"[dim]{self.last_load}[/dim]")
        
        return Panel(
            Align.center(table),
            title="[bold blue]Session[/bold blue]",
            border_style="blue",
            box=box.ROUNDED
        )

    def get_body(self) -> Panel:
        if not self.response_history:
            welcome_text = Text.assemble(
                ("\n\nWelcome to MANTRIQ Standalone CLI\n", "bold white"),
                ("Type anything to chat or use 'load <file>' to start analysis.\n\n", "grey50"),
                ("● ", "bright_blue"), ("TAB", "white"), (" to cycle agents\n", "grey50"),
                ("● ", "bright_blue"), ("Ctrl+Q", "white"), (" to exit\n", "grey50")
            )
            return Panel(
                Align.center(welcome_text),
                title="[bold blue]Console[/bold blue]",
                border_style="blue",
                box=box.ROUNDED
            )
        
        # Show last response
        last_agent, last_resp = self.response_history[-1]
        md = Markdown(last_resp)
        return Panel(
            md,
            title=f"[bold blue]{last_agent} Response[/bold blue]",
            border_style="blue",
            box=box.ROUNDED,
            padding=(1, 2)
        )

    def get_footer(self) -> Align:
        shortcuts = Text.assemble(
            ("TAB", "bright_blue"), (" Agents  ", "grey50"),
            ("CTRL+Q", "bright_blue"), (" Exit  ", "grey50"),
            ("LOAD", "bright_blue"), (" Context  ", "grey50"),
            ("HELP", "bright_blue"), (" Menu", "grey50")
        )
        return Align.center(shortcuts)

    def generate_dashboard(self) -> Layout:
        layout = self.make_layout()
        layout["header"].update(self.get_header())
        layout["sidebar"].update(self.get_sidebar())
        layout["body"].update(self.get_body())
        layout["footer"].update(self.get_footer())
        return layout

def print_header(active_agent: str, backend: str = "Local"):
    """Fallback for non-live updates."""
    dashboard = TUIDashboard(active_agent, backend)
    console.clear()
    console.print(dashboard.generate_dashboard())

def format_response(agent_name: str, response: str):
    """Formats the AI response with an 'animated' typing feel (simulated by live update)."""
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
    table.add_row("paste", "Paste multi-line code")
    table.add_row("analyze", "Run active agent")
    table.add_row("<text>", "Chat with MANTRIQ")
    table.add_row("clear", "Clear terminal")
    table.add_row("refresh", "Redraw Dashboard")
    table.add_row("help", "Show this menu")
    table.add_row("exit", "Exit MANTRIQ")
    console.print(table)
