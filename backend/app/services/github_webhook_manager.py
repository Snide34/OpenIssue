"""
GitHub Webhook Manager Service
Manages webhook registration, listing, and deletion via GitHub API.
"""

import requests
import logging
import os
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)


class GitHubWebhookManager:
    """Manage GitHub webhook registration and lifecycle."""
    
    def __init__(self, github_token: str, webhook_url: str):
        """
        Initialize GitHub webhook manager.
        
        Args:
            github_token: GitHub personal access token
            webhook_url: URL where webhooks will be sent
        """
        self.github_token = github_token
        self.webhook_url = webhook_url
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "OpenIssue"
        }
    
    def register_webhook(self, repo: str, events: Optional[List[str]] = None) -> Dict:
        """
        Register webhook for a repository.
        
        Args:
            repo: Repository in format "owner/repo"
            events: List of events to subscribe to
        
        Returns:
            Webhook configuration
        
        Raises:
            requests.RequestException: If GitHub API call fails
        """
        if events is None:
            events = ["issues", "pull_request"]
        
        url = f"https://api.github.com/repos/{repo}/hooks"
        
        webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET", "")
        
        payload = {
            "name": "web",
            "active": True,
            "events": events,
            "config": {
                "url": self.webhook_url,
                "content_type": "json",
                "secret": webhook_secret,
                "insecure_ssl": "0"
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            webhook = response.json()
            logger.info(f"Webhook registered for {repo}: {webhook.get('id')}")
            
            return webhook
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to register webhook for {repo}: {e}")
            raise
    
    def list_webhooks(self, repo: str) -> List[Dict]:
        """
        List all webhooks for a repository.
        
        Args:
            repo: Repository in format "owner/repo"
        
        Returns:
            List of webhook configurations
        
        Raises:
            requests.RequestException: If GitHub API call fails
        """
        url = f"https://api.github.com/repos/{repo}/hooks"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            webhooks = response.json()
            logger.info(f"Listed {len(webhooks)} webhooks for {repo}")
            
            return webhooks
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to list webhooks for {repo}: {e}")
            raise
    
    def delete_webhook(self, repo: str, hook_id: int) -> bool:
        """
        Delete a webhook.
        
        Args:
            repo: Repository in format "owner/repo"
            hook_id: Webhook ID
        
        Returns:
            True if successful, False otherwise
        
        Raises:
            requests.RequestException: If GitHub API call fails
        """
        url = f"https://api.github.com/repos/{repo}/hooks/{hook_id}"
        
        try:
            response = requests.delete(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Deleted webhook {hook_id} for {repo}")
            
            return response.status_code == 204
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to delete webhook {hook_id} for {repo}: {e}")
            raise
    
    def test_webhook(self, repo: str, hook_id: int) -> bool:
        """
        Send test event to webhook.
        
        Args:
            repo: Repository in format "owner/repo"
            hook_id: Webhook ID
        
        Returns:
            True if successful, False otherwise
        
        Raises:
            requests.RequestException: If GitHub API call fails
        """
        url = f"https://api.github.com/repos/{repo}/hooks/{hook_id}/tests"
        
        try:
            response = requests.post(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Sent test webhook for {repo} hook {hook_id}")
            
            return response.status_code == 204
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to test webhook {hook_id} for {repo}: {e}")
            raise
    
    def update_webhook(self, repo: str, hook_id: int, events: List[str]) -> Dict:
        """
        Update webhook events.
        
        Args:
            repo: Repository in format "owner/repo"
            hook_id: Webhook ID
            events: New list of events
        
        Returns:
            Updated webhook configuration
        
        Raises:
            requests.RequestException: If GitHub API call fails
        """
        url = f"https://api.github.com/repos/{repo}/hooks/{hook_id}"
        
        payload = {
            "events": events,
            "active": True
        }
        
        try:
            response = requests.patch(url, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            webhook = response.json()
            logger.info(f"Updated webhook {hook_id} for {repo}")
            
            return webhook
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to update webhook {hook_id} for {repo}: {e}")
            raise
