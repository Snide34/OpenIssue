"""
GitHub Webhook Handler
Receives and processes GitHub webhook events for real-time issue analysis.
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import hmac
import hashlib
import json
import os
import logging
from datetime import datetime
from typing import Optional
import asyncio

from app.services.webhook_service import WebhookProcessor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhooks", tags=["webhooks"])

# In-memory webhook event log (replace with database in production)
webhook_events_log = []


def validate_github_signature(body: bytes, signature: str) -> bool:
    """
    Validate GitHub webhook signature.
    
    Args:
        body: Raw request body
        signature: X-Hub-Signature-256 header value
    
    Returns:
        True if signature is valid, False otherwise
    """
    try:
        secret = os.getenv("GITHUB_WEBHOOK_SECRET", "").encode()
        if not secret:
            logger.warning("GITHUB_WEBHOOK_SECRET not configured")
            return False
        
        expected = "sha256=" + hmac.new(
            secret, body, hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected, signature)
    except Exception as e:
        logger.error(f"Signature validation error: {e}")
        return False


def log_webhook_event(event_type: str, payload: dict, status: str = "received", error: Optional[str] = None):
    """
    Log webhook event for debugging and replay.
    
    Args:
        event_type: GitHub event type (issues, pull_request, etc.)
        payload: Full GitHub webhook payload
        status: Event processing status
        error: Error message if processing failed
    """
    event_log = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "repo": payload.get("repository", {}).get("full_name", "unknown"),
        "action": payload.get("action", "unknown"),
        "status": status,
        "error": error
    }
    
    webhook_events_log.append(event_log)
    
    # Keep only last 1000 events in memory
    if len(webhook_events_log) > 1000:
        webhook_events_log.pop(0)
    
    logger.info(f"Webhook event logged: {event_type} {payload.get('action')} {event_log['repo']}")


@router.post("/github")
async def github_webhook(request: Request):
    """
    GitHub webhook endpoint for real-time issue events.
    
    Validates webhook signature and processes events asynchronously.
    
    Returns:
        202 Accepted for valid events
        401 Unauthorized for invalid signatures
        400 Bad Request for malformed payloads
    """
    try:
        # 1. Validate webhook signature
        signature = request.headers.get("X-Hub-Signature-256")
        if not signature:
            logger.warning("Missing X-Hub-Signature-256 header")
            raise HTTPException(status_code=401, detail="Missing signature")
        
        body = await request.body()
        if not validate_github_signature(body, signature):
            logger.warning(f"Invalid signature: {signature}")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # 2. Parse event
        try:
            payload = json.loads(body)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON payload: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        event_type = request.headers.get("X-GitHub-Event", "unknown")
        
        # 3. Log event
        log_webhook_event(event_type, payload)
        
        # 4. Process event asynchronously (don't wait for completion)
        asyncio.create_task(process_webhook_event(event_type, payload))
        
        # 5. Return immediately with 202 Accepted
        return JSONResponse(
            {"status": "received", "event_type": event_type},
            status_code=202
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


async def process_webhook_event(event_type: str, payload: dict):
    """
    Process webhook event asynchronously.
    
    Args:
        event_type: GitHub event type
        payload: GitHub webhook payload
    """
    try:
        processor = WebhookProcessor()
        await processor.process_event(event_type, payload)
        log_webhook_event(event_type, payload, status="processed")
    except Exception as e:
        logger.error(f"Error processing webhook event: {e}", exc_info=True)
        log_webhook_event(event_type, payload, status="failed", error=str(e))


@router.get("/events")
async def get_webhook_events(limit: int = 100):
    """
    Get recent webhook events (for debugging).
    
    Args:
        limit: Maximum number of events to return
    
    Returns:
        List of recent webhook events
    """
    return {
        "total": len(webhook_events_log),
        "events": webhook_events_log[-limit:]
    }


@router.get("/health")
async def webhook_health():
    """
    Health check endpoint for webhook system.
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "events_logged": len(webhook_events_log),
        "timestamp": datetime.utcnow().isoformat()
    }
