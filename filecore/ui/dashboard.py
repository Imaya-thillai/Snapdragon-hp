"""
FileCore Dashboard UI — Rich terminal dashboard
Run: python filecore/ui/dashboard.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich import box
import time

console = Console()

def build_dashboard():
    from filecore.db.database import init_db, get_all_files
    from filecore.core.search import find_sensitive_files, find_recent_files
    from filecore.core.indexer import find_duplicates
    from filecore.hsal.hsal import hsal
    from filecore.ai.ai_runtime import ai_runtime
    import socket

    init_db()
    files = get_all_files()
    sensitive = find_sensitive_files()
    dupes = find_duplicates()
    hsal_s = hsal.get_status()
    ai_s = ai_runtime.get_status()

    try:
        socket.setdefaulttimeout(1)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        network_status = Text("● ONLINE", style="bold red")
    except Exception:
        network_status = Text("● OFFLINE / LOCAL MODE", style="bold green")

    # Status panel
    status_table = Table(box=box.SIMPLE, show_header=False)
    status_table.add_column("Key", style="bold cyan")
    status_table.add_column("Value", style="white")
    status_table.add_row("Files Indexed", str(len(files)))
    status_table.add_row("Sensitive Files", f"[yellow]{len(sensitive)}[/yellow]")
    status_table.add_row("Duplicate Groups", f"[yellow]{len(dupes)}[/yellow]")
    status_table.add_row("Network", network_status)
    status_table.add_row("AI Runtime", ai_s["mode"])
    status_table.add_row("AI Model", ai_s["model_name"])
    status_table.add_row("HSAL Mode", f"[yellow]{hsal_s['status']}[/yellow]")
    status_table.add_row("Device ID", hsal_s["device_id"][:16] + "...")

    # Recent files table
    recent = find_recent_files(5)
    recent_table = Table(box=box.SIMPLE, show_header=True)
    recent_table.add_column("Filename", style="white", max_width=30)
    recent_table.add_column("Modified", style="dim")
    recent_table.add_column("Class", justify="center")
    for f in recent:
        recent_table.add_row(
            f.get("filename", "")[:30],
            str(f.get("modified_at", ""))[:16],
            f.get("security_class", "PUBLIC")
        )

    layout = Layout()
    layout.split_column(
        Layout(Panel(
            Text("FileCore  •  Local • Private • Offline", style="bold green"),
            border_style="green"
        ), size=3),
        Layout(Panel(status_table, title="[bold cyan]System Status[/bold cyan]", border_style="cyan")),
        Layout(Panel(recent_table, title="[bold]Recent Files[/bold]", border_style="dim")),
        Layout(Panel(
            Text(f"⚠ {hsal_s['label']}", style="yellow"),
            title="Hardware Security",
            border_style="yellow"
        ), size=5),
    )
    return layout


if __name__ == "__main__":
    console.print("\n[bold green]FileCore Dashboard[/bold green]")
    console.print("[dim]Press Ctrl+C to exit[/dim]\n")
    try:
        with Live(build_dashboard(), refresh_per_second=0.5, screen=False) as live:
            while True:
                time.sleep(5)
                live.update(build_dashboard())
    except KeyboardInterrupt:
        console.print("\n[dim]FileCore dashboard closed.[/dim]")
