import requests
from typing import List, Dict, Any, Optional
from app.models.config import GitLabConfig
from app.models.gitlab import MergeRequest, Change, CodeComment

class GitLabClient:
    """Client for interacting with GitLab API"""
    
    def __init__(self, config: GitLabConfig):
        self.config = config
        self.api_url = config.api_url.rstrip('/')
        self.headers = {
            'PRIVATE-TOKEN': config.access_token,
            'Content-Type': 'application/json'
        }
    
    def validate_webhook_signature(self, secret_token: str, gitlab_token: str) -> bool:
        """Validate the GitLab webhook signature"""
        if not self.config.webhook_secret:
            return True  # No validation if no secret is configured
        
        return self.config.webhook_secret == gitlab_token
    
    def get_merge_request(self, project_id: int, mr_iid: int) -> Optional[MergeRequest]:
        """Get detailed merge request information"""
        url = f"{self.api_url}/projects/{project_id}/merge_requests/{mr_iid}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            return None
            
        data = response.json()
        return self._build_merge_request(data)
    
    def get_merge_request_changes(self, project_id: int, mr_iid: int) -> List[Change]:
        """Get changes (diffs) for a merge request"""
        url = f"{self.api_url}/projects/{project_id}/merge_requests/{mr_iid}/changes"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            return []
            
        data = response.json()
        changes = []
        
        for change in data.get('changes', []):
            changes.append(Change(
                old_path=change.get('old_path'),
                new_path=change.get('new_path'),
                a_mode=change.get('a_mode'),
                b_mode=change.get('b_mode'),
                diff=change.get('diff', ''),
                new_file=change.get('new_file', False),
                renamed_file=change.get('renamed_file', False),
                deleted_file=change.get('deleted_file', False)
            ))
            
        return changes
    
    def add_comment(self, project_id: int, mr_iid: int, comment: CodeComment) -> bool:
        """Add a comment to a merge request"""
        url = f"{self.api_url}/projects/{project_id}/merge_requests/{mr_iid}/notes"
        
        payload = {
            'body': comment.note
        }
        
        # If this is a line-specific comment
        if comment.line and comment.path:
            if comment.position:
                payload['position'] = comment.position
            else:
                # Create a position object for the comment
                payload['position'] = {
                    'base_sha': None,  # Will be filled by GitLab
                    'start_sha': None,  # Will be filled by GitLab
                    'head_sha': None,  # Will be filled by GitLab
                    'position_type': 'text',
                    'new_path': comment.path,
                    'old_path': comment.path,
                    'new_line': comment.line if comment.line_type == 'new' else None,
                    'old_line': comment.line if comment.line_type == 'old' else None,
                }
        
        response = requests.post(url, headers=self.headers, json=payload)
        return response.status_code in (200, 201)
    
    def _build_merge_request(self, data: Dict[str, Any]) -> MergeRequest:
        """Build a MergeRequest object from API response"""
        # Implementation depends on the exact API response format
        # This is a simplified version
        from app.models.gitlab import User
        from datetime import datetime
        
        return MergeRequest(
            id=data.get('id'),
            iid=data.get('iid'),
            project_id=data.get('project_id'),
            title=data.get('title'),
            description=data.get('description'),
            state=data.get('state'),
            created_at=datetime.fromisoformat(data.get('created_at').replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(data.get('updated_at').replace('Z', '+00:00')),
            source_branch=data.get('source_branch'),
            target_branch=data.get('target_branch'),
            author=User(
                id=data.get('author', {}).get('id'),
                name=data.get('author', {}).get('name'),
                username=data.get('author', {}).get('username'),
                avatar_url=data.get('author', {}).get('avatar_url')
            ),
            web_url=data.get('web_url')
        )