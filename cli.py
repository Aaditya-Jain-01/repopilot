import os
import difflib
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from analyzer import audit_code, generate_patch, generate_unit_tests

console = Console()

@click.group()
def main():
    """RepoPilot: Autonomous PR Audit & Self-Healing Agent powered by BharatCode."""
    pass

@main.command()
@click.argument("file_path", type=click.Path(exists=True))
def scan(file_path):
    """Scan a target code file for security flaws, bugs, and anti-patterns."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    console.print(Panel(f"[bold cyan]RepoPilot Security & Logic Scanner[/bold cyan]\nTarget: [yellow]{file_path}[/yellow]", expand=False))
    
    with console.status("[bold green]Running deep inference audit via BharatCode API...[/bold green]", spinner="dots"):
        result = audit_code(os.path.basename(file_path), content)

    issues = result.get("issues", [])
    if not issues:
        console.print("[bold green]✔ No critical vulnerabilities found.[/bold green]")
        return

    table = Table(title="Detected Flaws & Recommendations", show_header=True, header_style="bold magenta")
    table.add_column("Line", style="dim", width=8)
    table.add_column("Severity", width=12)
    table.add_column("Issue", width=30)
    table.add_column("Recommendation", style="green")

    for item in issues:
        sev = item.get("severity", "INFO").upper()
        if sev == "CRITICAL":
            sev_styled = "[bold red]CRITICAL[/bold red]"
        elif sev == "WARNING":
            sev_styled = "[bold yellow]WARNING[/bold yellow]"
        else:
            sev_styled = "[bold blue]INFO[/bold blue]"

        table.add_row(
            str(item.get("line", "—")),
            sev_styled,
            item.get("title", "Unknown"),
            item.get("recommendation", "")
        )

    console.print(table)

@main.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--apply", is_flag=True, help="Directly overwrite the target file with the patch.")
def patch(file_path, apply):
    """Generate and inspect an autonomous patch to fix all issues in the target file."""
    with open(file_path, "r", encoding="utf-8") as f:
        original_code = f.read()

    console.print(Panel(f"[bold cyan]RepoPilot Auto-Patcher[/bold cyan]\nTarget: [yellow]{file_path}[/yellow]", expand=False))

    with console.status("[bold green]Synthesizing clean patch...[/bold green]", spinner="dots"):
        fixed_code = generate_patch(os.path.basename(file_path), original_code)

    # Generate unified diff
    diff = list(difflib.unified_diff(
        original_code.splitlines(keepends=True),
        fixed_code.splitlines(keepends=True),
        fromfile=f"a/{file_path}",
        tofile=f"b/{file_path}"
    ))

    if not diff:
        console.print("[green]Code already optimal. No patch required.[/green]")
        return

    diff_text = "".join(diff)
    syntax = Syntax(diff_text, "diff", theme="monokai", line_numbers=False)
    console.print(Panel(syntax, title="Suggested Unified Patch (.diff)", expand=False))

    if apply or click.confirm("Apply this patch directly to the file?"):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(fixed_code)
        console.print(f"[bold green]✔ Successfully applied patch to {file_path}[/bold green]")
    else:
        patch_file = f"{file_path}.patch"
        with open(patch_file, "w", encoding="utf-8") as f:
            f.write(diff_text)
        console.print(f"[yellow]Patch saved as {patch_file}. Run `git apply {patch_file}` when ready.[/yellow]")

@main.command()
@click.argument("file_path", type=click.Path(exists=True))
def gentest(file_path):
    """Autonomously generate a comprehensive pytest test suite for the file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    console.print(Panel(f"[bold cyan]RepoPilot Test Suite Generator[/bold cyan]\nTarget: [yellow]{file_path}[/yellow]", expand=False))

    with console.status("[bold green]Generating unit tests and edge cases...[/bold green]", spinner="dots"):
        tests = generate_unit_tests(os.path.basename(file_path), content)

    test_file_name = f"test_{os.path.basename(file_path)}"
    with open(test_file_name, "w", encoding="utf-8") as f:
        f.write(tests)

    syntax = Syntax(tests, "python", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title=f"Generated {test_file_name}", expand=False))
    console.print(f"[bold green]✔ Test suite written to {test_file_name}. Run `pytest {test_file_name}` to verify.[/bold green]")

if __name__ == "__main__":
    main()