"""DevKitX CLI - Security-first developer utilities."""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import typer
    from rich.console import Console
    from rich.table import Table
    _CLI_AVAILABLE = True
except ImportError:
    _CLI_AVAILABLE = False

if _CLI_AVAILABLE:
    app = typer.Typer(
        name="devkitx",
        help="Security-first developer utilities for regulated environments.",
        no_args_is_help=True,
    )
    console = Console()


def check_cli_deps() -> None:
    """Check CLI dependencies are installed."""
    if not _CLI_AVAILABLE:
        print(
            "CLI requires additional dependencies.\n"
            "Install with: pip install 'devkitx[cli]'"
        )
        sys.exit(1)


# ============================================================================
# AUDIT COMMANDS
# ============================================================================

if _CLI_AVAILABLE:
    audit_app = typer.Typer(help="Security auditing commands")
    app.add_typer(audit_app, name="audit")

    @audit_app.command("secrets")
    def audit_secrets(
        path: Path = typer.Argument(Path("."), help="Path to scan"),
        output: str = typer.Option("table", help="Output format: table, json, sarif"),
    ) -> None:
        """Scan for hardcoded secrets in source code."""
        from ..security import SecretsScanner
        
        scanner = SecretsScanner()
        matches = list(scanner.scan_directory(path))
        
        if not matches:
            console.print("[green]✓ No secrets found[/green]")
            return
        
        if output == "json":
            import json
            print(json.dumps([{
                "type": m.secret_type,
                "file": m.file_path,
                "line": m.line_number,
                "severity": m.severity,
            } for m in matches], indent=2))
            return
        
        # Table output
        table = Table(title=f"Secrets Found: {len(matches)}")
        table.add_column("Severity", style="bold")
        table.add_column("Type")
        table.add_column("File")
        table.add_column("Line")
        
        severity_colors = {
            "critical": "red",
            "high": "yellow",
            "medium": "blue",
            "low": "dim",
        }
        
        for match in sorted(matches, key=lambda m: (
            {"critical": 0, "high": 1, "medium": 2, "low": 3}[m.severity],
            m.file_path,
        )):
            color = severity_colors.get(match.severity, "white")
            table.add_row(
                f"[{color}]{match.severity.upper()}[/{color}]",
                match.secret_type,
                match.file_path,
                str(match.line_number),
            )
        
        console.print(table)
        sys.exit(1)  # Exit with error if secrets found

    @audit_app.command("pii")
    def audit_pii(
        path: Path = typer.Argument(Path("."), help="Path to scan"),
    ) -> None:
        """Scan for PII (personally identifiable information)."""
        from ..compliance import PIIDetector
        
        detector = PIIDetector()
        matches = list(detector.scan_directory(path))
        
        if not matches:
            console.print("[green]✓ No PII found[/green]")
            return
        
        table = Table(title=f"PII Found: {len(matches)}")
        table.add_column("Type")
        table.add_column("Value (Redacted)")
        table.add_column("File")
        table.add_column("Line")
        
        for match in matches[:100]:  # Limit output
            table.add_row(
                match.pii_type,
                match.redacted,
                match.file_path,
                str(match.line_number),
            )
        
        if len(matches) > 100:
            console.print(f"[dim]... and {len(matches) - 100} more[/dim]")
        
        console.print(table)

    @audit_app.command("deps")
    def audit_deps(
        path: Path = typer.Argument(Path("."), help="Project path"),
    ) -> None:
        """Check dependencies for known vulnerabilities."""
        import subprocess
        
        console.print("[bold]Checking dependencies for vulnerabilities...[/bold]\n")
        
        # Try pip-audit first
        try:
            result = subprocess.run(
                ["pip-audit", "--strict"],
                cwd=path,
                capture_output=True,
                text=True,
            )
            print(result.stdout)
            if result.returncode != 0:
                print(result.stderr)
                sys.exit(1)
        except FileNotFoundError:
            console.print(
                "[yellow]pip-audit not found. Install with: pip install pip-audit[/yellow]"
            )
            sys.exit(1)


