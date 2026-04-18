"""
Webhook Management API Routes
Endpoints for registering, listing, and managing GitHub webhooks.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import logging

from app.services.github_webhook_manager import GitHubWebhookManager
from app.routes.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/webhooks", tags=["webhook-management"])


@router.post("/register/{repo}")
async def register_webhook(
    repo: str,
    events: Optional[List[str]] = Query(None),
    current_user = Depends(get_current_user)
):
    """
    Register webhook for a repository.
    
    Args:
        repo: Repository in format "owner/repo"
        events: List of events to subscribe to (issues, pull_request, push)
        current_user: Authenticated user
    
    Returns:
        Webhook configuration
    """
    try:
        if not current_user.github_token:
            raise HTTPException(status_code=400, detail="GitHub token not configured")
        
        if events is None:
            events = ["issues", "pull_request"]
        
        manager = GitHubWebhookManager(
            github_token=current_user.github_token,
            webhook_url="http://localhost:8001/webhooks/github"  # TODO: Use env var
        )
        
        webhook = manager.register_webhook(repo, events)
        
        logger.info(f"Webhook registered for {repo} by {current_user.username}")
        
        return {
            "status": "registered",
            "webhook": webhook,
            "repo": repo,
            "events": events
        }
    
    except Exception as e:
        logger.error(f"Failed to register webhook: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/list/{repo}")
async def list_webhooks(
    repo: str,
    current_user = Depends(get_current_user)
):
    """
    List all webhooks for a repository.
    
    Args:
        repo: Repository in format "owner/repo"
        current_user: Authenticated user
    
    Returns:
        List of webhooks
    """
    try:
        if not current_user.github_token:
            raise HTTPException(status_code=400, detail="GitHub token not configured")
        
        manager = GitHubWebhookManager(
            github_token=current_user.github_token,
            webhook_url="http://localhost:8001/webhooks/github"
        )
        
        webhooks = manager.list_webhooks(repo)
        
        return {
            "repo": repo,
            "webhooks": webhooks,
            "total": len(webhooks)
        }
    
    except Exception as e:
        logger.error(f"Failed to list webhooks: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/delete/{repo}/{hook_id}")
async def delete_webhook(
    repo: str,
    hook_id: int,
    current_user = Depends(get_current_user)
):
    """
    Delete a webhook.
    
    Args:
        repo: Repository in format "owner/repo"
        hook_id: Webhook ID
        current_user: Authenticated user
    
    Returns:
        Deletion status
    """
    try:
        if not current_user.github_token:
            raise HTTPException(status_code=400, detail="GitHub token not configured")
        
        manager = GitHubWebhookManager(
            github_token=current_user.github_token,
            webhook_url="http://localhost:8001/webhooks/github"
        )
        
        success = manager.delete_webhook(repo, hook_id)
        
        if success:
            logger.info(f"Webhook {hook_id} deleted for {repo} by {current_user.username}")
            return {"status": "deleted", "repo": repo, "hook_id": hook_id}
        else:
            raise HTTPException(status_code=400, detail="Failed to delete webhook")
    
    except Exception as e:
        logger.error(f"Failed to delete webhook: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/test/{repo}/{hook_id}")
async def test_webhook(
    repo: str,
    hook_id: int,
    current_user = Depends(get_current_user)
):
    """
    Send test event to webhook.
    
    Args:
        repo: Repository in format "owner/repo"
        hook_id: Webhook ID
        current_user: Authenticated user
    
    Returns:
        Test status
    """
    try:
        if not current_user.github_token:
            raise HTTPException(status_code=400, detail="GitHub token not configured")
        
        manager = GitHubWebhookManager(
            github_token=current_user.github_token,
            webhook_url="http://localhost:8001/webhooks/github"
        )
        
        success = manager.test_webhook(repo, hook_id)
        
        if success:
            logger.info(f"Test webhook sent for {repo} hook {hook_id}")
            return {"status": "test_sent", "repo": repo, "hook_id": hook_id}
        else:
            raise HTTPException(status_code=400, detail="Failed to send test webhook")
    
    except Exception as e:
        logger.error(f"Failed to test webhook: {e}")
        raise HTTPException(status_code=400, detail=str(e))
