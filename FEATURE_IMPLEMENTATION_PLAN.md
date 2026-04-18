# Feature Implementation Plan: Real-Time Webhook Monitoring

## Overview
Enable automatic issue analysis when issues are created/updated on GitHub without manual intervention. This is a game-changer for competitive positioning.

## Architecture

```
GitHub Repository
       |
       v
GitHub Webhook Event
       |
       v
OpenIssue Webhook Endpoint (/webhooks/github)
       |
       v
Event Validation & Authentication
       |
       v
Issue Analysis Pipeline
       |
       +---> Classify Issue
       +---> Calculate Priority
       +---> Find Duplicates
       +---> Detect Vulnerabilities
       |
       v
Auto-Actions
       |
       +---> Add Labels
       +---> Post Comment with Analysis
       +---> Create Notification
       +---> Update Issue Status
       |
       v
Webhook Event Log (for replay/debugging)
```

## Implementation Phases

### Phase 1: Webhook Infrastructure (Days 1-2)

#### 1.1 Webhook Endpoint
**File:** `backend/app/routes/webhooks.py` (NEW)

```python
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import hmac
import hashlib
import json
from datetime import datetime

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

# Webhook event log storage
webhook_events = []

@router.post("/github")
async def github_webhook(request: Request):
    """
    GitHub webhook endpoint for real-time issue events.
    
    Validates webhook signature and processes events.
    """
    # 1. Validate webhook signature
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        raise HTTPException(status_code=401, detail="Missing signature")
    
    body = await request.body()
    expected_signature = validate_github_signature(body, signature)
    
    if not expected_signature:
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # 2. Parse event
    payload = json.loads(body)
    event_type = request.headers.get("X-GitHub-Event")
    
    # 3. Log event
    log_webhook_event(event_type, payload)
    
    # 4. Process event asynchronously
    await process_webhook_event(event_type, payload)
    
    return JSONResponse({"status": "received"}, status_code=202)


def validate_github_signature(body: bytes, signature: str) -> bool:
    """Validate GitHub webhook signature."""
    secret = os.getenv("GITHUB_WEBHOOK_SECRET").encode()
    expected = "sha256=" + hmac.new(
        secret, body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def log_webhook_event(event_type: str, payload: dict):
    """Log webhook event for debugging and replay."""
    webhook_events.append({
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "payload": payload,
        "status": "received"
    })
```

#### 1.2 Event Processing
**File:** `backend/app/services/webhook_service.py` (NEW)

