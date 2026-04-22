#!/usr/bin/env python3
"""
OpenIssue CLI - Main command-line interface
Provides security scanning, issue posting, and CI/CD integration
"""
import json
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

try:
    import typer
    from typer import Typer, Option, Argument
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    typer = None

# Import our modules
from .dependency_scanner import DependencyScanner
from .sarif import generate_sarif, save_sarif
from .ai_fixer import generate_fix, get_quick_fix

# Also import the backend CLI for issue posting
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))
try:
    from cli.post_issue import post_issue_to_server, add_to_queue
except ImportError:
    post_issue_to_server = None
    add_to_queue = None

app = Typer(help="🛡️ OpenIssue CLI - AI-powered security scanner with ASCII art flair!") if typer else None
console = Console() if HAS_RICH else None


def scan_for_vulnerabilities(directory: Path, include_ai_fixes: bool = False) -> Dict[str, Any]:
    """
    Scan directory for security vulnerabilities
    
    Args:
        directory: Directory to scan
        include_ai_fixes: Whether to generate AI-powered fixes
    
    Returns:
        Scan results dictionary
    """
    scanner = DependencyScanner()
    
    if console:
        # ASCII art for scanning
        scan_art = """
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                       🔍 SECURITY SCAN INITIATED!                        ║
    ║                                                                          ║
    ║    """ + f"Scanning: {str(directory)[:59]:<59}" + """║
    ║                                                                          ║
    ╚══════════════════════════════════════════════════════════════════════════╝
        """
        console.print(scan_art, style="blue")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("🔍 Analyzing dependencies and code patterns...", total=None)
            results = scanner.scan_directory(directory)
            progress.update(task, description="✅ Vulnerability scan complete")
    else:
        print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                       🔍 SECURITY SCAN INITIATED                         ║
║                                                                          ║
║    Scanning for vulnerabilities...                                       ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
        """)
        results = scanner.scan_directory(directory)
        print("✅ Vulnerability scan complete")
    
    # Add AI fixes if requested
    if include_ai_fixes and results["vulnerabilities"]:
        if console:
            ai_art = """
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                       🤖 AI FIX GENERATION ACTIVE                        ║
    ║                                                                          ║
    ║    Generating intelligent fix suggestions using AI...                    ║
    ║                                                                          ║
    ╚══════════════════════════════════════════════════════════════════════════╝
            """
            console.print(ai_art, style="green")
        else:
            print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                       🤖 AI FIX GENERATION ACTIVE                        ║
║                                                                          ║
║    Generating intelligent fix suggestions using AI...                    ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
            """)
        
        for vuln in results["vulnerabilities"]:
            # Try AI fix first
            ai_fix = generate_fix(vuln)
            if ai_fix:
                vuln["ai_fix"] = ai_fix
            else:
                # Fallback to quick fix template
                quick_fix = get_quick_fix(vuln["type"])
                if quick_fix:
                    vuln["quick_fix"] = quick_fix
    
    # Add metadata
    results["scan_metadata"] = {
        "directory": str(directory.absolute()),
        "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "cli_version": "1.0.0",
        "ai_fixes_included": include_ai_fixes
    }
    
    return results


