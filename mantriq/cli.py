import sys
import warnings
import os

# Suppress Pydantic V1 deprecation warnings for Python 3.14+
warnings.filterwarnings("ignore", message="Core Pydantic V1 functionality isn't compatible with Python 3.14 or greater")
# Also suppress general LangChain deprecation warnings for a cleaner TUI
warnings.filterwarnings("ignore", category=UserWarning, module="langchain_core")

from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import prompt
from rich.console import Console
import typer

from mantriq.agents import AGENT_MAP
from mantriq.utils.file_loader import load_file
from mantriq.utils.formatter import format_response, format_help, print_header, TUIDashboard
from mantriq.core.llm_engine import get_engine

# Initialize Typer app
app = typer.Typer()
console = Console()

class MantriqSession:
    def __init__(self):
        self.agents = ["Chat", "Explain", "Debug", "Review", "Optimize"]
        self.current_agent_idx = 0
        self.loaded_code = ""
        self.last_load = "None"
        self.history = []
        self.is_running = True
        self.should_redraw = False

    @property
    def active_agent(self):
        return self.agents[self.current_agent_idx]

    def cycle_agent(self, reverse=False):
        """Updates the agent index without redrawing the header."""
        if reverse:
            self.current_agent_idx = (self.current_agent_idx - 1) % len(self.agents)
        else:
            self.current_agent_idx = (self.current_agent_idx + 1) % len(self.agents)
        self.should_redraw = True

    def set_agent(self, name):
        """Sets the active agent by name."""
        if name in self.agents:
            self.current_agent_idx = self.agents.index(name)
            self.should_redraw = True

session_state = MantriqSession()

# Key Bindings
kb = KeyBindings()

def redraw_header():
    """Helper to redraw the TUI header smoothly."""
    engine = get_engine()
    dashboard = TUIDashboard(session_state.active_agent, engine.backend.capitalize())
    dashboard.last_load = session_state.last_load
    dashboard.response_history = session_state.history
    console.clear()
    console.print(dashboard.generate_dashboard())

@kb.add('tab')
def _(event):
    session_state.cycle_agent()

@kb.add('s-tab')
def _(event):
    session_state.cycle_agent(reverse=True)

@kb.add('c-e')
def _(event):
    session_state.set_agent("Explain")

@kb.add('c-d')
def _(event):
    session_state.set_agent("Debug")

@kb.add('c-r')
def _(event):
    session_state.set_agent("Review")

@kb.add('c-o')
def _(event):
    session_state.set_agent("Optimize")

@kb.add('c-q')
def _(event):
    session_state.is_running = False
    event.app.exit()

@kb.add('c-c')
def _(event):
    """Clear the current input buffer on Ctrl+C."""
    event.app.current_buffer.reset()

