# 🔍 OpenIssue CLI - Usage Examples

## Quick Start

### Installation
```bash
cd cli
pip install -e .
```

### Basic Scanning
```bash
# Scan current directory
openissue scan

# Scan specific directory
openissue scan /path/to/project

# Scan with verbose output
openissue scan --verbose
```

## CI/CD Integration Examples

### GitHub Actions (Complete Workflow)

Your project already includes a complete GitHub Actions workflow at `.github/workflows/openissue-scan.yml`. Here's what it does:

1. **Installs the CLI** in the CI environment
2. **Runs security scans** on every push and PR
3. **Uploads SARIF results** to GitHub Security tab
4. **Fails builds** on critical vulnerabilities
5. **Comments on PRs** with scan results

### Manual CI/CD Commands

```bash
# CI/CD scan with JSON and SARIF output
openissue scan . --sarif results.sarif --json > scan-results.json

# Fail build on high severity issues
openissue scan . --fail-on high

# Generate AI fixes for found vulnerabilities
openissue scan . --ai-fixes --verbose
```

### GitLab CI Example

```yaml
security_scan:
  stage: test
  image: python:3.11
  script:
    - cd cli && pip install -e .
    - openissue scan . --sarif results.sarif --json > scan-results.json
    - cat scan-results.json
  artifacts:
    reports:
      sast: results.sarif
    paths:
      - scan-results.json
  allow_failure: false
```

### Jenkins Pipeline Example

```groovy
pipeline {
    agent any
    stages {
        stage('Security Scan') {
            steps {
                sh '''
                    cd cli
                    pip install -e .
                    python -m openissue.cli scan . --sarif results.sarif --json > scan-results.json
                '''
                archiveArtifacts artifacts: 'results.sarif,scan-results.json'
                publishSarifReport sarifFilePath: 'results.sarif'
            }
        }
    }
}
```

## Output Examples

### JSON Output
```json
{
  "vulnerabilities": [
    {
      "type": "vulnerable_dependency",
      "severity": "HIGH",
      "description": "Vulnerable npm package: lodash",
      "package": "lodash",
      "current_version": "4.17.20",
      "fixed_version": "4.17.21",
      "cve": "CVE-2021-23337",
      "recommendation": "Update lodash to 4.17.21",
      "file": "package.json",
      "line": 1,
      "ecosystem": "npm"
    }
  ],
  "total": 1,
  "severity_counts": {
    "CRITICAL": 0,
    "HIGH": 1,
    "MEDIUM": 0,
    "LOW": 0
  },
  "scan_metadata": {
    "directory": "/path/to/project",
    "timestamp": "2024-01-01T12:00:00Z",
    "cli_version": "1.0.0",
    "ai_fixes_included": false
  }
}
```

### Console Output (Rich)
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                           OpenIssue Security Scan                           ┃
┃                                                                              ┃
┃ Total Vulnerabilities: 1                                                    ┃
┃ HIGH: 1                                                                      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

                              Vulnerability Details                              
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Type                 ┃ Severity ┃ File         ┃ Description                  ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ vulnerable_dependency│ HIGH     │ package.json │ Vulnerable npm package: lo…  │
└──────────────────────┴──────────┴──────────────┴──────────────────────────────┘
```

## Advanced Usage

### AI-Powered Fixes

```bash
# Generate AI fixes using Gemini
export GEMINI_API_KEY="your-api-key"
openissue scan . --ai-fixes --verbose
```

Example AI fix output:
```
🤖 AI Fix Suggestion:
FIXED CODE:
```javascript
// Update package.json
{
  "dependencies": {
    "lodash": "^4.17.21"  // Updated from 4.17.20
  }
}
```

EXPLANATION: Update lodash to version 4.17.21 to fix CVE-2021-23337.
```

### Issue Management

```bash
# Post scan results as an issue
openissue post --title "Security Scan Results" --description "Found 3 vulnerabilities"

# Post from markdown file
openissue post --file security-report.md

# Analyze before posting
openissue post --title "Critical Security Issue" --analyze
```

### Environment Configuration

```bash
# Set OpenIssue backend server
export OI_SERVER_URL="https://your-openissue-server.com"

# Set API token for authentication
export OI_API_TOKEN="your-api-token"

# Set Gemini API key for AI fixes
export GEMINI_API_KEY="your-gemini-key"
```

## Supported Vulnerability Types

### Dependency Vulnerabilities
- **npm** packages (using `npm audit`)
- **Python** packages (using `pip-audit`)
- **Composer** packages (using `composer audit`)
- **Maven** dependencies (planned)

### Code Vulnerabilities (Planned)
- Hardcoded secrets
- SQL injection patterns
- XSS vulnerabilities
- Command injection
- Insecure configurations

## Exit Codes

- `0`: Success (no vulnerabilities above fail threshold)
- `1`: Failure (vulnerabilities found above fail threshold or error)

## Integration with GitHub Security

The CLI generates SARIF 2.1.0 format output that integrates seamlessly with GitHub's Security tab:

1. **Upload SARIF** using `github/codeql-action/upload-sarif@v3`
2. **View results** in the Security tab
3. **Track fixes** across commits
4. **Set up alerts** for new vulnerabilities

## Troubleshooting

### Common Issues

1. **Unicode errors on Windows**: The CLI handles Windows console encoding automatically
2. **Missing dependencies**: Install with `pip install -e ".[dev]"` for development
3. **Permission errors**: Use `--user` flag with pip install
4. **Network timeouts**: Increase timeout with environment variables

### Debug Mode

```bash
# Enable verbose logging
openissue scan . --verbose

# Check CLI version
openissue version

# Test installation
python -c "from openissue.cli import main; print('CLI installed successfully')"
```

## Performance Tips

1. **Exclude large directories** like `node_modules` using `.gitignore`
2. **Use specific patterns** for targeted scanning
3. **Cache dependencies** in CI/CD for faster builds
4. **Run scans in parallel** for multiple projects

## Contributing

The CLI is designed to be extensible:

1. **Add new scanners** in `openissue/` directory
2. **Extend SARIF output** for new vulnerability types
3. **Add new output formats** (XML, CSV, etc.)
4. **Improve AI fix generation** with better prompts

See `cli/README.md` for development setup and contribution guidelines.