```python
from enum import Enum
from typing import Optional
import asyncio

class WebhookEventType(str, Enum):
    ISSUES_OPENED = "issues.opened"
    ISSUES_EDITED = "issues.edited"
    ISSUES_REOPENED = "issues.reopened"
    PULL_REQUEST_OPENED = "pull_request.opened"
    PULL_REQUEST_EDITED = "pull_request.edited"

class WebhookProcessor:
    """Process GitHub webhook events."""
    
    async def process_event(self, event_type: str, payload: dict):
        """Route event to appropriate handler."""
        
        if event_type == "issues":
            action = payload.get("action")
            if action in ["opened", "edited", "reopened"]:
                await self.handle_issue_event(payload)
        
        elif event_type == "pull_request":
            action = payload.get("action")
            if action in ["opened", "edited"]:
                await self.handle_pr_event(payload)
    
    async def handle_issue_event(self, payload: dict):
        """Handle issue creation/update."""
        issue = payload.get("issue")
        repo = payload.get("repository")
        
        # Extract issue details
        issue_data = {
            "repo": f"{repo['owner']['login']}/{repo['name']}",
            "issue_number": issue["number"],
            "title": issue["title"],
            "body": issue["body"],
            "labels": [label["name"] for label in issue.get("labels", [])],
            "author": issue["user"]["login"]
        }
        
        # Run analysis
        analysis = await self.analyze_issue(issue_data)
        
        # Apply auto-actions
        await self.apply_auto_actions(repo, issue, analysis)
    
    async def analyze_issue(self, issue_data: dict) -> dict:
        """Run full issue analysis."""
        from backend.app.services.classifier_service import classify_issue
        from backend.app.services.priority_service import calculate_priority
        from backend.app.services.duplicate_detector import find_duplicates
        from backend.app.services.vulnerability_service import detect_vulnerabilities
        
        # Run all analyses in parallel
        results = await asyncio.gather(
            classify_issue(issue_data),
            calculate_priority(issue_data),
            find_duplicates(issue_data),
            detect_vulnerabilities(issue_data)
        )
        
        return {
            "classification": results[0],
            "priority": results[1],
            "duplicates": results[2],
            "vulnerabilities": results[3]
        }
    
    async def apply_auto_actions(self, repo: dict, issue: dict, analysis: dict):
        """Apply automatic actions based on analysis."""
        
        # 1. Add labels based on classification
        labels_to_add = self.get_labels_from_analysis(analysis)
        if labels_to_add:
            await self.add_labels(repo, issue["number"], labels_to_add)
        
        # 2. Post analysis comment
        comment = self.format_analysis_comment(analysis)
        await self.post_comment(repo, issue["number"], comment)
        
        # 3. Create notification for high-priority issues
        if analysis["priority"]["score"] > 8:
            await self.create_notification(repo, issue, analysis)
    
    def get_labels_from_analysis(self, analysis: dict) -> list:
        """Determine labels to add based on analysis."""
        labels = []
        
        # Add classification label
        if analysis["classification"]:
            labels.append(f"type/{analysis['classification']}")
        
        # Add priority label
        priority_score = analysis["priority"]["score"]
        if priority_score >= 8:
            labels.append("priority/critical")
        elif priority_score >= 6:
            labels.append("priority/high")
        elif priority_score >= 4:
            labels.append("priority/medium")
        else:
            labels.append("priority/low")
        
        # Add vulnerability label
        if analysis["vulnerabilities"]:
            labels.append("security/vulnerability")
        
        # Add duplicate label
        if analysis["duplicates"]:
            labels.append("duplicate/potential")
        
        return labels
    
    def format_analysis_comment(self, analysis: dict) -> str:
        """Format analysis results as GitHub comment."""
        comment = "## 🤖 OpenIssue Analysis\n\n"
        
        # Classification
        if analysis["classification"]:
            comment += f"**Type:** {analysis['classification']}\n"
        
        # Priority
        priority = analysis["priority"]
        comment += f"**Priority:** {priority['score']}/10 - {priority['level']}\n"
        comment += f"*Reason: {priority['reason']}*\n\n"
        
        # Duplicates
        if analysis["duplicates"]:
            comment += "**Potential Duplicates:**\n"
            for dup in analysis["duplicates"][:3]:
                comment += f"- #{dup['issue_number']}: {dup['title']} ({dup['similarity']:.0%})\n"
            comment += "\n"
        
        # Vulnerabilities
        if analysis["vulnerabilities"]:
            comment += "**Security Issues Detected:**\n"
            for vuln in analysis["vulnerabilities"]:
                comment += f"- {vuln['type']}: {vuln['description']}\n"
            comment += "\n"
        
        comment += "---\n*Analysis by OpenIssue | [View Dashboard](https://openissue.dev)*"
        
        return comment
    
    async def add_labels(self, repo: dict, issue_number: int, labels: list):
        """Add labels to GitHub issue."""
        # Implementation using GitHub API
        pass
    
    async def post_comment(self, repo: dict, issue_number: int, comment: str):
        """Post comment to GitHub issue."""
        # Implementation using GitHub API
        pass
    
    async def create_notification(self, repo: dict, issue: dict, analysis: dict):
        """Create notification for high-priority issues."""
        # Implementation for notification system
        pass
```

#### 1.3 Database Schema for Webhook Events
**File:** `backend/app/models/webhook_event_model.py` (NEW)

