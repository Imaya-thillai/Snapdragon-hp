"""
FileCore — vault CLI
Usage:
  vault
  vault find <query>
  vault open <query>
  vault analyze <file>
  vault summarize <file>
  vault duplicates
  vault sensitive
  vault status
  vault index <path>
  vault audit
  vault --help
"""

import sys
import os

# Ensure the repo root is in sys.path so `filecore` package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from typing import Optional

app = typer.Typer(
    name="vault",
    help="FileCore — Local File Intelligence & Security Layer\n\nAll processing is done locally. No data leaves your machine.",
    add_completion=False
)
console = Console()

BANNER = """
[bold green]███████╗██╗██╗     ███████╗ ██████╗ ██████╗ ██████╗ ███████╗[/bold green]
[bold green]██╔════╝██║██║     ██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔════╝[/bold green]
[bold green]█████╗  ██║██║     █████╗  ██║     ██║   ██║██████╔╝█████╗  [/bold green]
[bold green]██╔══╝  ██║██║     ██╔══╝  ██║     ██║   ██║██╔══██╗██╔══╝  [/bold green]
[bold green]██║     ██║███████╗███████╗╚██████╗╚██████╔╝██║  ██║███████╗[/bold green]
[bold green]╚═╝     ╚═╝╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝[/bold green]
[dim]Local • Private • Offline[/dim]
"""


def print_banner():
    console.print(BANNER)


def print_file_table(files: list, title: str = "Results"):
    if not files:
        console.print(f"[yellow]No files found.[/yellow]")
        return

    table = Table(title=title, box=box.ROUNDED, show_header=True, header_style="bold cyan")
    table.add_column("Filename", style="white", max_width=30)
    table.add_column("Path", style="dim", max_width=45)
    table.add_column("Size", justify="right")
    table.add_column("Modified")
    table.add_column("Class", justify="center")
    table.add_column("Score", justify="right")

    for f in files:
        size = f.get("size_bytes", 0)
        size_str = f"{size // 1024} KB" if size else "—"
        table.add_row(
            str(f.get("filename", ""))[:30],
            str(f.get("path", ""))[:45],
            size_str,
            str(f.get("modified_at", ""))[:16],
            _classify_color(f.get("security_class", "PUBLIC")),
            str(f.get("relevance_score", "—"))
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(files)} results | [bold green]OFFLINE / LOCAL MODE[/bold green][/dim]")


def _classify_color(cls: str) -> str:
    colors = {
        "PUBLIC": "[green]PUBLIC[/green]",
        "PERSONAL": "[blue]PERSONAL[/blue]",
        "CONFIDENTIAL": "[yellow]CONFIDENTIAL[/yellow]",
        "HIGHLY_SENSITIVE": "[red]SENSITIVE[/red]",
        "SYSTEM": "[dim]SYSTEM[/dim]"
    }
    return colors.get(cls, cls)


@app.command(name="find")
def cmd_find(query: str = typer.Argument(..., help="Search query")):
    """Search for files on this computer."""
    from filecore.core.search import search
    from filecore.db.database import init_db
    init_db()
    console.print(f"\n[cyan]Searching for:[/cyan] [bold]{query}[/bold]")
    results = search(query)
    print_file_table(results, title=f"Results for: {query}")

    if results:
        console.print("\n[bold]Actions:[/bold]")
        console.print("  [cyan]vault open \"<filename>\"[/cyan] — open in File Explorer")
        console.print("  [cyan]vault summarize \"<full path>\"[/cyan] — summarize document locally")


@app.command(name="open")
def cmd_open(query: str = typer.Argument(..., help="File to open")):
    """Find and open a file in Windows File Explorer."""
    from filecore.core.search import search
    from filecore.core.policy import request_action
    from filecore.db.database import init_db
    init_db()

    results = search(query, limit=1)
    if not results:
        console.print(f"[red]No file found matching:[/red] {query}")
        return

    target = results[0]["path"]
    console.print(f"\n[cyan]Opening in File Explorer:[/cyan] {target}")
    result = request_action("open_folder", target, confirmed=True)
    console.print(f"[green]{result['message']}[/green]")


