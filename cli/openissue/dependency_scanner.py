"""
Dependency Vulnerability Scanner
Scans package.json, requirements.txt, pom.xml, etc. for vulnerable dependencies
"""
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional


class DependencyScanner:
    """Scans dependencies for known vulnerabilities"""
    
    def __init__(self):
        self.vulnerabilities = []
    
    def scan_directory(self, directory: Path) -> Dict[str, Any]:
        """Scan directory for dependency vulnerabilities"""
        all_vulns = []
        
        # Scan different package managers
        all_vulns.extend(self.scan_npm(directory))
        all_vulns.extend(self.scan_python(directory))
        all_vulns.extend(self.scan_maven(directory))
        all_vulns.extend(self.scan_composer(directory))
        
        # Count by severity
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for vuln in all_vulns:
            severity_counts[vuln["severity"]] += 1
        
        return {
            "vulnerabilities": all_vulns,
            "total": len(all_vulns),
            "severity_counts": severity_counts,
            "has_vulnerabilities": len(all_vulns) > 0
        }
    
    def scan_npm(self, directory: Path) -> List[Dict[str, Any]]:
        """Scan package.json using npm audit"""
        package_json = directory / "package.json"
        if not package_json.exists():
            return []
        
        try:
            result = subprocess.run(
                ["npm", "audit", "--json"],
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode in [0, 1]:  # 0 = no vulns, 1 = vulns found
                data = json.loads(result.stdout)
                return self._parse_npm_audit(data)
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            pass
        
        return []
    
    def _parse_npm_audit(self, audit_data: Dict) -> List[Dict[str, Any]]:
        """Parse npm audit JSON output"""
        vulns = []
        
        # npm audit v7+ format
        if "vulnerabilities" in audit_data:
            for pkg_name, vuln_data in audit_data.get("vulnerabilities", {}).items():
                severity = vuln_data.get("severity", "MEDIUM").upper()
                
                vulns.append({
                    "type": "vulnerable_dependency",
                    "severity": severity,
                    "description": f"Vulnerable npm package: {pkg_name}",
                    "package": pkg_name,
                    "current_version": vuln_data.get("range", "unknown"),
                    "fixed_version": vuln_data.get("fixAvailable", {}).get("version", "N/A") if isinstance(vuln_data.get("fixAvailable"), dict) else "N/A",
                    "cve": vuln_data.get("via", [{}])[0].get("cve", "N/A") if isinstance(vuln_data.get("via"), list) else "N/A",
                    "recommendation": f"Update {pkg_name} to a secure version",
                    "file": "package.json",
                    "line": 1,
                    "ecosystem": "npm"
                })
        
        return vulns
    
    def scan_python(self, directory: Path) -> List[Dict[str, Any]]:
        """Scan requirements.txt using pip-audit or safety"""
        requirements = directory / "requirements.txt"
        if not requirements.exists():
            return []
        
        # Try pip-audit first (better)
        try:
            result = subprocess.run(
                ["pip-audit", "--format", "json", "-r", str(requirements)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode in [0, 1]:
                data = json.loads(result.stdout)
                return self._parse_pip_audit(data)
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            pass
        
        # Fallback to manual CVE check (basic)
        return self._basic_python_check(requirements)
    
    def _parse_pip_audit(self, audit_data: Dict) -> List[Dict[str, Any]]:
        """Parse pip-audit JSON output"""
        vulns = []
        
        for vuln in audit_data.get("vulnerabilities", []):
            package = vuln.get("name", "unknown")
            version = vuln.get("version", "unknown")
            
            vulns.append({
                "type": "vulnerable_dependency",
                "severity": "HIGH",  # pip-audit doesn't provide severity
                "description": f"Vulnerable Python package: {package}",
                "package": package,
                "current_version": version,
                "fixed_version": vuln.get("fix_versions", ["N/A"])[0] if vuln.get("fix_versions") else "N/A",
                "cve": vuln.get("id", "N/A"),
                "recommendation": f"Update {package} to {vuln.get('fix_versions', ['latest'])[0]}",
                "file": "requirements.txt",
                "line": 1,
                "ecosystem": "pip"
            })
        
        return vulns
    
    def _basic_python_check(self, requirements_file: Path) -> List[Dict[str, Any]]:
        """Basic check for known vulnerable Python packages"""
        vulns = []
        
        # Known vulnerable versions (simplified - in production, use a database)
        known_vulns = {
            "django": {"<2.2.28": "CVE-2022-28346"},
            "flask": {"<2.0.3": "CVE-2023-30861"},
            "requests": {"<2.31.0": "CVE-2023-32681"},
            "pillow": {"<9.3.0": "CVE-2022-45198"},
        }
        
        try:
            content = requirements_file.read_text()
            for line_num, line in enumerate(content.split('\n'), 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Parse package==version
                if '==' in line:
                    pkg, version = line.split('==', 1)
                    pkg = pkg.strip().lower()
                    version = version.strip()
                    
                    if pkg in known_vulns:
                        vulns.append({
                            "type": "vulnerable_dependency",
                            "severity": "HIGH",
                            "description": f"Potentially vulnerable: {pkg}=={version}",
                            "package": pkg,
                            "current_version": version,
                            "fixed_version": "latest",
                            "cve": list(known_vulns[pkg].values())[0],
                            "recommendation": f"Update {pkg} to latest version",
                            "file": "requirements.txt",
                            "line": line_num,
                            "ecosystem": "pip"
                        })
        except Exception:
            pass
        
        return vulns
    
    def scan_maven(self, directory: Path) -> List[Dict[str, Any]]:
        """Scan pom.xml using OWASP dependency-check"""
        pom_xml = directory / "pom.xml"
        if not pom_xml.exists():
            return []
        
        # This would require OWASP dependency-check to be installed
        # For now, return empty (can be implemented later)
        return []
    
    def scan_composer(self, directory: Path) -> List[Dict[str, Any]]:
        """Scan composer.json for PHP dependencies"""
        composer_json = directory / "composer.json"
        if not composer_json.exists():
            return []
        
        try:
            result = subprocess.run(
                ["composer", "audit", "--format=json"],
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode in [0, 1]:
                data = json.loads(result.stdout)
                return self._parse_composer_audit(data)
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            pass
        
        return []
    
    def _parse_composer_audit(self, audit_data: Dict) -> List[Dict[str, Any]]:
        """Parse composer audit JSON output"""
        vulns = []
        
        for advisory in audit_data.get("advisories", {}).values():
            for vuln in advisory:
                vulns.append({
                    "type": "vulnerable_dependency",
                    "severity": "HIGH",
                    "description": f"Vulnerable PHP package: {vuln.get('packageName')}",
                    "package": vuln.get("packageName", "unknown"),
                    "current_version": vuln.get("affectedVersions", "unknown"),
                    "fixed_version": "See advisory",
                    "cve": vuln.get("cve", "N/A"),
                    "recommendation": vuln.get("title", "Update to secure version"),
                    "file": "composer.json",
                    "line": 1,
                    "ecosystem": "composer"
                })
        
        return vulns