def handle_command(cmd_text):
    cmd_text = cmd_text.strip()
    if not cmd_text:
        return

    parts = cmd_text.split()
    cmd = parts[0].lower()
    args = parts[1:]

    if cmd == "exit":
        session_state.is_running = False
    elif cmd == "help":
        format_help()
    elif cmd == "clear":
        redraw_header()
    elif cmd == "agent":
        console.print(f"[bold green]Current Active Agent: {session_state.active_agent}[/bold green]")
    elif cmd == "refresh":
        redraw_header()
    elif cmd == "load":
        if not args:
            console.print("[red]Error: Please specify a file path.[/red]")
            return
        try:
            session_state.loaded_code = load_file(args[0])
            session_state.last_load = args[0]
            console.print(f"[green]Successfully loaded {args[0]}[/green]")
        except Exception as e:
            console.print(f"[red]Error loading file: {str(e)}[/red]")
    elif cmd == "paste":
        console.print("[yellow]Pasting mode enabled. Paste your code and press [bold]Meta+Enter[/bold] (Alt+Enter) or [bold]Esc, Enter[/bold] to finish.[/yellow]")
        try:
            # Use prompt-toolkit's prompt for better multi-line support
            content = prompt("paste > ", multiline=True)
            if content:
                session_state.loaded_code = content
                session_state.last_load = "Clipboard/Paste"
                console.print("[green]Code pasted and stored in context.[/green]")
            else:
                console.print("[yellow]Paste cancelled (empty content).[/yellow]")
        except Exception as e:
            console.print(f"[red]Error during paste: {str(e)}[/red]")
    elif cmd == "analyze":
        if not session_state.loaded_code:
            console.print("[red]Error: No code loaded. Use 'load' or 'paste' first.[/red]")
            return
        
        with console.status(f"[yellow]MANTRIQ {session_state.active_agent} is thinking...[/yellow]", spinner="dots"):
            try:
                agent_class = AGENT_MAP[session_state.active_agent]
                agent = agent_class()
                response = agent.process(session_state.loaded_code)
                session_state.history.append((session_state.active_agent, response))
                
                # Show typing animation for the response
                from rich.live import Live
                dashboard = TUIDashboard(session_state.active_agent, get_engine().backend.capitalize())
                dashboard.last_load = session_state.last_load
                dashboard.response_history = session_state.history
                dashboard.status_msg = "Completed"
                
                with Live(dashboard.generate_dashboard(), refresh_per_second=4) as live:
                    for i in range(1, len(response) + 1, 5):
                        # Update the last entry in history for a typing effect
                        session_state.history[-1] = (session_state.active_agent, response[:i])
                        dashboard.response_history = session_state.history
                        live.update(dashboard.generate_dashboard())
                        time.sleep(0.01)
                    
                    # Ensure full response is set
                    session_state.history[-1] = (session_state.active_agent, response)
                    dashboard.response_history = session_state.history
                    live.update(dashboard.generate_dashboard())
            except Exception as e:
                console.print(f"[red]Error during analysis: {str(e)}[/red]")
                if "RuntimeError" in str(type(e)):
                     console.print("[dim]Check the terminal logs for more details.[/dim]")
    else:
        # If it's not a recognized command, treat it as a chat query
        with console.status(f"[yellow]MANTRIQ is thinking...[/yellow]", spinner="dots"):
            try:
                agent_class = AGENT_MAP["Chat"]
                agent = agent_class()
                response = agent.process(cmd_text)
                session_state.history.append(("Chat", response))
                
                # Show typing animation for the response
                from rich.live import Live
                dashboard = TUIDashboard(session_state.active_agent, get_engine().backend.capitalize())
                dashboard.last_load = session_state.last_load
                dashboard.response_history = session_state.history
                dashboard.status_msg = "Completed"
                
                with Live(dashboard.generate_dashboard(), refresh_per_second=4) as live:
                    for i in range(1, len(response) + 1, 5):
                        session_state.history[-1] = ("Chat", response[:i])
                        dashboard.response_history = session_state.history
                        live.update(dashboard.generate_dashboard())
                        time.sleep(0.01)
                    
                    session_state.history[-1] = ("Chat", response)
                    dashboard.response_history = session_state.history
                    live.update(dashboard.generate_dashboard())
            except Exception as e:
                console.print(f"[red]Error during chat: {str(e)}[/red]")

@app.command()
def main():
    """MANTRIQ CLI - Your AI Coding Assistant"""
    engine = get_engine()
    
    # Check if there was an initialization error
    if engine.init_error:
        # The error is already printed by LLMEngine during init
        pass
    
    # Preliminary check for Ollama if that's the backend
    elif engine.backend == "ollama":
        try:
            import requests
            requests.get("http://localhost:11434/api/tags", timeout=1)
        except Exception:
            console.print("[bold red]Warning: Could not detect Ollama running on http://localhost:11434[/bold red]")
            console.print("[yellow]Please ensure Ollama is started ('ollama serve') before running analysis.[/yellow]\n")

    print_header(session_state.active_agent, engine.backend.capitalize())
    
    session = PromptSession(key_bindings=kb)
    
    while session_state.is_running:
        try:
            if session_state.should_redraw:
                redraw_header()
                session_state.should_redraw = False
                
            with patch_stdout():
                user_input = session.prompt("mantriq > ")
                if user_input.strip():
                    handle_command(user_input)
        except (KeyboardInterrupt, EOFError):
            break

    console.print("[bold cyan]Goodbye from MANTRIQ![/bold cyan]")

if __name__ == "__main__":
    app()