@app.command(name="analyze")
def cmd_analyze(file_path: str = typer.Argument(..., help="Full path to file")):
    """Run a local security scan on a file."""
    from filecore.core.security import scan_file
    result = scan_file(file_path)

    status_color = "red" if result["suspicious"] else "green"
    console.print(Panel(
        f"[bold]File:[/bold] {result['file']}\n"
        f"[bold]Security Class:[/bold] {result['security_class']}\n"
        f"[bold]Suspicious:[/bold] [{status_color}]{result['suspicious']}[/{status_color}]\n"
        f"[bold]Reasons:[/bold] {', '.join(result['reasons']) or 'None'}\n"
        f"[bold]Recommendation:[/bold] {result['recommendation']}\n\n"
        f"[dim]✓ Processed locally[/dim]",
        title="[bold cyan]FileCore Security Analysis[/bold cyan]",
        border_style=status_color
    ))


@app.command(name="summarize")
def cmd_summarize(file_path: str = typer.Argument(..., help="Full path to file")):
    """Summarize a document locally (no internet required)."""
    from filecore.core.document_intel import summarize_document
    console.print(f"\n[cyan]Summarizing (locally):[/cyan] {file_path}")
    result = summarize_document(file_path)

    if result["status"] == "error":
        console.print(f"[red]{result['message']}[/red]")
        return

    console.print(Panel(
        f"[bold]Summary:[/bold]\n{result['summary']}\n\n"
        f"[bold]Word Count:[/bold] {result['word_count']}\n"
        f"[bold]Keywords:[/bold] {', '.join(result['keywords'])}\n"
        f"[bold]Method:[/bold] {result['method']}\n\n"
        f"[dim]✓ Processed locally[/dim]",
        title=f"[bold cyan]Summary: {os.path.basename(file_path)}[/bold cyan]",
        border_style="cyan"
    ))


@app.command(name="duplicates")
def cmd_duplicates():
    """Find duplicate files on indexed paths."""
    from filecore.core.indexer import find_duplicates
    from filecore.db.database import init_db
    init_db()
    console.print("\n[cyan]Scanning for duplicates...[/cyan]")
    dupes = find_duplicates()

    if not dupes:
        console.print("[green]No duplicate files found.[/green]")
        return

    for group in dupes:
        console.print(Panel(
            "\n".join(f"  • {p}" for p in group["paths"]),
            title=f"[yellow]Hash: {group['hash'][:16]}... ({group['count']} copies)[/yellow]",
            border_style="yellow"
        ))

    console.print(f"\n[yellow]Found {len(dupes)} duplicate group(s).[/yellow]")
    console.print("[dim]Use [bold]vault delete \"<path>\"[/bold] to remove after manual review.[/dim]")


@app.command(name="sensitive")
def cmd_sensitive():
    """Show potentially sensitive files on indexed paths."""
    from filecore.core.search import find_sensitive_files
    from filecore.db.database import init_db
    init_db()
    console.print("\n[cyan]Scanning for sensitive files...[/cyan]")
    files = find_sensitive_files()
    print_file_table(files, title="Sensitive Files")


@app.command(name="index")
def cmd_index(path: str = typer.Argument(..., help="Directory path to index")):
    """Index a directory for local search."""
    from filecore.core.indexer import index_directory
    from filecore.db.database import init_db
    init_db()

    if not os.path.isdir(path):
        console.print(f"[red]Not a valid directory:[/red] {path}")
        return

    console.print(f"\n[cyan]Indexing:[/cyan] {path}")
    console.print("[dim]This may take a few moments for large directories...[/dim]")

    count = 0
    def progress(n, current_file):
        nonlocal count
        count = n
        if n % 50 == 0:
            console.print(f"  [dim]Indexed {n} files... ({os.path.basename(current_file)})[/dim]")

    result = index_directory(path, progress_callback=progress)
    console.print(f"\n[green]✓ Indexed {result['indexed']} files[/green] ({result['errors']} errors)")
    console.print(f"[dim]Now run [bold]vault find <query>[/bold] to search.[/dim]")


