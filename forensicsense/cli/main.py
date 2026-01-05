"""
Main CLI entry point for ForensicSense

Provides command-line interface for all functionality
"""

import click
import asyncio
import yaml
import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import print as rprint

console = Console()


def load_config():
    """Load configuration from config.yaml"""
    config_path = Path("config.yaml")
    
    if not config_path.exists():
        # Look in parent directories
        for parent in [Path.cwd(), Path.cwd().parent]:
            config_candidate = parent / "config.yaml"
            if config_candidate.exists():
                config_path = config_candidate
                break
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        # Expand environment variables
        def expand_env_vars(d):
            if isinstance(d, dict):
                return {k: expand_env_vars(v) for k, v in d.items()}
            elif isinstance(d, str) and d.startswith('${') and d.endswith('}'):
                var_name = d[2:-1]
                return os.getenv(var_name, d)
            else:
                return d
        
        config = expand_env_vars(config)
        return config
    else:
        console.print("[yellow]Warning: config.yaml not found, using defaults[/yellow]")
        return {}


@click.group()
@click.version_option(version='1.0.0')
def main():
    """
    ForensicSense AI - Forensics-first Penetration Testing Platform
    
    "Know Before You Strike" - Complete target intelligence before exploitation
    """
    pass


@main.command()
@click.argument('target')
@click.option('--depth', type=click.Choice(['basic', 'standard', 'full', 'deep']), 
              default='standard', help='Profiling depth')
@click.option('--output', type=str, help='Output report file')
@click.option('--format', type=click.Choice(['json', 'html', 'md', 'pdf']), 
              default='json', help='Output format')
def profile(target, depth, output, format):
    """
    Profile a target (safe reconnaissance only)
    
    Examples:
        forensicsense profile example.com
        forensicsense profile 10.10.10.10 --depth deep
        forensicsense profile target.com --output report.pdf --format pdf
    """
    from ..intel.profiler import TargetProfiler
    from ..forensics.report_generator import ReportGenerator
    
    console.print(f"\n[bold cyan]ForensicSense AI - Target Profiling[/bold cyan]")
    console.print(f"[cyan]Target:[/cyan] {target}")
    console.print(f"[cyan]Depth:[/cyan] {depth}\n")
    
    # Load config
    config = load_config()
    
    # Create profiler
    profiler = TargetProfiler(config.get('forensics', {}))
    
    # Run profiling
    with console.status(f"[bold green]Profiling {target}...", spinner="dots"):
        profile_result = asyncio.run(profiler.profile_target(target, depth=depth))
    
    # Display results
    console.print("\n[bold green]✓ Profiling Complete[/bold green]\n")
    
    # Risk Assessment
    risk = profile_result.risk_assessment
    risk_level = risk.get('level', 'UNKNOWN')
    risk_score = risk.get('score', 0)
    
    # Color code risk level
    risk_colors = {
        'CRITICAL': 'bold red',
        'HIGH': 'red',
        'MEDIUM': 'yellow',
        'LOW': 'green',
        'MINIMAL': 'green'
    }
    risk_color = risk_colors.get(risk_level, 'white')
    
    console.print(f"[bold]Risk Assessment:[/bold]")
    console.print(f"  Level: [{risk_color}]{risk_level}[/{risk_color}]")
    console.print(f"  Score: {risk_score}/100\n")
    
    # Open Ports
    network_scan = profile_result.network_scan
    open_ports = network_scan.get('open_ports', [])
    
    if open_ports:
        console.print(f"[bold]Open Ports:[/bold] {len(open_ports)} found\n")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Port", style="cyan")
        table.add_column("Service", style="green")
        table.add_column("State")
        table.add_column("Banner", style="dim")
        
        for port in open_ports[:10]:  # Show first 10
            banner = port.get('banner', 'N/A')
            if banner and len(banner) > 50:
                banner = banner[:50] + "..."
            table.add_row(
                str(port['port']),
                port.get('service', 'unknown'),
                port['state'],
                banner
            )
        
        console.print(table)
        console.print()
    
    # Vulnerabilities
    vulnerabilities = profile_result.vulnerabilities
    if vulnerabilities:
        console.print(f"[bold]Vulnerabilities:[/bold] {len(vulnerabilities)} found\n")
        for vuln in vulnerabilities[:5]:  # Show first 5
            severity = vuln.get('severity', 'unknown').upper()
            console.print(f"  [{risk_colors.get(severity.upper(), 'white')}]●[/] {vuln.get('description', 'N/A')}")
        console.print()
    
    # Generate report
    if output or format != 'json':
        console.print(f"[bold]Generating report...[/bold]")
        report_gen = ReportGenerator()
        report_path = report_gen.generate_report(
            profile_result.to_dict(),
            format=format,
            output_file=output
        )
        console.print(f"[green]✓ Report saved to:[/green] {report_path}\n")
    else:
        # Just save JSON
        import json
        from datetime import datetime
        output_file = f"profile_{target.replace('/', '_').replace(':', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(profile_result.to_dict(), f, indent=2, default=str)
        console.print(f"[green]✓ Profile saved to:[/green] {output_file}\n")


