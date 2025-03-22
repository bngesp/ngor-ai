from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class User(BaseModel):
    """GitLab user information"""
    id: int
    name: str
    username: str
    avatar_url: Optional[str] = None

class Change(BaseModel):
    """File change information"""
    old_path: str
    new_path: str
    a_mode: Optional[str] = None
    b_mode: Optional[str] = None
    diff: str
    new_file: bool = False
    renamed_file: bool = False
    deleted_file: bool = False

class MergeRequest(BaseModel):
    """GitLab merge request information"""
    id: int
    iid: int  # Internal ID within a project
    project_id: int
    title: str
    description: Optional[str] = None
    state: str
    created_at: datetime
    updated_at: datetime
    source_branch: str
    target_branch: str
    author: User
    assignees: List[User] = Field(default_factory=list)
    reviewers: List[User] = Field(default_factory=list)
    web_url: str
    changes: List[Change] = Field(default_factory=list)

class MergeRequestEvent(BaseModel):
    """GitLab merge request webhook event"""
    object_kind: str
    event_type: str
    user: User
    project: Dict[str, Any]
    object_attributes: Dict[str, Any]
    changes: Dict[str, Any] = Field(default_factory=dict)
    
    def to_merge_request(self) -> MergeRequest:
        """Convert webhook event to MergeRequest model"""
        attrs = self.object_attributes
        return MergeRequest(
            id=attrs.get("id"),
            iid=attrs.get("iid"),
            project_id=self.project.get("id"),
            title=attrs.get("title"),
            description=attrs.get("description"),
            state=attrs.get("state"),
            created_at=datetime.fromisoformat(attrs.get("created_at").replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(attrs.get("updated_at").replace("Z", "+00:00")),
            source_branch=attrs.get("source_branch"),
            target_branch=attrs.get("target_branch"),
            author=User(
                id=self.user.get("id"),
                name=self.user.get("name"),
                username=self.user.get("username"),
                avatar_url=self.user.get("avatar_url")
            ),
            web_url=attrs.get("url")
        )

class CodeComment(BaseModel):
    """Code review comment model"""
    note: str
    path: Optional[str] = None
    line: Optional[int] = None
    line_type: str = "new"  # "new" or "old"
    position: Optional[Dict[str, Any]] = None