@app.command(name="audit")
def cmd_audit():
    """Show recent audit log entries."""
    from filecore.core.audit import get_audit_viewer
    events = get_audit_viewer(limit=20)
    if not events:
        console.print("[yellow]No audit events recorded yet.[/yellow]")
        return

    table = Table(title="Audit Log (Recent 20)", box=box.SIMPLE)
    table.add_column("Time", style="dim")
    table.add_column("Action", style="cyan")
    table.add_column("Target", max_width=40)
    table.add_column("Risk", justify="center")
    table.add_column("Result")

    risk_colors = {"LOW": "green", "MEDIUM": "yellow", "HIGH": "red", "CRITICAL": "bold red"}
    for e in events:
        risk = e.get("risk_level", "")
        color = risk_colors.get(risk, "white")
        table.add_row(
            str(e.get("timestamp", ""))[:19],
            str(e.get("action", "")),
            str(e.get("target", ""))[:40],
            f"[{color}]{risk}[/{color}]",
            str(e.get("result", ""))
        )
    console.print(table)


@app.command(name="status")
def cmd_status():
    """Show FileCore system status."""
    from filecore.hsal.hsal import hsal
    from filecore.ai.ai_runtime import ai_runtime
    from filecore.db.database import get_all_files, init_db
    init_db()

    files = get_all_files()
    hsal_status = hsal.get_status()
    ai_status = ai_runtime.get_status()

    import socket
    try:
        socket.setdefaulttimeout(1)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        network = "[red]ONLINE[/red] (prefer offline mode for privacy)"
    except Exception:
        network = "[bold green]OFFLINE / LOCAL MODE[/bold green]"

    console.print(Panel(
        f"[bold]Files Indexed:[/bold] {len(files)}\n"
        f"[bold]Network Status:[/bold] {network}\n"
        f"[bold]AI Runtime:[/bold] {ai_status['mode']}\n"
        f"[bold]AI Model:[/bold] {ai_status['model_name']}\n\n"
        f"[bold yellow]Hardware Security Module:[/bold yellow]\n"
        f"  Status: [yellow]{hsal_status['status']}[/yellow]\n"
        f"  Chip Concept: {hsal_status['chip_concept']}\n"
        f"  Device ID: {hsal_status['device_id'][:16]}...\n"
        f"  [dim]{hsal_status['label']}[/dim]\n",
        title="[bold cyan]FileCore System Status[/bold cyan]",
        border_style="cyan"
    ))


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """FileCore — Local File Intelligence & Security Layer"""
    if ctx.invoked_subcommand is None:
        print_banner()
        console.print(Panel(
            "[bold]Quick Commands:[/bold]\n\n"
            "  [cyan]vault find my project report[/cyan]\n"
            "  [cyan]vault open my resume[/cyan]\n"
            "  [cyan]vault summarize <path_to_pdf>[/cyan]\n"
            "  [cyan]vault analyze <path_to_file>[/cyan]\n"
            "  [cyan]vault duplicates[/cyan]\n"
            "  [cyan]vault sensitive[/cyan]\n"
            "  [cyan]vault index C:\\Users\\YourName\\Documents[/cyan]\n"
            "  [cyan]vault status[/cyan]\n"
            "  [cyan]vault audit[/cyan]\n"
            "  [cyan]vault --help[/cyan]",
            title="[bold green]FileCore vault[/bold green]",
            border_style="green"
        ))


if __name__ == "__main__":
    app()