# ============================================================================
# JSON COMMANDS
# ============================================================================

if _CLI_AVAILABLE:
    json_app = typer.Typer(help="JSON utilities")
    app.add_typer(json_app, name="json")

    @json_app.command("flatten")
    def json_flatten(
        path: Path = typer.Argument(..., help="JSON file to flatten"),
    ) -> None:
        """Flatten nested JSON to dot notation."""
        import json
        from ..utils.json_utils import flatten_json
        
        data = json.loads(path.read_text())
        flat = flatten_json(data)
        print(json.dumps(flat, indent=2))

    @json_app.command("diff")
    def json_diff(
        file1: Path = typer.Argument(..., help="First JSON file"),
        file2: Path = typer.Argument(..., help="Second JSON file"),
    ) -> None:
        """Show differences between two JSON files."""
        import json
        
        data1 = json.loads(file1.read_text())
        data2 = json.loads(file2.read_text())
        
        def diff_dict(d1: dict, d2: dict, path: str = "") -> None:
            all_keys = set(d1.keys()) | set(d2.keys())
            
            for key in sorted(all_keys):
                current_path = f"{path}.{key}" if path else key
                
                if key not in d1:
                    console.print(f"[green]+ {current_path}: {d2[key]}[/green]")
                elif key not in d2:
                    console.print(f"[red]- {current_path}: {d1[key]}[/red]")
                elif isinstance(d1[key], dict) and isinstance(d2[key], dict):
                    diff_dict(d1[key], d2[key], current_path)
                elif d1[key] != d2[key]:
                    console.print(f"[red]- {current_path}: {d1[key]}[/red]")
                    console.print(f"[green]+ {current_path}: {d2[key]}[/green]")
        
        diff_dict(data1, data2)


# ============================================================================
# STRING COMMANDS
# ============================================================================

if _CLI_AVAILABLE:
    string_app = typer.Typer(help="String utilities")
    app.add_typer(string_app, name="string")

    @string_app.command("convert")
    def string_convert(
        text: str = typer.Argument(..., help="Text to convert"),
        to: str = typer.Option(..., "--to", help="Target case: snake, camel, pascal, kebab"),
    ) -> None:
        """Convert string between case formats."""
        from ..utils import string_utils
        
        converters = {
            "snake": string_utils.to_snake_case,
            "camel": string_utils.to_camel_case,
            "pascal": string_utils.to_pascal_case,
            "kebab": string_utils.to_kebab_case,
        }
        
        if to not in converters:
            console.print(f"[red]Unknown case: {to}[/red]")
            sys.exit(1)
        
        print(converters[to](text))


# ============================================================================
# INIT COMMAND
# ============================================================================

if _CLI_AVAILABLE:
    @app.command()
    def init(
        name: str = typer.Argument(..., help="Project name"),
        template: str = typer.Option("basic", help="Template: basic, fastapi, django"),
    ) -> None:
        """Initialize a new project with secure defaults."""
        path = Path(name)
        if path.exists():
            console.print(f"[red]Directory {name} already exists[/red]")
            sys.exit(1)
        
        # Create basic project structure
        path.mkdir()
        
        # Create basic files
        (path / "README.md").write_text(f"# {name}\n\nA secure Python project created with DevKitX.\n")
        (path / ".gitignore").write_text("""
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Secrets
*.key
*.pem
secrets.json
.secrets
""".strip())
        
        console.print(f"[green]✓ Created project: {name}[/green]")
        console.print(f"\nNext steps:")
        console.print(f"  cd {name}")
        console.print(f"  python -m venv .venv")
        console.print(f"  source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate")
        console.print(f"  pip install devkitx[all]")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main() -> None:
    """CLI entry point."""
    check_cli_deps()
    app()


if __name__ == "__main__":
    main()