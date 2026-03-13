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
from datetime import datetime

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
            Layout(name="sidebar", size=32),
            Layout(name="body", ratio=1)
        )
        return layout

    def get_header(self) -> Panel:
        title = get_pixel_title("MANTRIQ", "bright_blue")
        time_text = Text(f"{datetime.now().strftime('%H:%M:%S')}", style="bright_yellow")
        
        # Header table for title and system info
        header_table = Table.grid(expand=True)
        header_table.add_column(justify="left", ratio=1)
        header_table.add_column(justify="center", ratio=2)
        header_table.add_column(justify="right", ratio=1)
        
        header_table.add_row(
            Text(f" V 1.0.0", style="grey37"),
            Align.center(title),
            time_text
        )
        
        return Panel(
            header_table,
            box=box.MINIMAL,
            border_style="blue",
            padding=(0, 1)
        )

    def get_sidebar(self) -> Panel:
        table = Table.grid(padding=1)
        table.add_column(style="cyan bold")
        table.add_column(style="white")
        
        table.add_row("Agent:", f"[bright_cyan]{self.active_agent}[/bright_cyan]")
        table.add_row("Backend:", f"[bright_yellow]{self.backend}[/bright_yellow]")
        table.add_row("Status:", f"[green]{self.status_msg}[/green]")
        table.add_row("Context:", f"[dim]{self.last_load}[/dim]")
        
        table.add_section()
        table.add_row("CPU Usage:", "[dim]Normal[/dim]")
        table.add_row("Mode:", "[dim]Standalone[/dim]")
        
        return Panel(
            Align.center(table),
            title="[bold blue]Dashboard[/bold blue]",
            border_style="blue",
            box=box.ROUNDED,
            padding=(1, 2)
        )

    def get_body(self) -> Panel:
        if not self.response_history:
            welcome_text = Text.assemble(
                ("\n\n" + "─" * 40 + "\n", "grey23"),
                ("MANTRIQ INTELLIGENCE\n", "bold bright_blue"),
                ("─" * 40 + "\n\n", "grey23"),
                ("Welcome, Developer.\n\n", "white"),
                ("MANTRIQ is a fully standalone AI coding assistant.\n", "grey50"),
                ("Type anything to chat or use ", "grey50"), ("'load'", "white"), (" for file analysis.\n\n", "grey50"),
                ("Quick Keys:\n", "white"),
                ("● ", "bright_blue"), ("TAB", "white"), ("    Cycle Agents\n", "grey50"),
                ("● ", "bright_blue"), ("CTRL+E", "white"), (" Explain Logic\n", "grey50"),
                ("● ", "bright_blue"), ("CTRL+D", "white"), (" Debug Error\n", "grey50"),
                ("● ", "bright_blue"), ("CTRL+Q", "white"), (" Exit Application\n", "grey50")
            )
            return Panel(
                Align.center(welcome_text),
                title="[bold blue]Output Terminal[/bold blue]",
                border_style="blue",
                box=box.ROUNDED,
                padding=(1, 2)
            )
        
        # Show last response
        last_agent, last_resp = self.response_history[-1]
        md = Markdown(last_resp)
        return Panel(
            md,
            title=f"[bold blue]{last_agent} Analysis[/bold blue]",
            border_style="blue",
            box=box.ROUNDED,
            padding=(1, 2)
        )

    def get_footer(self) -> Panel:
        shortcuts = Text.assemble(
            ("TAB", "bright_blue"), (" Next Agent  ", "grey50"),
            ("CTRL+Q", "bright_blue"), (" Quit  ", "grey50"),
            ("LOAD", "bright_blue"), (" Import  ", "grey50"),
            ("CLEAR", "bright_blue"), (" Wipe  ", "grey50"),
            ("HELP", "bright_blue"), (" Menu", "grey50")
        )
        return Panel(
            Align.center(shortcuts),
            box=box.MINIMAL,
            border_style="blue"
        )

    def generate_dashboard(self, height: int = 40) -> Layout:
        layout = self.make_layout()
        layout["header"].update(self.get_header())
        layout["sidebar"].update(self.get_sidebar())
        layout["body"].update(self.get_body())
        layout["footer"].update(self.get_footer())
        return layout

def print_header(active_agent: str, backend: str = "Local"):
    """Prints a fullscreen-style dashboard."""
    dashboard = TUIDashboard(active_agent, backend)
    console.clear()
    # We use the full height to ensure it looks like a fullscreen app
    console.print(dashboard.generate_dashboard())

def format_response(agent_name: str, response: str):
    """Fallback for direct printing."""
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
