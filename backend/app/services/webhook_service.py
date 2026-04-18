"""
Webhook Event Processing Service
Handles GitHub webhook events and triggers analysis pipeline.
"""

import asyncio
import logging
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class WebhookEventType(str, Enum):
    """GitHub webhook event types."""
    ISSUES = "issues"
    PULL_REQUEST = "pull_request"
    PUSH = "push"


class WebhookProcessor:
    """Process GitHub webhook events and trigger analysis."""
    
    def __init__(self):
        """Initialize webhook processor."""
        self.logger = logging.getLogger(__name__)
    
    async def process_event(self, event_type: str, payload: dict):
        """
        Route event to appropriate handler.
        
        Args:
            event_type: GitHub event type (issues, pull_request, etc.)
            payload: Full GitHub webhook payload
        """
        try:
            if event_type == WebhookEventType.ISSUES:
                await self.handle_issue_event(payload)
            elif event_type == WebhookEventType.PULL_REQUEST:
                await self.handle_pr_event(payload)
            elif event_type == WebhookEventType.PUSH:
                await self.handle_push_event(payload)
            else:
                self.logger.debug(f"Ignoring event type: {event_type}")
        except Exception as e:
            self.logger.error(f"Error processing {event_type} event: {e}", exc_info=True)
            raise
    
    async def handle_issue_event(self, payload: dict):
        """
        Handle issue creation/update/reopened events.
        
        Args:
            payload: GitHub webhook payload
        """
        action = payload.get("action")
        
        # Only process relevant actions
        if action not in ["opened", "edited", "reopened"]:
            self.logger.debug(f"Ignoring issue action: {action}")
            return
        
        try:
            issue = payload.get("issue", {})
            repo = payload.get("repository", {})
            
            # Extract issue details
            issue_data = {
                "repo": f"{repo['owner']['login']}/{repo['name']}",
                "repo_id": repo.get("id"),
                "issue_number": issue.get("number"),
                "title": issue.get("title", ""),
                "body": issue.get("body", ""),
                "labels": [label.get("name") for label in issue.get("labels", [])],
                "author": issue.get("user", {}).get("login"),
                "created_at": issue.get("created_at"),
                "updated_at": issue.get("updated_at"),
                "state": issue.get("state"),
                "url": issue.get("html_url")
            }
            
            self.logger.info(f"Processing issue #{issue_data['issue_number']} in {issue_data['repo']}")
            
            # Run analysis
            analysis = await self.analyze_issue(issue_data)
            
            # Apply auto-actions
            await self.apply_auto_actions(repo, issue, analysis, issue_data)
            
        except Exception as e:
            self.logger.error(f"Error handling issue event: {e}", exc_info=True)
            raise
    
    async def handle_pr_event(self, payload: dict):
        """
        Handle pull request creation/update events.
        
        Args:
            payload: GitHub webhook payload
        """
        action = payload.get("action")
        
        # Only process relevant actions
        if action not in ["opened", "edited"]:
            self.logger.debug(f"Ignoring PR action: {action}")
            return
        
        try:
            pr = payload.get("pull_request", {})
            repo = payload.get("repository", {})
            
            self.logger.info(f"Processing PR #{pr.get('number')} in {repo.get('full_name')}")
            
            # PR processing logic can be added here
            # For now, we'll just log it
            
        except Exception as e:
            self.logger.error(f"Error handling PR event: {e}", exc_info=True)
            raise
    
    async def handle_push_event(self, payload: dict):
        """
        Handle push events.
        
        Args:
            payload: GitHub webhook payload
        """
        try:
            repo = payload.get("repository", {})
            self.logger.info(f"Processing push to {repo.get('full_name')}")
            
            # Push processing logic can be added here
            
        except Exception as e:
            self.logger.error(f"Error handling push event: {e}", exc_info=True)
            raise
    
    async def analyze_issue(self, issue_data: dict) -> dict:
        """
        Run full issue analysis pipeline.
        
        Args:
            issue_data: Extracted issue data
        
        Returns:
            Analysis results
        """
        try:
            # Import analysis services
            from backend.app.services.classifier_service import classify_issue
            from backend.app.services.priority_service import calculate_priority
            from backend.app.services.duplicate_detector import find_duplicates
            from backend.app.services.vulnerability_service import detect_vulnerabilities
            
            # Run all analyses in parallel
            results = await asyncio.gather(
                self._safe_classify(classify_issue, issue_data),
                self._safe_priority(calculate_priority, issue_data),
                self._safe_duplicates(find_duplicates, issue_data),
                self._safe_vulnerabilities(detect_vulnerabilities, issue_data),
                return_exceptions=True
            )
            
            return {
                "classification": results[0] if not isinstance(results[0], Exception) else None,
                "priority": results[1] if not isinstance(results[1], Exception) else {"score": 5, "level": "medium", "reason": "Unable to calculate"},
                "duplicates": results[2] if not isinstance(results[2], Exception) else [],
                "vulnerabilities": results[3] if not isinstance(results[3], Exception) else []
            }
        
        except Exception as e:
            self.logger.error(f"Error analyzing issue: {e}", exc_info=True)
            return {
                "classification": None,
                "priority": {"score": 5, "level": "medium", "reason": "Analysis failed"},
                "duplicates": [],
                "vulnerabilities": []
            }
    
    async def _safe_classify(self, func, issue_data):
        """Safely call classification service."""
        try:
            return await func(issue_data) if asyncio.iscoroutinefunction(func) else func(issue_data)
        except Exception as e:
            self.logger.warning(f"Classification failed: {e}")
            return None
    
    async def _safe_priority(self, func, issue_data):
        """Safely call priority service."""
        try:
            return await func(issue_data) if asyncio.iscoroutinefunction(func) else func(issue_data)
        except Exception as e:
            self.logger.warning(f"Priority calculation failed: {e}")
            return {"score": 5, "level": "medium", "reason": "Unable to calculate"}
    
    async def _safe_duplicates(self, func, issue_data):
        """Safely call duplicate detector."""
        try:
            return await func(issue_data) if asyncio.iscoroutinefunction(func) else func(issue_data)
        except Exception as e:
            self.logger.warning(f"Duplicate detection failed: {e}")
            return []
    
    async def _safe_vulnerabilities(self, func, issue_data):
        """Safely call vulnerability detector."""
        try:
            return await func(issue_data) if asyncio.iscoroutinefunction(func) else func(issue_data)
        except Exception as e:
            self.logger.warning(f"Vulnerability detection failed: {e}")
            return []
    
    async def apply_auto_actions(self, repo: dict, issue: dict, analysis: dict, issue_data: dict):
        """
        Apply automatic actions based on analysis.
        
        Args:
            repo: Repository data
            issue: Issue data
            analysis: Analysis results
            issue_data: Extracted issue data
        """
        try:
            # 1. Determine labels to add
            labels_to_add = self.get_labels_from_analysis(analysis)
            
            if labels_to_add:
                await self.add_labels(repo, issue["number"], labels_to_add)
            
            # 2. Post analysis comment
            comment = self.format_analysis_comment(analysis, issue_data)
            await self.post_comment(repo, issue["number"], comment)
            
            # 3. Create notification for high-priority issues
            if analysis.get("priority", {}).get("score", 0) >= 8:
                await self.create_notification(repo, issue, analysis)
            
            self.logger.info(f"Auto-actions applied for issue #{issue['number']}")
        
        except Exception as e:
            self.logger.error(f"Error applying auto-actions: {e}", exc_info=True)
    
    def get_labels_from_analysis(self, analysis: dict) -> List[str]:
        """
        Determine labels to add based on analysis.
        
        Args:
            analysis: Analysis results
        
        Returns:
            List of labels to add
        """
        labels = []
        
        # Add classification label
        if analysis.get("classification"):
            labels.append(f"type/{analysis['classification'].lower()}")
        
        # Add priority label
        priority_score = analysis.get("priority", {}).get("score", 5)
        if priority_score >= 8:
            labels.append("priority/critical")
        elif priority_score >= 6:
            labels.append("priority/high")
        elif priority_score >= 4:
            labels.append("priority/medium")
        else:
            labels.append("priority/low")
        
        # Add vulnerability label
        if analysis.get("vulnerabilities"):
            labels.append("security/vulnerability")
        
        # Add duplicate label
        if analysis.get("duplicates"):
            labels.append("duplicate/potential")
        
        return labels
    
    def format_analysis_comment(self, analysis: dict, issue_data: dict) -> str:
        """
        Format analysis results as GitHub comment.
        
        Args:
            analysis: Analysis results
            issue_data: Issue data
        
        Returns:
            Formatted comment
        """
        comment = "## 🤖 OpenIssue Analysis\n\n"
        
        # Classification
        if analysis.get("classification"):
            comment += f"**Type:** `{analysis['classification']}`\n"
        
        # Priority
        priority = analysis.get("priority", {})
        score = priority.get("score", 5)
        level = priority.get("level", "medium")
        reason = priority.get("reason", "")
        
        emoji = "🔴" if score >= 8 else "🟠" if score >= 6 else "🟡" if score >= 4 else "🟢"
        comment += f"\n**Priority:** {emoji} {score}/10 - {level.upper()}\n"
        if reason:
            comment += f"*{reason}*\n"
        
        # Duplicates
        duplicates = analysis.get("duplicates", [])
        if duplicates:
            comment += "\n**Potential Duplicates:**\n"
            for dup in duplicates[:3]:
                similarity = dup.get("similarity", 0)
                comment += f"- #{dup.get('issue_number')}: {dup.get('title')} ({similarity:.0%})\n"
        
        # Vulnerabilities
        vulnerabilities = analysis.get("vulnerabilities", [])
        if vulnerabilities:
            comment += "\n**Security Issues Detected:**\n"
            for vuln in vulnerabilities:
                comment += f"- **{vuln.get('type')}:** {vuln.get('description')}\n"
        
        comment += "\n---\n*Analysis by [OpenIssue](https://openissue.dev) | [View Dashboard](http://localhost:8080)*"
        
        return comment
    
    async def add_labels(self, repo: dict, issue_number: int, labels: List[str]):
        """
        Add labels to GitHub issue.
        
        Args:
            repo: Repository data
            issue_number: Issue number
            labels: Labels to add
        """
        try:
            from backend.app.services.github_service import GitHubService
            
            github = GitHubService()
            await github.add_labels(repo["full_name"], issue_number, labels)
            self.logger.info(f"Added labels to issue #{issue_number}: {labels}")
        
        except Exception as e:
            self.logger.warning(f"Failed to add labels: {e}")
    
    async def post_comment(self, repo: dict, issue_number: int, comment: str):
        """
        Post comment to GitHub issue.
        
        Args:
            repo: Repository data
            issue_number: Issue number
            comment: Comment text
        """
        try:
            from backend.app.services.github_service import GitHubService
            
            github = GitHubService()
            await github.post_comment(repo["full_name"], issue_number, comment)
            self.logger.info(f"Posted comment to issue #{issue_number}")
        
        except Exception as e:
            self.logger.warning(f"Failed to post comment: {e}")
    
    async def create_notification(self, repo: dict, issue: dict, analysis: dict):
        """
        Create notification for high-priority issues.
        
        Args:
            repo: Repository data
            issue: Issue data
            analysis: Analysis results
        """
        try:
            # Notification logic can be implemented here
            # For now, just log it
            self.logger.info(f"High-priority issue detected: {repo['full_name']}#{issue['number']}")
        
        except Exception as e:
            self.logger.warning(f"Failed to create notification: {e}")