```python
from sqlalchemy import Column, String, JSON, DateTime, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class WebhookEvent(Base):
    __tablename__ = "webhook_events"
    
    id = Column(Integer, primary_key=True)
    event_type = Column(String, index=True)  # issues, pull_request, etc.
    action = Column(String)  # opened, edited, closed, etc.
    repo_full_name = Column(String, index=True)
    issue_number = Column(Integer, nullable=True)
    pr_number = Column(Integer, nullable=True)
    payload = Column(JSON)  # Full GitHub payload
    analysis_result = Column(JSON, nullable=True)  # Analysis results
    auto_actions_applied = Column(JSON, nullable=True)  # Actions taken
    status = Column(String, default="processed")  # processed, failed, pending
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    processed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<WebhookEvent {self.event_type} {self.repo_full_name}#{self.issue_number}>"
```

### Phase 2: GitHub Integration (Days 3-4)

#### 2.1 Webhook Registration
**File:** `backend/app/services/github_webhook_manager.py` (NEW)

```python
import requests
from typing import Optional

class GitHubWebhookManager:
    """Manage GitHub webhook registration."""
    
    def __init__(self, github_token: str, webhook_url: str):
        self.github_token = github_token
        self.webhook_url = webhook_url
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def register_webhook(self, repo: str, events: list = None) -> dict:
        """
        Register webhook for a repository.
        
        Args:
            repo: Repository in format "owner/repo"
            events: List of events to subscribe to
        
        Returns:
            Webhook configuration
        """
        if events is None:
            events = [
                "issues",
                "pull_request",
                "push"
            ]
        
        url = f"https://api.github.com/repos/{repo}/hooks"
        
        payload = {
            "name": "web",
            "active": True,
            "events": events,
            "config": {
                "url": self.webhook_url,
                "content_type": "json",
                "secret": os.getenv("GITHUB_WEBHOOK_SECRET"),
                "insecure_ssl": "0"
            }
        }
        
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        
        return response.json()
    
    def list_webhooks(self, repo: str) -> list:
        """List all webhooks for a repository."""
        url = f"https://api.github.com/repos/{repo}/hooks"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def delete_webhook(self, repo: str, hook_id: int) -> bool:
        """Delete a webhook."""
        url = f"https://api.github.com/repos/{repo}/hooks/{hook_id}"
        response = requests.delete(url, headers=self.headers)
        return response.status_code == 204
    
    def test_webhook(self, repo: str, hook_id: int) -> bool:
        """Send test event to webhook."""
        url = f"https://api.github.com/repos/{repo}/hooks/{hook_id}/tests"
        response = requests.post(url, headers=self.headers)
        return response.status_code == 204
```

#### 2.2 API Endpoint for Webhook Management
**File:** `backend/app/routes/webhook_management.py` (NEW)