def print_ascii_banner():
    """Print ASCII art banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║   ██████╗ ██████╗ ███████╗███╗   ██╗██╗███████╗███████╗██╗   ██╗███████╗      ║
║  ██╔═══██╗██╔══██╗██╔════╝████╗  ██║██║██╔════╝██╔════╝██║   ██║██╔════╝      ║
║  ██║   ██║██████╔╝█████╗  ██╔██╗ ██║██║███████╗███████╗██║   ██║█████╗        ║
║  ██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║██║╚════██║╚════██║██║   ██║██╔══╝        ║
║  ╚██████╔╝██║     ███████╗██║ ╚████║██║███████║███████║╚██████╔╝███████╗      ║
║   ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝╚═╝╚══════╝╚══════╝ ╚═════╝ ╚══════╝      ║
║                                                                               ║
║                    🛡️  AI-Powered Security Scanner  🛡️                       ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
    return banner

def print_scan_results(results: Dict[str, Any], verbose: bool = False):
    """Print scan results to console"""
    
    total = results.get("total", 0)
    severity_counts = results.get("severity_counts", {})
    
    if not console:
        # Fallback to plain text with ASCII art
        print(print_ascii_banner())
        print(f"\n{'='*80}")
        print("                        SECURITY SCAN RESULTS")
        print(f"{'='*80}")
        
        # ASCII art for results
        if total == 0:
            print("""
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                                                                          ║
    ║    ✅ NO VULNERABILITIES FOUND!                                          ║
    ║                                                                          ║
    ║    🎉 Your code looks secure! Great job maintaining security standards.  ║
    ║                                                                          ║
    ╚══════════════════════════════════════════════════════════════════════════╝
            """)
        else:
            print(f"""
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                        VULNERABILITIES DETECTED                          ║
    ║                                                                          ║
    ║    Total Found: {total:>3}                                               ║
    ║                                                                          ║""")
            
            for severity, count in severity_counts.items():
                if count > 0:
                    icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(severity, "⚪")
                    print(f"    ║    {icon} {severity:<8}: {count:>3}                                               ║")
            
            print("    ║                                                                          ║")
            print("    ╚══════════════════════════════════════════════════════════════════════════╝")
        
        print(f"{'='*80}\n")
        
        if verbose and results.get("vulnerabilities"):
            print("📋 DETAILED VULNERABILITY REPORT")
            print("─" * 80)
            for i, vuln in enumerate(results["vulnerabilities"], 1):
                severity_icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(vuln["severity"], "⚪")
                print(f"\n{i:>2}. {severity_icon} {vuln['description']}")
                print(f"    📁 File: {vuln['file']}:{vuln['line']}")
                print(f"    ⚡ Severity: {vuln['severity']}")
                if vuln.get("recommendation"):
                    print(f"    🔧 Fix: {vuln['recommendation']}")
                if vuln.get("ai_fix"):
                    print(f"    🤖 AI Fix: {vuln['ai_fix'][:100]}...")
                print("    " + "─" * 76)
        return
    
    # Rich output
    console.print()
    console.print(print_ascii_banner(), style="cyan")
    
    # Summary panel with ASCII-style borders
    if total == 0:
        success_art = """
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                                                                          ║
    ║    🎉 [bold green]NO VULNERABILITIES FOUND![/bold green]                                          ║
    ║                                                                          ║
    ║    ✨ Your code looks secure! Great job maintaining security standards.  ║
    ║                                                                          ║
    ╚══════════════════════════════════════════════════════════════════════════╝
        """
        console.print(success_art)
    else:
        # Create vulnerability summary with ASCII art
        severity_text = []
        colors = {"CRITICAL": "red", "HIGH": "orange1", "MEDIUM": "yellow", "LOW": "green"}
        icons = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}
        
        vuln_summary = f"""
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                      [bold red]VULNERABILITIES DETECTED[/bold red]                                ║
    ║                                                                          ║
    ║    [bold]Total Found: {total:>3}[/bold]                                                           ║
    ║                                                                          ║"""
        
        for severity, count in severity_counts.items():
            if count > 0:
                color = colors.get(severity, "white")
                icon = icons.get(severity, "⚪")
                vuln_summary += f"\n    ║    {icon} [{color}]{severity:<8}: {count:>3}[/{color}]                                                                    ║"
        
        vuln_summary += """
    ║                                                                          ║
    ╚══════════════════════════════════════════════════════════════════════════╝
        """
        
        console.print(vuln_summary)
    
    # Detailed results table
    if verbose and results.get("vulnerabilities"):
        console.print("\n" + "─" * 80, style="dim")
        console.print("📋 [bold]DETAILED VULNERABILITY REPORT[/bold]", style="cyan")
        console.print("─" * 80, style="dim")
        
        table = Table(show_header=True, header_style="bold magenta", border_style="blue")
        table.add_column("ID", style="dim", width=4)
        table.add_column("Type", style="cyan", width=20)
        table.add_column("Severity", style="bold", width=10)
        table.add_column("File", style="blue", width=20)
        table.add_column("Description", style="white", width=40)
        
        for i, vuln in enumerate(results["vulnerabilities"], 1):
            severity_color = {"CRITICAL": "red", "HIGH": "orange1", "MEDIUM": "yellow", "LOW": "green"}.get(vuln["severity"], "white")
            severity_icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(vuln["severity"], "⚪")
            
            table.add_row(
                str(i),
                vuln["type"].replace("_", " ").title(),
                f"{severity_icon} [{severity_color}]{vuln['severity']}[/{severity_color}]",
                f"{vuln['file']}:{vuln['line']}",
                vuln["description"][:40] + "..." if len(vuln["description"]) > 40 else vuln["description"]
            )
        
        console.print(table)
        
        # Show AI fixes if available
        ai_fixes = [v for v in results["vulnerabilities"] if v.get("ai_fix") or v.get("quick_fix")]
        if ai_fixes:
            console.print("\n🤖 [bold]AI-POWERED FIX SUGGESTIONS[/bold]", style="green")
            console.print("─" * 80, style="dim")
            
            for i, vuln in enumerate(ai_fixes, 1):
                fix_text = vuln.get("ai_fix") or vuln.get("quick_fix", "")
                if fix_text:
                    console.print(f"\n[bold]{i}. {vuln['description']}[/bold]")
                    console.print(Panel(fix_text[:300] + "..." if len(fix_text) > 300 else fix_text, 
                                      title="🔧 Suggested Fix", border_style="green"))


if typer:
    @app.command()
    def scan(
        directory: Path = Argument(".", help="Directory to scan"),
        output: Optional[Path] = Option(None, "--output", "-o", help="Output file for JSON results"),
        sarif: Optional[Path] = Option(None, "--sarif", help="Output SARIF file for GitHub Security"),
        json_output: bool = Option(False, "--json", help="Output JSON to stdout"),
        verbose: bool = Option(False, "--verbose", "-v", help="Show detailed results"),
        ai_fixes: bool = Option(False, "--ai-fixes", help="Generate AI-powered fix suggestions"),
        fail_on: str = Option("critical", "--fail-on", help="Fail on severity level (critical, high, medium, low)"),
    ):
        """🔍 Scan directory for security vulnerabilities"""
        
        if not directory.exists():
            if console:
                console.print(f"❌ [red]Directory not found: {directory}[/red]")
            else:
                print(f"❌ Directory not found: {directory}")
            raise typer.Exit(1)
        
        # Run scan
        results = scan_for_vulnerabilities(directory, include_ai_fixes=ai_fixes)
        
        # Output JSON to stdout if requested
        if json_output:
            print(json.dumps(results, indent=2))
        else:
            # Print results to console
            print_scan_results(results, verbose=verbose)
        
        # Save JSON output file
        if output:
            output.parent.mkdir(parents=True, exist_ok=True)
            with open(output, 'w') as f:
                json.dump(results, f, indent=2)
            if console:
                console.print(f"📄 Results saved to: {output}")
            else:
                print(f"📄 Results saved to: {output}")
        
        # Generate SARIF for GitHub Security
        if sarif:
            sarif_data = generate_sarif(results, str(directory.absolute()))
            save_sarif(sarif_data, str(sarif))
            if console:
                console.print(f"📋 SARIF saved to: {sarif}")
            else:
                print(f"📋 SARIF saved to: {sarif}")
        
        # Check exit conditions
        severity_counts = results.get("severity_counts", {})
        fail_levels = {
            "critical": ["CRITICAL"],
            "high": ["CRITICAL", "HIGH"],
            "medium": ["CRITICAL", "HIGH", "MEDIUM"],
            "low": ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        }
        
        should_fail = any(
            severity_counts.get(level, 0) > 0 
            for level in fail_levels.get(fail_on.lower(), ["CRITICAL"])
        )
        
        if should_fail:
            fail_art = """
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                            ❌ BUILD FAILED                               ║
    ║                                                                          ║
    ║    Critical vulnerabilities detected! Please fix before proceeding.      ║
    ║                                                                          ║
    ╚══════════════════════════════════════════════════════════════════════════╝
            """
            if console:
                console.print(fail_art, style="red")
            else:
                print(fail_art)
            raise typer.Exit(1)
        
        success_art = """
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                           ✅ SCAN COMPLETED                              ║
    ║                                                                          ║
    ║    Security scan finished successfully! No critical issues found.        ║
    ║                                                                          ║
    ╚══════════════════════════════════════════════════════════════════════════╝
        """
        if console:
            console.print(success_art, style="green")
        else:
            print(success_art)

    @app.command()
    def post(
        title: str = Option(..., "--title", "-t", help="Issue title"),
        description: str = Option("", "--description", "-d", help="Issue description"),
        file: Optional[Path] = Option(None, "--file", "-f", help="Read issue from markdown file"),
        repo: Optional[str] = Option(None, "--repo", "-r", help="Repository (owner/repo)"),
        labels: Optional[str] = Option(None, "--labels", "-l", help="Comma-separated labels"),
        analyze: bool = Option(False, "--analyze", "-a", help="Analyze issue before creating"),
        server: Optional[str] = Option(None, "--server", help="OpenIssue server URL"),
    ):
        """📝 Post an issue to OpenIssue backend for triage"""
        
        if not post_issue_to_server:
            if console:
                console.print("❌ [red]Backend CLI not available. Check installation.[/red]")
            else:
                print("❌ Backend CLI not available. Check installation.")
            raise typer.Exit(1)
        
        # Read from file if specified
        if file:
            if not file.exists():
                if console:
                    console.print(f"❌ [red]File not found: {file}[/red]")
                else:
                    print(f"❌ File not found: {file}")
                raise typer.Exit(1)
            
            content = file.read_text()
            lines = content.strip().split("\n", 1)
            title = lines[0].lstrip("#").strip()
            description = lines[1].strip() if len(lines) > 1 else ""
        
        # Build issue payload
        issue = {"title": title, "description": description}
        if repo:
            issue["repository"] = repo
        if labels:
            issue["labels"] = [l.strip() for l in labels.split(",")]
        
        # Set server URL if provided
        if server:
            os.environ["OI_SERVER_URL"] = server
        
        if console:
            post_art = """
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                          📝 POSTING ISSUE                                ║
    ║                                                                          ║
    ║    """ + f"Title: {title[:63]:<63}" + """║
    ║                                                                          ║
    ╚══════════════════════════════════════════════════════════════════════════╝
            """
            console.print(post_art, style="blue")
        else:
            print(f"""
