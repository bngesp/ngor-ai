from typing import List, Dict, Any
from app.models.gitlab import MergeRequest, Change, CodeComment
from app.models.config import AppConfig
from app.utils.diff_processor import DiffProcessor
from app.utils.gitlab_client import GitLabClient
from app.utils.llm_service import LLMService
import logging

logger = logging.getLogger(__name__)

class CodeReviewService:
    """Service for performing code reviews on merge requests"""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.gitlab_client = GitLabClient(config.gitlab)
        self.llm_service = LLMService(config.llm)
        self.diff_processor = DiffProcessor(config.code_review)
    
    async def process_merge_request(self, project_id: int, mr_iid: int) -> bool:
        """Process a merge request and add code review comments"""
        try:
            # Get merge request details
            merge_request = self.gitlab_client.get_merge_request(project_id, mr_iid)
            
            if not merge_request:
                logger.error(f"Could not retrieve merge request {project_id}/{mr_iid}")
                return False
                
            # Get the changes/diffs
            changes = self.gitlab_client.get_merge_request_changes(project_id, mr_iid)
            
            if not changes:
                logger.info(f"No changes found for merge request {project_id}/{mr_iid}")
                return True
                
            # Filter changes according to configuration
            filtered_changes = self.diff_processor.filter_changes(changes)
            
            if not filtered_changes:
                logger.info(f"No changes to review after filtering for merge request {project_id}/{mr_iid}")
                return True
                
            # Generate code review comments
            comments = self.llm_service.generate_code_review(
                filtered_changes, 
                self.config.code_review.review_guidelines
            )
            
            if not comments:
                logger.info(f"No comments generated for merge request {project_id}/{mr_iid}")
                return True
                
            # Add comments to the merge request
            self._add_comments_to_merge_request(project_id, mr_iid, comments)
            
            return True
        except Exception as e:
            logger.exception(f"Error processing merge request {project_id}/{mr_iid}: {e}")
            return False
    
    def _add_comments_to_merge_request(self, project_id: int, mr_iid: int, comments: List[CodeComment]) -> None:
        """Add comments to the merge request"""
        # Add a summary comment first
        summary = self._generate_summary_comment(comments)
        summary_comment = CodeComment(
            note=summary,
            path=None  # General comment, not tied to a specific file
        )
        
        self.gitlab_client.add_comment(project_id, mr_iid, summary_comment)
        
        # Add individual line comments
        for comment in comments:
            if comment.line:  # Only add line-specific comments
                self.gitlab_client.add_comment(project_id, mr_iid, comment)
    
    def _generate_summary_comment(self, comments: List[CodeComment]) -> str:
        """Generate a summary comment from all review comments"""
        # Count issues by type
        categories = {}
        
        for comment in comments:
            # Simple categorization based on keywords in the comment
            text = comment.note.lower()
            
            if any(keyword in text for keyword in ["secur", "vulnerab", "inject", "auth"]):
                categories["Security"] = categories.get("Security", 0) + 1
            elif any(keyword in text for keyword in ["bug", "error", "exception", "crash", "fix"]):
                categories["Bugs"] = categories.get("Bugs", 0) + 1
            elif any(keyword in text for keyword in ["perform", "speed", "slow", "optim"]):
                categories["Performance"] = categories.get("Performance", 0) + 1
            elif any(keyword in text for keyword in ["style", "naming", "format", "indent", "spacing"]):
                categories["Style"] = categories.get("Style", 0) + 1
            elif any(keyword in text for keyword in ["document", "comment", "clarif"]):
                categories["Documentation"] = categories.get("Documentation", 0) + 1
            else:
                categories["Other"] = categories.get("Other", 0) + 1
        
        # Build the summary message
        summary = "## Ngor-AI Code Review Summary\n\n"
        summary += f"I've reviewed the code changes and found **{len(comments)}** potential issues.\n\n"
        
        if categories:
            summary += "### Issues by Category:\n\n"
            for category, count in categories.items():
                summary += f"- **{category}**: {count}\n"
        
        # Add explanation and disclaimer
        summary += "\n### Note:\n\n"
        summary += "I've added specific comments to the relevant lines of code. "
        summary += "Please review each comment and address the issues as appropriate. "
        summary += "Remember that these are suggestions based on static analysis and "
        summary += "may require human judgment to evaluate.\n\n"
        summary += "_This review was generated by Ngor-AI, an automated code review assistant._"
        
        return summary