```python
from fastapi import APIRouter, Depends, HTTPException
from backend.app.services.github_webhook_manager import GitHubWebhookManager

router = APIRouter(prefix="/api/webhooks", tags=["webhook-management"])

@router.post("/register/{repo}")
async def register_webhook(repo: str, current_user = Depends(get_current_user)):
    """Register webhook for a repository."""
    try:
        manager = GitHubWebhookManager(
            github_token=current_user.github_token,
            webhook_url=os.getenv("WEBHOOK_URL")
        )
        webhook = manager.register_webhook(repo)
        return {"status": "registered", "webhook": webhook}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/list/{repo}")
async def list_webhooks(repo: str, current_user = Depends(get_current_user)):
    """List webhooks for a repository."""
    try:
        manager = GitHubWebhookManager(
            github_token=current_user.github_token,
            webhook_url=os.getenv("WEBHOOK_URL")
        )
        webhooks = manager.list_webhooks(repo)
        return {"webhooks": webhooks}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/delete/{repo}/{hook_id}")
async def delete_webhook(repo: str, hook_id: int, current_user = Depends(get_current_user)):
    """Delete a webhook."""
    try:
        manager = GitHubWebhookManager(
            github_token=current_user.github_token,
            webhook_url=os.getenv("WEBHOOK_URL")
        )
        success = manager.delete_webhook(repo, hook_id)
        return {"status": "deleted" if success else "failed"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Phase 3: Frontend UI (Days 5-6)

#### 3.1 Webhook Settings Page
**File:** `frontend/pages/webhook-settings.html` (NEW)

```html
<!DOCTYPE html>
<html class="dark" lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Webhook Settings | OpenIssue</title>
    <link href="../styles/main.css" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-background text-on-surface min-h-screen">
    <!-- Navigation -->
    <nav class="fixed top-0 w-full z-50 bg-[#0a0e13]/60 backdrop-blur-xl border-b border-white/5">
        <div class="flex justify-between items-center h-16 px-8 w-full max-w-screen-2xl mx-auto">
            <span class="text-2xl font-bold text-primary">OpenIssue</span>
            <div class="flex items-center gap-6">
                <a href="dashboard.html" class="text-slate-400 hover:text-primary">Dashboard</a>
                <a href="settings.html" class="text-primary">Settings</a>
            </div>
        </div>
    </nav>

    <main class="pt-24 pb-12 px-6 max-w-screen-2xl mx-auto">
        <header class="mb-12">
            <h1 class="text-4xl font-bold mb-2">Webhook Settings</h1>
            <p class="text-on-surface-variant">Configure real-time issue analysis for your repositories</p>
        </header>

        <!-- Webhook Status -->
        <div class="glass-card p-6 mb-8">
            <h2 class="text-xl font-bold mb-4">Active Webhooks</h2>
            <div id="webhook-list" class="space-y-4">
                <div class="text-on-surface-variant">Loading webhooks...</div>
            </div>
        </div>

        <!-- Register New Webhook -->
        <div class="glass-card p-6">
            <h2 class="text-xl font-bold mb-4">Register New Webhook</h2>
            <form id="webhook-form" class="space-y-4">
                <div>
                    <label class="block text-sm font-semibold mb-2">Repository</label>
                    <input type="text" id="repo-input" placeholder="owner/repo" 
                           class="glass-input w-full" required>
                </div>
                <div>
                    <label class="block text-sm font-semibold mb-2">Events to Monitor</label>
                    <div class="space-y-2">
                        <label class="flex items-center gap-2">
                            <input type="checkbox" name="events" value="issues" checked>
                            <span>Issues (created, edited, reopened)</span>
                        </label>
                        <label class="flex items-center gap-2">
                            <input type="checkbox" name="events" value="pull_request">
                            <span>Pull Requests (created, edited)</span>
                        </label>
                        <label class="flex items-center gap-2">
                            <input type="checkbox" name="events" value="push">
                            <span>Push Events</span>
                        </label>
                    </div>
                </div>
                <button type="submit" class="btn-primary-gradient px-6 py-2">
                    Register Webhook
                </button>
            </form>
        </div>
    </main>

    <script src="../js/webhook-settings.js"></script>
</body>
</html>
```

#### 3.2 Webhook Settings JavaScript
**File:** `frontend/js/webhook-settings.js` (NEW)

```javascript
const API_BASE = 'http://localhost:8001';

class WebhookSettings {
    constructor() {
        this.init();
    }

    async init() {
        this.loadWebhooks();
        document.getElementById('webhook-form').addEventListener('submit', (e) => this.handleRegister(e));
    }