╔══════════════════════════════════════════════════════════════════════════╗
║                          📝 POSTING ISSUE                                ║
║                                                                          ║
║    Title: {title[:63]:<63}║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
            """)
        
        # Post to server
        try:
            result = post_issue_to_server(issue, analyze=analyze)
            
            if result is None:
                add_to_queue(issue)
                raise typer.Exit(1)
            
            if console:
                success_post_art = """
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                       ✅ ISSUE POSTED SUCCESSFULLY                       ║
    ║                                                                          ║
    ║    Your issue has been submitted to the OpenIssue backend.               ║
    ║                                                                          ║
    ╚══════════════════════════════════════════════════════════════════════════╝
                """
                console.print(success_post_art, style="green")
                if "id" in result:
                    console.print(f"    🆔 Issue ID: [bold]{result['id']}[/bold]")
            else:
                print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                       ✅ ISSUE POSTED SUCCESSFULLY                       ║
║                                                                          ║
║    Your issue has been submitted to the OpenIssue backend.               ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
                """)
                if "id" in result:
                    print(f"    🆔 Issue ID: {result['id']}")
                    
        except Exception as e:
            if console:
                console.print(f"❌ [red]Failed to post issue: {e}[/red]")
            else:
                print(f"❌ Failed to post issue: {e}")
            raise typer.Exit(1)

    @app.command()
    def version():
        """Show version information"""
        version_art = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║   ██████╗ ██████╗ ███████╗███╗   ██╗██╗███████╗███████╗██╗   ██╗███████╗      ║
