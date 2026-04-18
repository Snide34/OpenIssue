"""
GitHub App Service
Handles GitHub App authentication and API calls
"""
import os
import time
import jwt
import httpx
from pathlib import Path
from typing import Optional


class GitHubAppService:
    """Service for GitHub App operations"""
    
    def __init__(self):
        self.app_id = os.getenv("GITHUB_APP_ID")
        self.private_key_path = os.getenv("GITHUB_APP_PRIVATE_KEY")
        self.private_key = None
        
        if self.private_key_path and Path(self.private_key_path).exists():
            with open(self.private_key_path, 'r') as f:
                self.private_key = f.read()
    
    def is_configured(self) -> bool:
        """Check if GitHub App is configured"""
        return bool(self.app_id and self.private_key)
    
    def generate_jwt(self) -> str:
        """Generate JWT for GitHub App authentication"""
        if not self.is_configured():
            raise ValueError("GitHub App not configured")
        
        now = int(time.time())
        payload = {
            'iat': now,
            'exp': now + (10 * 60),  # 10 minutes
            'iss': self.app_id
        }
        
        return jwt.encode(payload, self.private_key, algorithm='RS256')
    
    async def get_installation_token(self, installation_id: int) -> Optional[str]:
        """Get installation access token"""
        if not self.is_configured():
            return None
        
        jwt_token = self.generate_jwt()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.github.com/app/installations/{installation_id}/access_tokens",
                headers={
                    "Authorization": f"Bearer {jwt_token}",
                    "Accept": "application/vnd.github.v3+json"
                }
            )
            
            if response.status_code == 201:
                return response.json().get("token")
        
        return None
    
    async def post_issue_comment(
        self,
        installation_id: int,
        repo_owner: str,
        repo_name: str,
        issue_number: int,
        comment_body: str
    ) -> bool:
        """Post a comment on a GitHub issue"""
        
        token = await self.get_installation_token(installation_id)
        if not token:
            return False
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{issue_number}/comments",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                json={"body": comment_body}
            )
            
            return response.status_code == 201
    
    async def add_labels(
        self,
        installation_id: int,
        repo_owner: str,
        repo_name: str,
        issue_number: int,
        labels: list
    ) -> bool:
        """Add labels to a GitHub issue"""
        
        token = await self.get_installation_token(installation_id)
        if not token:
            return False
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{issue_number}/labels",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                json={"labels": labels}
            )
            
            return response.status_code == 200


# Global instance
github_app = GitHubAppService()
