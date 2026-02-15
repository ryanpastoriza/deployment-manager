#!/usr/bin/env python3
"""
Woosoo Deployment Manager - Standalone Version
Main application with TUI interface and CLI commands
"""

import os
import sys
import click
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import ConfigManager
from validators import SystemValidator
from services import ServiceManager, ServiceStatus
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()


class DeploymentManager:
    """Main deployment manager class - Standalone Version."""
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize deployment manager.
        
        Args:
            project_root: Project root directory. If None, uses current directory or WOOSOO_PROJECT_ROOT env var.
        """
        if project_root is None:
            # Check environment variable first
            env_root = os.getenv('WOOSOO_PROJECT_ROOT')
            if env_root:
                project_root = Path(env_root)
            else:
                # Default to current working directory
                project_root = Path.cwd()
        
        self.project_root = project_root
        self.config_manager = ConfigManager(self.project_root)
        self.validator = SystemValidator(self.project_root)
        
        # Initialize service manager with config (if config exists)
        try:
            config = self.config_manager.load_config()
            self.service_manager = ServiceManager(
                self.project_root,
                backend_dir=config.backend_dir,
                nginx_exe=config.nginx_exe,
                nginx_config=config.nginx_config
            )
        except FileNotFoundError:
            # Config doesn't exist yet, use defaults
            self.service_manager = ServiceManager(self.project_root)
    
    def show_header(self):
        """Show application header."""
        text = Text()
        text.append("WOOSOO DEPLOYMENT MANAGER", style="bold cyan")
        text.append(" v2.0.0", style="dim")
        console.print(Panel(text, box=box.DOUBLE, border_style="cyan"))
    
    def show_dashboard(self):
        """Show interactive dashboard."""
        self.show_header()
        
        # Services status
        console.print("\n[bold cyan]═══ Services Status ═══[/bold cyan]")
        services = self.service_manager.get_all_services_status()
        
        table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
        table.add_column("Service", style="cyan")
        table.add_column("Display Name", style="white")
        table.add_column("Status", justify="center")
        
        for svc in services:
            if svc.status == ServiceStatus.RUNNING:
                status_text = "[green]● Running[/green]"
            elif svc.status == ServiceStatus.STOPPED:
                status_text = "[yellow]○ Stopped[/yellow]"
            elif svc.status == ServiceStatus.PAUSED:
                status_text = "[yellow]⏸ Paused[/yellow]"
            else:
                status_text = "[dim]✕ Not Installed[/dim]"
            
            table.add_row(svc.name, svc.display_name, status_text)
        
        console.print(table)
        
        # Configuration summary
        try:
            config = self.config_manager.load_config()
            console.print("\n[bold cyan]═══ Configuration ═══[/bold cyan]")
            
            config_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
            config_table.add_column("Key", style="cyan")
            config_table.add_column("Value", style="white")
            
            summary = self.config_manager.get_config_summary()
            for key, value in summary.items():
                config_table.add_row(key, value)
            
            console.print(config_table)
        except FileNotFoundError as e:
            console.print(f"\n[yellow]⚠ Configuration not found: deployment.config.env[/yellow]")
            console.print(f"[dim]Copy deployment.config.env.template and fill in your values[/dim]")
        except Exception as e:
            console.print(f"\n[yellow]⚠ Configuration error: {e}[/yellow]")
    
    def run_pre_flight(self, verbose: bool = True):
        """Run pre-flight validation checks."""
        if verbose:
            console.print("\n[bold cyan]═══ Running Pre-Flight Checks ═══[/bold cyan]\n")
        
        results = self.validator.run_all_checks()
        
        if verbose:
            for result in results:
                icon = "✓" if result.passed else "✗"
                if result.passed:
                    color = "green"
                elif result.level.value == "critical":
                    color = "red"
                elif result.level.value == "high":
                    color = "yellow"
                else:
                    color = "blue"
                
                console.print(f"[{color}]{icon} {result.name}[/{color}] - {result.message}")
                if not result.passed and result.recommendation:
                    console.print(f"  [dim]→ {result.recommendation}[/dim]")
        
        summary = self.validator.get_summary()
        
        console.print()
        console.print(Panel(
            f"[bold]Total:[/bold] {summary['total']} | "
            f"[green]Passed:[/green] {summary['passed']} | "
            f"[red]Failed:[/red] {summary['failed']} | "
            f"[bold red]Critical:[/bold red] {summary['critical_failed']}",
            title="Validation Summary",
            border_style="cyan"
        ))
        
        if summary['can_proceed']:
            console.print("\n[bold green]✓ All critical checks passed - ready for deployment[/bold green]")
            return True
        else:
            console.print("\n[bold red]✗ Critical checks failed - cannot proceed[/bold red]")
            return False


# CLI Commands
@click.group(invoke_without_command=True)
@click.option('--project-root', type=click.Path(exists=True, file_okay=False, dir_okay=True),
              help='Project root directory (default: current directory or WOOSOO_PROJECT_ROOT env var)')
@click.pass_context
def cli(ctx, project_root):
    """Woosoo Deployment Manager - Comprehensive deployment tool.
    
    Environment Variables:
        WOOSOO_PROJECT_ROOT    Set default project root directory
    """
    # Store project root in context
    ctx.ensure_object(dict)
    ctx.obj['project_root'] = Path(project_root) if project_root else None
    
    if ctx.invoked_subcommand is None:
        # Show dashboard if no command specified
        manager = DeploymentManager(ctx.obj['project_root'])
        manager.show_dashboard()
        console.print("\n[dim]Use --help to see available commands[/dim]")


@cli.command()
@click.pass_context
def dashboard(ctx):
    """Show system dashboard."""
    manager = DeploymentManager(ctx.obj['project_root'])
    manager.show_dashboard()


@cli.command()
@click.option('--verbose', '-v', is_flag=True, help='Show detailed output')
@click.pass_context
def check(ctx, verbose):
    """Run pre-flight validation checks."""
    manager = DeploymentManager(ctx.obj['project_root'])
    manager.run_pre_flight(verbose=verbose)


@cli.command()
@click.argument('service', type=click.Choice(['reverb', 'queue', 'nginx', 'all']))
@click.pass_context
def start(ctx, service):
    """Start a service or all services."""
    manager = DeploymentManager(ctx.obj['project_root'])
    console.print(f"\n[cyan]Starting {service}...[/cyan]")
    
    if service == 'all':
        results = manager.service_manager.start_all()
        for svc, (success, msg) in results.items():
            icon = "✓" if success else "✗"
            color = "green" if success else "red"
            console.print(f"[{color}]{icon} {svc}: {msg}[/{color}]")
    else:
        success, msg = manager.service_manager.start_service(service)
        icon = "✓" if success else "✗"
        color = "green" if success else "red"
        console.print(f"[{color}]{icon} {msg}[/{color}]")


@cli.command()
@click.argument('service', type=click.Choice(['reverb', 'queue', 'nginx', 'all']))
@click.pass_context
def stop(ctx, service):
    """Stop a service or all services."""
    manager = DeploymentManager(ctx.obj['project_root'])
    console.print(f"\n[cyan]Stopping {service}...[/cyan]")
    
    if service == 'all':
        results = manager.service_manager.stop_all()
        for svc, (success, msg) in results.items():
            icon = "✓" if success else "✗"
            color = "green" if success else "red"
            console.print(f"[{color}]{icon} {svc}: {msg}[/{color}]")
    else:
        success, msg = manager.service_manager.stop_service(service)
        icon = "✓" if success else "✗"
        color = "green" if success else "red"
        console.print(f"[{color}]{icon} {msg}[/{color}]")


@cli.command()
@click.argument('service', type=click.Choice(['reverb', 'quote', 'nginx', 'all']))
@click.pass_context
def install(ctx, service):
    """Install a service or all services."""
    manager = DeploymentManager(ctx.obj['project_root'])
    console.print(f"\n[cyan]Installing {service}...[/cyan]")
    
    if service == 'all':
        results = manager.service_manager.install_all()
        for svc, (success, msg) in results.items():
            icon = "✓" if success else "✗"
            color = "green" if success else "red"
            console.print(f"[{color}]{icon} {svc}: {msg}[/{color}]")
    else:
        success, msg = manager.service_manager.install_service(service)
        icon = "✓" if success else "✗"
        color = "green" if success else "red"
        console.print(f"[{color}]{icon} {msg}[/{color}]")


@cli.command()
@click.argument('service', type=click.Choice(['reverb', 'queue', 'nginx', 'all']))
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
def uninstall(ctx, service, confirm):
    """Uninstall a service or all services."""
    if not confirm:
        if not click.confirm(f'Are you sure you want to uninstall {service}?'):
            return
    
    manager = DeploymentManager(ctx.obj['project_root'])
    console.print(f"\n[cyan]Uninstalling {service}...[/cyan]")
    
    if service == 'all':
        results = manager.service_manager.uninstall_all()
        for svc, (success, msg) in results.items():
            icon = "✓" if success else "✗"
            color = "green" if success else "red"
            console.print(f"[{color}]{icon} {svc}: {msg}[/{color}]")
    else:
        success, msg = manager.service_manager.uninstall_service(service)
        icon = "✓" if success else "✗"
        color = "green" if success else "red"
        console.print(f"[{color}]{icon} {msg}[/{color}]")


@cli.command()
@click.pass_context
def config(ctx):
    """Show current configuration."""
    manager = DeploymentManager(ctx.obj['project_root'])
    
    try:
        config = manager.config_manager.load_config()
        console.print("\n[bold cyan]Current Configuration:[/bold cyan]")
        
        table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="white")
        
        summary = manager.config_manager.get_config_summary()
        for key, value in summary.items():
            table.add_row(key, value)
        
        console.print(table)
        
        # Validate
        valid, errors = manager.config_manager.validate_config()
        if valid:
            console.print("\n[green]✓ Configuration is valid[/green]")
        else:
            console.print("\n[red]✗ Configuration has errors:[/red]")
            for error in errors:
                console.print(f"  [red]• {error}[/red]")
    
    except FileNotFoundError as e:
        console.print(f"[red]Configuration file not found: {e}[/red]")
        console.print(f"[yellow]→ Copy deployment.config.env.template to deployment.config.env[/yellow]")
    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")


@cli.command()
def version():
    """Show version information."""
    console.print("\n[bold cyan]Woosoo Deployment Manager[/bold cyan]")
    console.print("Version: 2.0.0 (Standalone)")
    console.print("Python: " + sys.version.split()[0])
    console.print()


if __name__ == '__main__':
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red bold]Error:[/red bold] {e}")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)