    async loadWebhooks() {
        const repo = localStorage.getItem('selected_repo');
        if (!repo) return;

        try {
            const response = await fetch(`${API_BASE}/api/webhooks/list/${repo}`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('session_id')}` }
            });
            const data = await response.json();
            this.renderWebhooks(data.webhooks);
        } catch (error) {
            console.error('Failed to load webhooks:', error);
        }
    }

    renderWebhooks(webhooks) {
        const list = document.getElementById('webhook-list');
        if (webhooks.length === 0) {
            list.innerHTML = '<div class="text-on-surface-variant">No webhooks registered</div>';
            return;
        }

        list.innerHTML = webhooks.map(webhook => `
            <div class="border border-white/10 rounded-lg p-4 flex justify-between items-center">
                <div>
                    <p class="font-semibold">${webhook.config.url}</p>
                    <p class="text-sm text-on-surface-variant">Events: ${webhook.events.join(', ')}</p>
                    <p class="text-xs text-on-surface-variant mt-1">Status: ${webhook.active ? '✅ Active' : '❌ Inactive'}</p>
                </div>
                <button onclick="webhookSettings.deleteWebhook(${webhook.id})" 
                        class="px-4 py-2 bg-error/20 text-error rounded hover:bg-error/30">
                    Delete
                </button>
            </div>
        `).join('');
    }

    async handleRegister(e) {
        e.preventDefault();
        const repo = document.getElementById('repo-input').value;
        const events = Array.from(document.querySelectorAll('input[name="events"]:checked'))
            .map(el => el.value);

        try {
            const response = await fetch(`${API_BASE}/api/webhooks/register/${repo}`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${localStorage.getItem('session_id')}` },
                body: JSON.stringify({ events })
            });
            const data = await response.json();
            alert('Webhook registered successfully!');
            this.loadWebhooks();
        } catch (error) {
            alert('Failed to register webhook: ' + error.message);
        }
    }

    async deleteWebhook(hookId) {
        if (!confirm('Delete this webhook?')) return;
        
        const repo = localStorage.getItem('selected_repo');
        try {
            await fetch(`${API_BASE}/api/webhooks/delete/${repo}/${hookId}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${localStorage.getItem('session_id')}` }
            });
            this.loadWebhooks();
        } catch (error) {
            alert('Failed to delete webhook: ' + error.message);
        }
    }
}

const webhookSettings = new WebhookSettings();
```

### Phase 4: Testing & Deployment (Days 7)

#### 4.1 Unit Tests
**File:** `backend/tests/test_webhooks.py` (NEW)

```python
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_webhook_signature_validation():
    """Test GitHub webhook signature validation."""
    # Test with invalid signature
    response = client.post(
        "/webhooks/github",
        json={"action": "opened"},
        headers={"X-Hub-Signature-256": "invalid"}
    )
    assert response.status_code == 401

def test_webhook_event_processing():
    """Test webhook event processing."""
    payload = {
        "action": "opened",
        "issue": {
            "number": 123,
            "title": "Test Issue",
            "body": "Test body"
        },
        "repository": {
            "name": "test-repo",
            "owner": {"login": "test-owner"}
        }
    }
    # Test event processing
    # (Implementation details)

def test_auto_label_application():
    """Test automatic label application."""
    # Test that labels are correctly applied based on analysis
    # (Implementation details)
```

#### 4.2 Integration Tests
**File:** `backend/tests/test_webhook_integration.py` (NEW)

```python
import pytest
from unittest.mock import patch, MagicMock

def test_full_webhook_flow():
    """Test complete webhook flow from event to auto-actions."""
    # Mock GitHub API
    # Mock analysis services
    # Verify auto-actions are applied
    # (Implementation details)
```

---

## Environment Variables Required

```env
# .env
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here
WEBHOOK_URL=https://your-domain.com/webhooks/github
GITHUB_TOKEN=ghp_your_token_here
```

---

## Deployment Checklist

- [ ] Database migrations for webhook_events table
- [ ] Environment variables configured
- [ ] GitHub webhook secret generated
- [ ] Webhook URL publicly accessible
- [ ] Rate limiting configured
- [ ] Error handling and logging
- [ ] Monitoring and alerting setup
- [ ] Documentation updated
- [ ] User guide created

---

## Success Metrics

- Webhook events processed per day
- Average analysis time per event
- Auto-action success rate
- User adoption rate
- Reduction in manual triage time

---

## Next Features to Build

1. **Notification System** - Slack, Email, In-app notifications
2. **Webhook Event Replay** - Replay failed events
3. **Custom Automation Rules** - User-defined auto-actions
4. **Webhook Analytics** - Dashboard showing webhook activity

