from fastapi import APIRouter, Request, HTTPException, Header, Depends
from typing import Optional, Dict, Any
from app.models.gitlab import MergeRequestEvent
from app.services.code_review_service import CodeReviewService
from app.models.config import AppConfig
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

def get_config() -> AppConfig:
    """Dependency to get application configuration"""
    # This would typically load from a file or environment variables
    # For simplicity, we're mocking it here
    from app.models.config import GitLabConfig, LLMConfig, CodeReviewConfig
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    return AppConfig(
        gitlab=GitLabConfig(
            api_url=os.getenv("GITLAB_API_URL", "https://gitlab.com/api/v4"),
            access_token=os.getenv("GITLAB_ACCESS_TOKEN", ""),
            webhook_secret=os.getenv("GITLAB_WEBHOOK_SECRET", None),
            project_ids=[int(id) for id in os.getenv("GITLAB_PROJECT_IDS", "").split(",") if id]
        ),
        llm=LLMConfig(
            api_key=os.getenv("OPENAI_API_KEY", ""),
            model_name=os.getenv("LLM_MODEL_NAME", "gpt-4"),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "4000")),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.1"))
        ),
        code_review=CodeReviewConfig()
    )

def get_code_review_service(config: AppConfig = Depends(get_config)) -> CodeReviewService:
    """Dependency to get the code review service"""
    return CodeReviewService(config)

@router.post("/gitlab-webhook")
async def gitlab_webhook(
    request: Request,
    x_gitlab_token: Optional[str] = Header(None),
    x_gitlab_event: Optional[str] = Header(None),
    code_review_service: CodeReviewService = Depends(get_code_review_service),
    config: AppConfig = Depends(get_config)
):
    """Handle GitLab webhook events"""
    try:
        # Validate webhook token if configured
        if config.gitlab.webhook_secret and x_gitlab_token != config.gitlab.webhook_secret:
            logger.warning("Invalid GitLab webhook token")
            raise HTTPException(status_code=401, detail="Invalid webhook token")
        
        # Check event type
        if x_gitlab_event != "Merge Request Hook":
            return {"status": "skipped", "reason": f"Event type '{x_gitlab_event}' not supported"}
        
        # Parse the payload
        payload = await request.json()
        event = MergeRequestEvent(**payload)
        
        # Get the merge request attributes
        attrs = event.object_attributes
        
        # Check if this is an event we care about
        if attrs.get("action") not in ["open", "update", "reopen"]:
            return {"status": "skipped", "reason": f"Action '{attrs.get('action')}' not supported"}
        
        # Check if the project is in our monitored list
        project_id = event.project.get("id")
        if config.gitlab.project_ids and project_id not in config.gitlab.project_ids:
            return {"status": "skipped", "reason": "Project not in monitored list"}
        
        # Process the merge request
        mr_iid = attrs.get("iid")
        success = await code_review_service.process_merge_request(project_id, mr_iid)
        
        if success:
            return {"status": "success", "message": f"Processed merge request {project_id}/{mr_iid}"}
        else:
            return {"status": "error", "message": f"Failed to process merge request {project_id}/{mr_iid}"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")