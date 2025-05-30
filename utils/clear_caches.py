#!/usr/bin/env python3
import os
import shutil
from time import sleep
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn

console = Console()

def human_readable_size(size_bytes):
    """Convert bytes into KB, MB nicely."""
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"

def clear_pycache_dirs(root_dir="."):
    console.print("\n[bold magenta]🧹 Clearing all __pycache__ folders...[/bold magenta]\n")
    deleted_dirs = 0
    deleted_files = 0
    total_size = 0
    found_paths = []

    # First, collect all __pycache__ paths
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for dirname in dirnames:
            if dirname == "__pycache__":
                full_path = os.path.join(dirpath, dirname)
                found_paths.append(full_path)

    total = len(found_paths)

    if total == 0:
        console.print("\n[bold green]🎯 No __pycache__ folders found. Project is clean![/bold green]")
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("[cyan]Clearing caches...", total=total)

        for full_path in found_paths:
            try:
                # Count files and their total size
                file_count = 0
                folder_size = 0
                for root, dirs, files in os.walk(full_path):
                    file_count += len(files)
                    for file in files:
                        file_path = os.path.join(root, file)
                        if os.path.isfile(file_path):
                            folder_size += os.path.getsize(file_path)

                deleted_files += file_count
                total_size += folder_size
                shutil.rmtree(full_path)
                console.print(f"[green]✅ Deleted: {full_path} ({file_count} file(s), {human_readable_size(folder_size)})[/green]")
                deleted_dirs += 1
            except Exception as e:
                console.print(f"[red]❌ Failed to delete {full_path}: {e}[/red]")
            progress.update(task, advance=1)
            sleep(0.1)  # Smooth UX animation

    console.print(f"\n[bold green]✅ Done! Cleared {deleted_dirs} __pycache__ folder(s), {deleted_files} file(s), and freed {human_readable_size(total_size)}![/bold green]")

if __name__ == "__main__":
    clear_pycache_dirs(".")
