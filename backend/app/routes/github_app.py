"""
GitHub App Integration
Webhook handler for automatic issue triage
"""
from fastapi import APIRouter, Request, HTTPException, Header
from typing import Optional
import hmac
import hashlib
import os

from app.services.classifier_service import triage_issue
from app.services.vector_service import find_similar_issues
from app.services.github_app_service import github_app

router = APIRouter(prefix="/github", tags=["GitHub App"])

WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")


def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify GitHub webhook signature"""
    if not WEBHOOK_SECRET:
        return True  # Skip verification in development
    
    expected = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)


@router.post("/webhook")
async def github_webhook(
    request: Request,
    x_github_event: Optional[str] = Header(None),
    x_hub_signature_256: Optional[str] = Header(None)
):
    """
    Handle GitHub webhook events
    Automatically triages issues when they're opened
    """
    
    # Get raw payload for signature verification
    payload = await request.body()
    
    # Verify webhook signature
    if x_hub_signature_256 and not verify_signature(payload, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse JSON payload
    data = await request.json()
    
    # Handle different event types
    if x_github_event == "ping":
        return {"message": "pong"}
    
    if x_github_event == "issues":
        return await handle_issue_event(data)
    
    return {"message": "Event received but not processed"}


async def handle_issue_event(data: dict):
    """Handle issue opened/edited events"""
    action = data.get("action")
    
    # Only process new issues
    if action not in ["opened", "reopened"]:
        return {"message": f"Ignored action: {action}"}
    
    issue = data.get("issue", {})
    repository = data.get("repository", {})
    
    title = issue.get("title", "")
    body = issue.get("body", "")
    issue_number = issue.get("number")
    repo_full_name = repository.get("full_name")
    
    if not title or not issue_number:
        return {"message": "Invalid issue data"}
    
    # Classify the issue
    classification = triage_issue(title, body or "")
    
    # Find similar issues
    similar = find_similar_issues(title, body or "", top_k=5)
    
    # Build comment with triage results
    comment = build_triage_comment(classification, similar)
    
    # Post comment back to GitHub
    installation_id = data.get("installation", {}).get("id")
    if installation_id and github_app.is_configured():
        repo_parts = repo_full_name.split("/")
        if len(repo_parts) == 2:
            await github_app.post_issue_comment(
                installation_id,
                repo_parts[0],
                repo_parts[1],
                issue_number,
                comment
            )
            
            # Add labels
            labels = [classification.get("label", "triage")]
            if classification.get("priority") in ["critical", "high"]:
                labels.append("priority")
            
            await github_app.add_labels(
                installation_id,
                repo_parts[0],
                repo_parts[1],
                issue_number,
                labels
            )
    
    return {
        "message": "Issue triaged",
        "issue_number": issue_number,
        "repository": repo_full_name,
        "classification": classification.get("label"),
        "priority": classification.get("priority"),
        "similar_count": len(similar)
    }


def build_triage_comment(classification: dict, similar: list) -> str:
    """Build markdown comment for GitHub issue"""
    
    label = classification.get("label", "unknown")
    priority = classification.get("priority", "medium")
    reason = classification.get("reason", "")
    
    # Emoji mapping
    label_emoji = {
        "bug": "🐛",
        "feature": "✨",
        "question": "❓",
        "docs": "📚"
    }
    
    priority_emoji = {
        "critical": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🔵"
    }
    
    comment = f"""## 🤖 OpenIssue AI Triage

**Classification:** {label_emoji.get(label, '📋')} {label.upper()}
**Priority:** {priority_emoji.get(priority, '⚪')} {priority.upper()}

"""
    
    if reason:
        comment += f"**Reasoning:** {reason}\n\n"
    
    # Add similar issues
    if similar:
        comment += "### 🔍 Similar Issues\n\n"
        for sim in similar[:3]:  # Top 3
            similarity = sim.get("similarity_score", 0) * 100
            sim_title = sim.get("title", "Unknown")
            sim_id = sim.get("id", "")[:8]
            comment += f"- **{similarity:.0f}% match** - {sim_title} (`#{sim_id}`)\n"
        
        if len(similar) > 3:
            comment += f"\n*...and {len(similar) - 3} more similar issues*\n"
    
    comment += "\n---\n*Powered by [OpenIssue](https://github.com/yourusername/openissue)*"
    
    return comment


@router.get("/app/setup")
async def github_app_setup():
    """
    Instructions for setting up GitHub App
    """
    return {
        "message": "GitHub App Setup Instructions",
        "steps": [
            "1. Go to https://github.com/settings/apps/new",
            "2. Fill in app details:",
            {
                "name": "OpenIssue Triage Bot",
                "homepage_url": "https://yourdomain.com",
                "webhook_url": "https://yourdomain.com/github/webhook",
                "webhook_secret": "Generate a random secret",
                "permissions": {
                    "issues": "Read & write",
                    "metadata": "Read-only"
                },
                "events": ["issues"]
            },
            "3. Generate private key and save it",
            "4. Install app on your repositories",
            "5. Add credentials to .env:",
            {
                "GITHUB_APP_ID": "Your app ID",
                "GITHUB_APP_PRIVATE_KEY": "Path to private key file",
                "GITHUB_WEBHOOK_SECRET": "Your webhook secret"
            }
        ]
    }
