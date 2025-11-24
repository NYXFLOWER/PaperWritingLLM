"""Command Line Interface for Writing Assistant"""

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich import print as rprint
from pathlib import Path
import sys

from .model_loader import QWenModelLoader
from .session_manager import SessionManager


console = Console()


class WritingAssistant:
    """Main Writing Assistant Application"""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the writing assistant"""
        self.config_path = config_path
        self.model_loader = None
        self.session_manager = None
        self.system_prompt = None
        self.running = False
        self.mode_name = None
        self.nuno_submode = None  # Track !outline or !proofread
        self.mode_config = None  # Store loaded mode config

    def initialize(self, username: str, custom_instructions: str = None):
        """Initialize the assistant with model and session"""
        console.print("\n[bold blue]Initializing Writing Assistant...[/bold blue]\n")

        # Initialize model loader
        console.print("[cyan]Loading model...[/cyan]")
        self.model_loader = QWenModelLoader(self.config_path)
        self.model_loader.load_model()

        # Display model and device info
        model_name = self.model_loader.model_config['name']
        device = self.model_loader.device
        console.print(f"[green]✓ Model loaded: {model_name}[/green]")
        console.print(f"[green]✓ Device: {device.upper()}[/green]")

        # Get system prompt
        self.system_prompt = self.model_loader.get_system_prompt(custom_instructions)

        # Initialize session manager
        self.session_manager = SessionManager(self.config_path)
        log_file = self.session_manager.start_session(username, custom_instructions)

        console.print(f"[green]✓ Session started for user: {username}[/green]")
        console.print(f"[dim]Log file: {log_file}[/dim]\n")

        self.running = True

    def run_interactive_session(self):
        """Run the interactive chat session"""
        # Check if a mode is being used
        mode_info = ""
        nuno_commands = ""

        if hasattr(self, 'mode_name') and self.mode_name:
            mode_info = f"\n[dim]Mode:[/dim] [yellow]{self.mode_name}[/yellow]"

            # Add nuno-specific commands if in nuno mode
            if self.mode_name == 'nuno-writing-style':
                nuno_commands = (
                    "\n[dim]Nuno Commands:[/dim]\n"
                    "  [yellow]!outline[/yellow]   - Paper outline drafting\n"
                    "  [yellow]!proofread[/yellow] - Writing improvement\n"
                )

        console.print(Panel.fit(
            "[bold cyan]Writing Assistant with Fine-Tuned Qwen2.5-7B[/bold cyan]\n\n"
            "I'm here to help you improve your writing with:\n"
            "  • Grammar and style corrections\n"
            "  • Paper outline drafting\n"
            "  • Academic writing refinement\n"
            "  • Clarity and conciseness improvements"
            + mode_info + "\n"
            + nuno_commands + "\n"
            "[dim]Interactive Commands:[/dim]\n"
            "  [cyan]/nuno[/cyan]  - Switch to Nuno writing style\n"
            "  [cyan]/help[/cyan]  - Show detailed help and tips\n"
            "  [cyan]/clear[/cyan] - Clear conversation history\n"
            "  [cyan]/quit[/cyan]  - End session and save\n\n"
            "[dim]Tip:[/dim] Paste your text or describe what you need help with!",
            title="✨ Welcome ✨",
            border_style="blue"
        ))

        while self.running:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold green]You[/bold green]")

                if not user_input.strip():
                    continue

                # Handle commands
                if user_input.lower() in ['/quit', '/exit']:
                    self.shutdown()
                    break
                elif user_input.lower() == '/clear':
                    self.session_manager.conversation_history = []
                    console.print("[yellow]Conversation history cleared[/yellow]")
                    continue
                elif user_input.lower() == '/help':
                    self.show_help()
                    continue
                elif user_input.lower() == '/nuno':
                    self.switch_mode('nuno-writing-style')
                    continue
                elif user_input.lower().startswith('/mode '):
                    mode_name = user_input[6:].strip()
                    self.switch_mode(mode_name)
                    continue
                # Handle Nuno submodes
                elif user_input.lower() == '!outline':
                    self.activate_nuno_submode('outline')
                    continue
                elif user_input.lower() == '!proofread':
                    self.activate_nuno_submode('proofread')
                    continue

                # Add user message to history
                self.session_manager.add_message("user", user_input)

                # Prepare messages for model
                messages = [
                    {"role": "system", "content": self.system_prompt}
                ]
                messages.extend(self.session_manager.get_conversation_history())

                # Generate response
                console.print("\n[bold cyan]Assistant[/bold cyan] [dim](thinking...)[/dim]", end="\r")
                response = self.model_loader.generate_response(messages)

                # Clear the "thinking" line and display response
                console.print(" " * 50, end="\r")
                console.print(f"[bold cyan]Assistant:[/bold cyan]\n")
                console.print(Markdown(response))

                # Add assistant message to history
                self.session_manager.add_message("assistant", response)

            except KeyboardInterrupt:
                console.print("\n\n[yellow]Interrupted by user[/yellow]")
                self.shutdown()
                break
            except Exception as e:
                console.print(f"\n[red]Error: {str(e)}[/red]")
                console.print("[yellow]Session will continue. Type /quit to exit.[/yellow]")

    def switch_mode(self, mode_name: str):
        """Switch to a different writing mode during the session"""
        mode_file = Path(f"prompts/{mode_name}.yaml")

        if not mode_file.exists():
            console.print(f"[red]✗ Mode not found: {mode_name}[/red]")
            console.print(f"[yellow]Available modes: nuno-writing-style, academic, creative, business[/yellow]")
            return

        try:
            # Load mode instructions
            import yaml
            with open(mode_file, 'r') as f:
                mode_config = yaml.safe_load(f)
                self.mode_config = mode_config  # Store for submode access
                mode_instructions = mode_config.get('custom_instructions', '')

            # Update system prompt
            self.system_prompt = self.model_loader.get_system_prompt(mode_instructions)
            self.mode_name = mode_name
            self.nuno_submode = None  # Reset submode

            # Clear conversation history to avoid confusion with different modes
            old_history_count = len(self.session_manager.conversation_history)
            self.session_manager.conversation_history = []

            console.print(f"\n[green]✓ Switched to mode: {mode_name}[/green]")
            console.print(f"[dim]Previous conversation history cleared ({old_history_count} messages)[/dim]")

            # Show mode-specific info
            if mode_name == 'nuno-writing-style':
                console.print("\n[cyan]Nuno Writing Style Mode Activated[/cyan]")
                console.print("Available commands:")
                console.print("  • [yellow]!outline[/yellow] - Paper outline drafting mode")
                console.print("  • [yellow]!proofread[/yellow] - Writing improvement mode")
                console.print("  • General writing help and questions\n")
            else:
                console.print(f"\n[cyan]{mode_name.title()} mode activated[/cyan]\n")

        except Exception as e:
            console.print(f"[red]Error loading mode: {str(e)}[/red]")

    def activate_nuno_submode(self, submode: str):
        """Activate outline or proofread submode in nuno-writing-style"""
        # Check if we're in nuno mode
        if self.mode_name != 'nuno-writing-style':
            console.print(f"[red]✗ Commands !outline and !proofread only work in nuno-writing-style mode[/red]")
            console.print("[yellow]Use /nuno to switch to nuno-writing-style mode first[/yellow]")
            return

        # Check if mode_config is loaded
        if not self.mode_config:
            console.print(f"[red]✗ Mode configuration not loaded[/red]")
            return

        # Get the submode prompt
        submode_prompt = self.mode_config.get(submode, '')
        if not submode_prompt:
            console.print(f"[red]✗ Submode not found: {submode}[/red]")
            return

        # Update system prompt with submode instructions
        self.system_prompt = self.model_loader.get_system_prompt(submode_prompt)
        self.nuno_submode = submode

        # Clear conversation history for clean slate
        old_history_count = len(self.session_manager.conversation_history)
        self.session_manager.conversation_history = []

        # Show activation message
        if submode == 'outline':
            console.print(f"\n[green]✓ Activated: OUTLINE MODE[/green]")
            console.print(f"[dim]Previous conversation history cleared ({old_history_count} messages)[/dim]")
            console.print("\n[cyan]📋 Paper Outline Drafting[/cyan]")
            console.print("Provide your project details, research question, and desired sections.")
            console.print("I'll help you create a comprehensive outline.\n")
        elif submode == 'proofread':
            console.print(f"\n[green]✓ Activated: PROOFREAD MODE[/green]")
            console.print(f"[dim]Previous conversation history cleared ({old_history_count} messages)[/dim]")
            console.print("\n[cyan]✏️  Writing Improvement & Proofreading[/cyan]")
            console.print("Paste your text and I'll improve grammar, style, and clarity.")
            console.print("You can request: 'grammar only', 'style only', or comprehensive revision.\n")

    def show_help(self):
        """Show help information"""
        help_text = """
        ## Available Commands

        **General Commands:**
        - `/help` - Show this help message
        - `/clear` - Clear the conversation history
        - `/nuno` - Switch to Nuno writing style mode
        - `/mode <name>` - Switch to a specific mode (academic, creative, business)
        - `/quit` or `/exit` - End the session and save

        **Nuno Mode Commands** (only in nuno-writing-style mode):
        - `!outline` - Activate paper outline drafting mode
        - `!proofread` - Activate writing improvement mode

        ## What I Can Do

        **For Nuno Writing Style Mode:**
        - **!outline**: Create comprehensive paper outlines with detailed section guidance
        - **!proofread**: Improve writing (grammar, style, clarity, conciseness)
        - General writing questions and academic writing guidance

        **For All Modes:**
        - Correct grammar and punctuation errors
        - Rephrase sentences for better clarity
        - Suggest improvements in style and tone
        - Maintain your original voice and intent

        ## How to Use

        **General Usage:**
        1. **Paste your text** - Simply paste what you want improved
        2. **Ask questions** - Ask why a change was made or request alternatives
        3. **Iterate** - Request multiple revisions until satisfied

        **Nuno Mode Workflow:**
        1. Use `/nuno` to enter Nuno writing style mode
        2. Use `!outline` for paper planning, or `!proofread` for text improvement
        3. Provide your content and receive specialized assistance

        ## Tips

        - **Be specific** about what you want help with
        - **Provide context** for better suggestions (audience, purpose, field)
        - **Ask for explanations** if something is unclear
        - **Use conversation history** - I remember our previous exchanges
        - **Focus requests** - In proofread mode, specify "grammar only" or "style only"

        ## Examples

        - "Please improve this paragraph: [paste text]"
        - "Help me outline a paper on proteomics with these sections..."
        - "Make this more concise: [paste text]"
        - "Check only grammar: [paste text]"
        """
        console.print(Panel(Markdown(help_text), title="📚 Help & Tips", border_style="cyan"))

    def shutdown(self):
        """Shutdown the assistant gracefully"""
        console.print("\n[yellow]Shutting down...[/yellow]")

        if self.session_manager:
            self.session_manager.end_session()
            console.print("[green]✓ Session saved[/green]")

        if self.model_loader:
            self.model_loader.unload_model()

        console.print("[bold green]Goodbye![/bold green]\n")
        self.running = False


@click.group()
def cli():
    """Writing Assistant - AI-powered writing help using QWen3-8b"""
    pass


@cli.command()
@click.option('--username', '-u', required=True, help='Username for this session')
@click.option('--instructions', '-i', help='Custom instructions for the assistant')
@click.option('--mode', '-m', help='Built-in mode (e.g., nuno-writing-style, academic, creative, business)')
@click.option('--config', '-c', default='config.yaml', help='Path to config file')
def start(username: str, instructions: str, mode: str, config: str):
    """Start an interactive writing assistant session"""
    # Check if config exists
    if not Path(config).exists():
        console.print(f"[red]Error: Config file not found: {config}[/red]")
        console.print("[yellow]Please create a config.yaml file first.[/yellow]")
        sys.exit(1)

    # Handle built-in mode
    mode_config_data = None
    if mode:
        mode_file = Path(f"prompts/{mode}.yaml")
        if not mode_file.exists():
            console.print(f"[red]Error: Mode file not found: {mode_file}[/red]")
            console.print(f"[yellow]Available modes: nuno-writing-style, academic, creative, business[/yellow]")
            sys.exit(1)

        # Load instructions from mode file
        import yaml
        with open(mode_file, 'r') as f:
            mode_config_data = yaml.safe_load(f)
            mode_instructions = mode_config_data.get('custom_instructions', '')

        # Mode takes precedence over -i flag
        if instructions:
            console.print(f"[yellow]Warning: --mode overrides --instructions flag[/yellow]")
        instructions = mode_instructions
        console.print(f"[cyan]Using mode: {mode}[/cyan]")

    assistant = WritingAssistant(config)
    if mode:
        assistant.mode_name = mode
        assistant.mode_config = mode_config_data  # Store for submode access
    assistant.initialize(username, instructions)
    assistant.run_interactive_session()


@cli.command()
@click.option('--username', '-u', required=True, help='Username to list sessions for')
@click.option('--config', '-c', default='config.yaml', help='Path to config file')
def list_sessions(username: str, config: str):
    """List all sessions for a user"""
    session_manager = SessionManager(config)
    sessions = session_manager.list_user_sessions(username)

    if not sessions:
        console.print(f"[yellow]No sessions found for user: {username}[/yellow]")
        return

    console.print(f"\n[bold]Sessions for {username}:[/bold]\n")
    for session in sessions:
        console.print(f"  • {session}")
    console.print()


@cli.command()
@click.option('--username', '-u', required=True, help='Username')
@click.option('--session-id', '-s', required=True, help='Session ID to view')
@click.option('--config', '-c', default='config.yaml', help='Path to config file')
def view_session(username: str, session_id: str, config: str):
    """View a previous session"""
    session_manager = SessionManager(config)

    try:
        # Remove 'session_' prefix if provided
        if session_id.startswith('session_'):
            session_id = session_id[8:]

        messages = session_manager.load_session_history(username, session_id)

        console.print(f"\n[bold]Session: {session_id}[/bold]")
        console.print(f"[dim]User: {username}[/dim]\n")
        console.print("=" * 60 + "\n")

        for msg in messages:
            role = msg['role'].upper()
            content = msg['content']
            timestamp = msg.get('timestamp', '')

            if role == 'USER':
                console.print(f"[bold green]{role}:[/bold green]")
            else:
                console.print(f"[bold cyan]{role}:[/bold cyan]")

            console.print(content)
            console.print(f"\n[dim]{timestamp}[/dim]")
            console.print("-" * 60 + "\n")

    except FileNotFoundError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


if __name__ == '__main__':
    cli()
