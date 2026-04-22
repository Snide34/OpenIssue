# 🔍 OpenIssue CLI

AI-powered security vulnerability scanner with GitHub integration and CI/CD support.

## Features

- 🔍 **Multi-language dependency scanning** (npm, pip, maven, composer)
- 🤖 **AI-powered fix suggestions** using Google Gemini
- 📋 **SARIF output** for GitHub Security tab integration
- 🚀 **CI/CD ready** with GitHub Actions support
- 📝 **Issue management** with OpenIssue backend integration
- 🎨 **Rich terminal output** with colors and progress bars

## Installation

### From Source
```bash
cd cli
pip install -e .
```

### For Development
```bash
cd cli
pip install -e ".[dev]"
```

## Usage

### Security Scanning

Scan current directory:
```bash
openissue scan
```

Scan specific directory with verbose output:
```bash
openissue scan /path/to/project --verbose
```

Generate SARIF for GitHub Security:
```bash
openissue scan --sarif results.sarif
```

Output JSON results:
```bash
openissue scan --json > results.json
```

Generate AI-powered fixes:
```bash
openissue scan --ai-fixes --verbose
```

Fail build on high severity issues:
```bash
openissue scan --fail-on high
```

### Issue Management

Post an issue to OpenIssue backend:
```bash
openissue post --title "Security Issue" --description "Found vulnerability"
```

Post from markdown file:
```bash
openissue post --file issue.md
```

Analyze before posting:
```bash
openissue post --title "Bug Report" --analyze
```

## CI/CD Integration

### GitHub Actions

The CLI is designed to work seamlessly with GitHub Actions. Here's an example workflow:

```yaml
name: Security Scan
on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install OpenIssue CLI
        run: |
          cd cli
          pip install -e .
      
      - name: Run Security Scan
        run: |
          openissue scan --sarif results.sarif --json > results.json
      
      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: results.sarif
```

### Exit Codes

- `0`: No vulnerabilities found (or below fail threshold)
- `1`: Vulnerabilities found above fail threshold

### Environment Variables

- `OI_SERVER_URL`: OpenIssue backend server URL (default: http://localhost:8000)
- `OI_API_TOKEN`: API token for backend authentication
- `GEMINI_API_KEY`: Google Gemini API key for AI fixes

## Supported Vulnerability Types

### Dependency Vulnerabilities
- **npm** packages (using `npm audit`)
- **Python** packages (using `pip-audit` or `safety`)
- **Maven** dependencies (planned)
- **Composer** packages (using `composer audit`)

### Code Vulnerabilities (Planned)
- Hardcoded secrets
- SQL injection
- XSS vulnerabilities
- Command injection
- Insecure configurations

## Output Formats

### JSON Output
```json
{
  "vulnerabilities": [...],
  "total": 5,
  "severity_counts": {
    "CRITICAL": 1,
    "HIGH": 2,
    "MEDIUM": 2,
    "LOW": 0
  },
  "scan_metadata": {
    "directory": "/path/to/project",
    "timestamp": "2024-01-01T12:00:00Z",
    "cli_version": "1.0.0"
  }
}
```

### SARIF Output
Standard SARIF 2.1.0 format for GitHub Security tab integration.

## AI-Powered Fixes

When `--ai-fixes` is enabled, the CLI uses Google Gemini to generate contextual fix suggestions:

```bash
openissue scan --ai-fixes --verbose
```

Example output:
```
🤖 AI Fix Suggestion:
FIXED CODE:
```python
# Use environment variable instead of hardcoded secret
api_key = os.getenv('API_KEY')
```

EXPLANATION: Move the hardcoded API key to an environment variable for security.
```

## Commands

### `scan`
Scan directory for security vulnerabilities.

**Options:**
- `--output, -o`: Save JSON results to file
- `--sarif`: Generate SARIF output file
- `--json`: Output JSON to stdout
- `--verbose, -v`: Show detailed results
- `--ai-fixes`: Generate AI-powered fix suggestions
- `--fail-on`: Fail on severity level (critical, high, medium, low)

### `post`
Post an issue to OpenIssue backend.

**Options:**
- `--title, -t`: Issue title (required)
- `--description, -d`: Issue description
- `--file, -f`: Read issue from markdown file
- `--repo, -r`: Repository (owner/repo format)
- `--labels, -l`: Comma-separated labels
- `--analyze, -a`: Analyze issue before creating
- `--server`: OpenIssue server URL

### `version`
Show version information.

## Development

### Running Tests
```bash
cd cli
python -m pytest tests/
```

### Code Formatting
```bash
black openissue/
flake8 openissue/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- 📖 [Documentation](https://github.com/yourusername/openissue/docs)
- 🐛 [Bug Reports](https://github.com/yourusername/openissue/issues)
- 💬 [Discussions](https://github.com/yourusername/openissue/discussions)