║  ██╔═══██╗██╔══██╗██╔════╝████╗  ██║██║██╔════╝██╔════╝██║   ██║██╔════╝      ║
║  ██║   ██║██████╔╝█████╗  ██╔██╗ ██║██║███████╗███████╗██║   ██║█████╗        ║
║  ██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║██║╚════██║╚════██║██║   ██║██╔══╝        ║
║  ╚██████╔╝██║     ███████╗██║ ╚████║██║███████║███████║╚██████╔╝███████╗      ║
║   ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝╚═╝╚══════╝╚══════╝ ╚═════╝ ╚══════╝      ║
║                                                                               ║
║                           🛡️  Version 1.0.0  🛡️                              ║
║                    AI-Powered Security Vulnerability Scanner                  ║
║                                                                               ║
║  Features:                                                                    ║
║    🔍 Multi-language dependency scanning                                     ║
║    🤖 AI-powered fix suggestions                                             ║
║    📋 SARIF output for GitHub Security                                       ║
║    🚀 CI/CD ready with GitHub Actions                                        ║
║    📝 Issue management integration                                           ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
        """
        
        try:
            if console:
                console.print(version_art, style="cyan")
            else:
                print(version_art)
        except UnicodeEncodeError:
            # Fallback for Windows console encoding issues
            if console:
                console.print("[bold]OpenIssue CLI[/bold] v1.0.0")
                console.print("AI-powered security vulnerability scanner")
            else:
                print("OpenIssue CLI v1.0.0")
                print("AI-powered security vulnerability scanner")


def main_argparse():
    """Fallback CLI using argparse when Typer is not available"""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenIssue CLI - Security Scanner")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # scan command
    scan_parser = subparsers.add_parser("scan", help="Scan for vulnerabilities")
    scan_parser.add_argument("directory", nargs="?", default=".", help="Directory to scan")
    scan_parser.add_argument("--output", "-o", help="Output JSON file")
    scan_parser.add_argument("--sarif", help="Output SARIF file")
    scan_parser.add_argument("--json", action="store_true", help="Output JSON to stdout")
    scan_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    scan_parser.add_argument("--ai-fixes", action="store_true", help="Generate AI fixes")
    scan_parser.add_argument("--fail-on", default="critical", help="Fail on severity")
    
    # post command
    post_parser = subparsers.add_parser("post", help="Post an issue")
    post_parser.add_argument("--title", "-t", required=True, help="Issue title")
    post_parser.add_argument("--description", "-d", default="", help="Issue description")
    post_parser.add_argument("--file", "-f", help="Read from file")
    post_parser.add_argument("--repo", "-r", help="Repository")
    post_parser.add_argument("--analyze", "-a", action="store_true", help="Analyze first")
    
    # version command
    subparsers.add_parser("version", help="Show version")
    
    args = parser.parse_args()
    
    if args.command == "scan":
        directory = Path(args.directory)
        results = scan_for_vulnerabilities(directory, include_ai_fixes=args.ai_fixes)
        
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print_scan_results(results, verbose=args.verbose)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"📄 Results saved to: {args.output}")
        
        if args.sarif:
            sarif_data = generate_sarif(results, str(directory.absolute()))
            save_sarif(sarif_data, args.sarif)
            print(f"📋 SARIF saved to: {args.sarif}")
        
        # Check exit conditions
        severity_counts = results.get("severity_counts", {})
        fail_levels = {
            "critical": ["CRITICAL"],
            "high": ["CRITICAL", "HIGH"],
            "medium": ["CRITICAL", "HIGH", "MEDIUM"],
            "low": ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        }
        
        should_fail = any(
            severity_counts.get(level, 0) > 0 
            for level in fail_levels.get(args.fail_on.lower(), ["CRITICAL"])
        )
        
        if should_fail:
            print(f"❌ Build failed due to {args.fail_on.upper()} vulnerabilities")
            sys.exit(1)
    
    elif args.command == "post":
        if not post_issue_to_server:
            print("❌ Backend CLI not available")
            sys.exit(1)
        
        issue = {"title": args.title, "description": args.description}
        if args.repo:
            issue["repository"] = args.repo
        
        if args.file:
            content = Path(args.file).read_text()
            lines = content.strip().split("\n", 1)
            issue["title"] = lines[0].lstrip("#").strip()
            issue["description"] = lines[1].strip() if len(lines) > 1 else ""
        
        result = post_issue_to_server(issue, analyze=args.analyze)
        if result:
            print("✅ Issue posted successfully")
        else:
            add_to_queue(issue)
            sys.exit(1)
    
    elif args.command == "version":
        version_art = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║   ██████╗ ██████╗ ███████╗███╗   ██╗██╗███████╗███████╗██╗   ██╗███████╗      ║
║  ██╔═══██╗██╔══██╗██╔════╝████╗  ██║██║██╔════╝██╔════╝██║   ██║██╔════╝      ║
║  ██║   ██║██████╔╝█████╗  ██╔██╗ ██║██║███████╗███████╗██║   ██║█████╗        ║
║  ██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║██║╚════██║╚════██║██║   ██║██╔══╝        ║
║  ╚██████╔╝██║     ███████╗██║ ╚████║██║███████║███████║╚██████╔╝███████╗      ║
║   ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝╚═╝╚══════╝╚══════╝ ╚═════╝ ╚══════╝      ║
║                                                                               ║
║                           🛡️  Version 1.0.0  🛡️                              ║
║                    AI-Powered Security Vulnerability Scanner                  ║
╚═══════════════════════════════════════════════════════════════════════════════╝
        """
        print(version_art)
    
    else:
        parser.print_help()


def main():
    """Main entry point"""
    if typer and app:
        app()
    else:
        main_argparse()


if __name__ == "__main__":
    main()