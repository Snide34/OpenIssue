"""
AI-Powered Fix Generator
Uses Gemini AI to generate code fixes for vulnerabilities
"""
import os
from typing import Dict, Any, Optional


def generate_fix(vulnerability: Dict[str, Any]) -> Optional[str]:
    """
    Generate AI-powered fix suggestion for a vulnerability
    
    Args:
        vulnerability: Vulnerability dict with type, code, file, etc.
    
    Returns:
        Fix suggestion as string, or None if can't generate
    """
    
    # Check if Gemini API key is available
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # Build prompt based on vulnerability type
        prompt = build_fix_prompt(vulnerability)
        
        # Generate fix
        response = model.generate_content(prompt)
        return response.text
        
    except ImportError:
        return None
    except Exception as e:
        print(f"AI fix generation failed: {e}")
        return None


def build_fix_prompt(vuln: Dict[str, Any]) -> str:
    """Build prompt for AI fix generation"""
    
    vuln_type = vuln.get("type", "unknown")
    code = vuln.get("code", vuln.get("code_snippet", ""))
    file = vuln.get("file", "unknown")
    description = vuln.get("description", "")
    recommendation = vuln.get("recommendation", "")
    
    # Dependency vulnerability
    if vuln_type == "vulnerable_dependency":
        package = vuln.get("package", "unknown")
        current = vuln.get("current_version", "unknown")
        fixed = vuln.get("fixed_version", "latest")
        ecosystem = vuln.get("ecosystem", "unknown")
        
        return f"""You are a security expert. A vulnerable dependency was found:

Package: {package}
Ecosystem: {ecosystem}
Current Version: {current}
Fixed Version: {fixed}
Issue: {description}

Provide a concise fix in this format:
1. Command to update the package
2. Any breaking changes to watch for
3. Alternative if update isn't possible

Keep it under 100 words."""
    
    # Code vulnerability
    else:
        return f"""You are a security expert. A vulnerability was found in code:

File: {file}
Vulnerability Type: {vuln_type}
Issue: {description}
Current Code:
```
{code}
```

Recommendation: {recommendation}

Provide:
1. Fixed code (just the corrected line/block)
2. Brief explanation (1 sentence)

Format:
FIXED CODE:
```
[corrected code here]
```

EXPLANATION: [one sentence]

Keep it concise and actionable."""


def get_quick_fix(vuln_type: str) -> Optional[str]:
    """Get quick fix template without AI"""
    
    quick_fixes = {
        "hardcoded_secrets": """
QUICK FIX:
1. Move secret to environment variable
2. Add to .env file: SECRET_KEY=your_secret_here
3. Update code: secret = os.getenv('SECRET_KEY')
4. Add .env to .gitignore
""",
        "exposed_api_keys": """
QUICK FIX:
1. Rotate the exposed API key immediately!
2. Move to environment variable
3. Update code: api_key = os.getenv('API_KEY')
4. Add .env to .gitignore
5. Never commit .env file
""",
        "sql_injection": """
QUICK FIX:
1. Use parameterized queries
2. Example: cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
3. Never concatenate user input into SQL
4. Use ORM if possible (SQLAlchemy, Django ORM)
""",
        "xss_vulnerability": """
QUICK FIX:
1. Sanitize user input before rendering
2. Use textContent instead of innerHTML
3. Or use a library like DOMPurify
4. Escape HTML entities
""",
        "command_injection": """
QUICK FIX:
1. Avoid shell=True in subprocess
2. Use list of arguments instead of string
3. Validate and sanitize all inputs
4. Use subprocess.run(['cmd', 'arg1', 'arg2'])
""",
        "vulnerable_dependency": """
QUICK FIX:
1. Update the package to the fixed version
2. Run: npm update [package] or pip install --upgrade [package]
3. Test your application after updating
4. Check for breaking changes in changelog
"""
    }
    
    return quick_fixes.get(vuln_type)