@main.command()
@click.argument('target')
@click.option('--vuln', type=str, required=True, help='Vulnerability type (sqli, xss, rce, etc.)')
@click.option('--reason', type=str, required=True, help='Business justification/SOW reference')
@click.option('--interactive', is_flag=True, help='Interactive exploitation mode')
def exploit(target, vuln, reason, interactive):
    """
    Exploit a target (requires authorization)
    
    Examples:
        forensicsense exploit target.com --vuln sqli --reason "SOW #12345"
        forensicsense exploit 10.10.10.10 --vuln rce --reason "Client authorization" --interactive
    """
    from ..exploit.gated_exploiter import GatedExploiter
    
    console.print(f"\n[bold red]⚠️  ForensicSense AI - EXPLOITATION MODE ⚠️[/bold red]\n")
    console.print(f"[cyan]Target:[/cyan] {target}")
    console.print(f"[cyan]Vulnerability:[/cyan] {vuln}")
    console.print(f"[cyan]Reason:[/cyan] {reason}\n")
    
    # Load config
    config = load_config()
    
    # Create exploiter
    exploiter = GatedExploiter(config)
    
    # Request authorization
    console.print("[bold yellow]Requesting exploitation authorization...[/bold yellow]\n")
    
    auth_result = exploiter.request_access(target, reason)
    
    # Display gates
    console.print("[bold]Authorization Gates:[/bold]")
    for gate in auth_result.get('gates_passed', []):
        console.print(f"  [green]✓[/green] {gate}")
    
    for gate in auth_result.get('gates_failed', []):
        console.print(f"  [red]✗[/red] {gate}")
    
    console.print()
    
    if not auth_result['authorized']:
        console.print("[bold red]✗ Exploitation DENIED[/bold red]\n")
        console.print("Authorization failed. Cannot proceed with exploitation.")
        return
    
    console.print("[bold green]✓ Exploitation AUTHORIZED[/bold green]\n")
    
    # Proceed with exploitation
    auth_token = auth_result['auth_token']
    
    exploit_config = {
        'type': vuln,
        'interactive': interactive
    }
    
    result = exploiter.exploit(target, auth_token, exploit_config)
    
    if result.get('success'):
        console.print("[bold green]✓ Exploitation framework ready[/bold green]")
        console.print(f"[dim]{result.get('message', '')}[/dim]\n")
    else:
        console.print(f"[bold red]✗ Exploitation failed:[/bold red] {result.get('error', 'Unknown error')}\n")


@main.command()
@click.option('--format', type=click.Choice(['text', 'json']), default='text', help='Output format')
def audit(format):
    """
    Show audit log
    
    Examples:
        forensicsense audit
        forensicsense audit --format json
    """
    from ..utils.logging import AuditLogger
    
    console.print("\n[bold cyan]Audit Log[/bold cyan]\n")
    
    audit_logger = AuditLogger()
    
    # Verify integrity
    valid, message = audit_logger.verify_integrity()
    
    if valid:
        console.print(f"[green]✓ Audit log integrity verified[/green]")
        console.print(f"[dim]{message}[/dim]\n")
    else:
        console.print(f"[red]✗ Audit log integrity check FAILED[/red]")
        console.print(f"[red]{message}[/red]\n")
        return
    
    # Read and display log
    if audit_logger.audit_file.exists():
        import json
        
        entries = []
        with open(audit_logger.audit_file, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    entries.append(entry)
                except:
                    pass
        
        if format == 'json':
            console.print(json.dumps(entries, indent=2))
        else:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Timestamp", style="cyan")
            table.add_column("User", style="green")
            table.add_column("Target")
            table.add_column("Action", style="yellow")
            table.add_column("Result")
            
            for entry in entries[-20:]:  # Show last 20
                table.add_row(
                    entry.get('timestamp', '')[:19],
                    entry.get('user', ''),
                    entry.get('target', ''),
                    entry.get('action', ''),
                    entry.get('result', '')
                )
            
            console.print(table)
    else:
        console.print("[yellow]No audit log entries found[/yellow]")
    
    console.print()


@main.command()
@click.option('--api-token', type=str, help='HTB API token')
def htb_list(api_token):
    """
    List Hack The Box machines
    
    Examples:
        forensicsense htb-list
        forensicsense htb-list --api-token YOUR_TOKEN
    """
    from ..integrations.hackthebox import HTBIntegration
    
    console.print("\n[bold cyan]Hack The Box - Active Machines[/bold cyan]\n")
    
    # Get token from env if not provided
    if not api_token:
        api_token = os.getenv('HTB_API_TOKEN')
    
    if not api_token:
        console.print("[red]Error: HTB API token required[/red]")
        console.print("Set HTB_API_TOKEN environment variable or use --api-token")
        return
    
    htb = HTBIntegration(api_token)
    
    with console.status("[bold green]Fetching HTB machines...", spinner="dots"):
        machines = asyncio.run(htb.api.list_machines())
    
    if machines:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan")
        table.add_column("OS", style="green")
        table.add_column("Difficulty")
        table.add_column("IP")
        
        for machine in machines[:20]:  # Show first 20
            table.add_row(
                machine.get('name', 'Unknown'),
                machine.get('os', 'Unknown'),
                machine.get('difficulty', 'Unknown'),
                machine.get('ip', 'N/A')
            )
        
        console.print(table)
        console.print()
    else:
        console.print("[yellow]No machines found or API error[/yellow]\n")


@main.command()
@click.argument('setting', required=False)
@click.argument('value', required=False)
def config(setting, value):
    """
    View or modify configuration
    
    Examples:
        forensicsense config
        forensicsense config exploitation.enabled true
    """
    console.print("\n[bold cyan]ForensicSense Configuration[/bold cyan]\n")
    
    config_data = load_config()
    
    if not setting:
        # Display all config
        import json
        console.print(json.dumps(config_data, indent=2))
    elif not value:
        # Display specific setting
        keys = setting.split('.')
        current = config_data
        for key in keys:
            current = current.get(key, {})
        console.print(f"{setting}: {current}")
    else:
        # Modify setting (would need to implement config writing)
        console.print(f"[yellow]Config modification not yet implemented[/yellow]")
        console.print(f"Please edit config.yaml manually to set {setting}={value}")
    
    console.print()


if __name__ == '__main__':
    main()
