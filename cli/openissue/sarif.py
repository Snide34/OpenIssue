"""
SARIF (Static Analysis Results Interchange Format) Output
For GitHub Security Tab integration
"""
import json
from typing import List, Dict, Any
from datetime import datetime


def generate_sarif(scan_results: Dict[str, Any], repo_path: str) -> Dict[str, Any]:
    """
    Generate SARIF format output for GitHub Security tab
    Spec: https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/sarif-support-for-code-scanning
    """
    
    rules = []
    results = []
    
    # Group vulnerabilities by type
    vuln_types = {}
    for vuln in scan_results.get("vulnerabilities", []):
        vuln_type = vuln["type"]
        if vuln_type not in vuln_types:
            vuln_types[vuln_type] = {
                "id": vuln_type,
                "name": vuln["description"],
                "shortDescription": {"text": vuln["description"]},
                "fullDescription": {"text": vuln["description"]},
                "help": {
                    "text": vuln.get("recommendation", "Fix this vulnerability"),
                    "markdown": f"**Recommendation:** {vuln.get('recommendation', 'Fix this vulnerability')}"
                },
                "defaultConfiguration": {
                    "level": severity_to_level(vuln["severity"])
                },
                "properties": {
                    "tags": ["security", vuln["severity"].lower()],
                    "precision": "high"
                }
            }
            rules.append(vuln_types[vuln_type])
    
    # Create results
    for vuln in scan_results.get("vulnerabilities", []):
        result = {
            "ruleId": vuln["type"],
            "level": severity_to_level(vuln["severity"]),
            "message": {
                "text": f"{vuln['description']}: {vuln.get('matched', '')}"
            },
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {
                        "uri": vuln["file"].replace("\\", "/"),
                        "uriBaseId": "%SRCROOT%"
                    },
                    "region": {
                        "startLine": vuln["line"],
                        "startColumn": 1,
                        "snippet": {
                            "text": vuln.get("code", "")
                        }
                    }
                }
            }],
            "partialFingerprints": {
                "primaryLocationLineHash": f"{vuln['file']}:{vuln['line']}"
            }
        }
        results.append(result)
    
    # Build SARIF document
    sarif = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {
                "driver": {
                    "name": "OpenIssue Security Scanner",
                    "version": "1.0.0",
                    "informationUri": "https://github.com/yourusername/openissue",
                    "rules": rules
                }
            },
            "results": results,
            "columnKind": "utf16CodeUnits",
            "properties": {
                "scannedFiles": scan_results.get("scanned_files", 0),
                "totalVulnerabilities": scan_results.get("total", 0),
                "severityCounts": scan_results.get("severity_counts", {}),
                "scanDate": datetime.utcnow().isoformat() + "Z"
            }
        }]
    }
    
    return sarif


def severity_to_level(severity: str) -> str:
    """Convert severity to SARIF level"""
    mapping = {
        "CRITICAL": "error",
        "HIGH": "error",
        "MEDIUM": "warning",
        "LOW": "note"
    }
    return mapping.get(severity, "warning")


def save_sarif(sarif_data: Dict[str, Any], output_path: str):
    """Save SARIF to file"""
    with open(output_path, 'w') as f:
        json.dump(sarif_data, f, indent=2)
