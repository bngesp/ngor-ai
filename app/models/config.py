from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class GitLabConfig(BaseModel):
    """Configuration for GitLab connection"""
    api_url: str = Field(..., description="GitLab API URL")
    access_token: str = Field(..., description="GitLab personal access token")
    webhook_secret: Optional[str] = Field(None, description="Secret token for webhook validation")
    project_ids: List[int] = Field(default_factory=list, description="List of project IDs to monitor")

class LLMConfig(BaseModel):
    """Configuration for LLM service"""
    api_key: str = Field(..., description="API key for the LLM service")
    model_name: str = Field("gpt-4", description="Model name to use")
    max_tokens: int = Field(4000, description="Maximum tokens per request")
    temperature: float = Field(0.1, description="Temperature for response generation")

class CodeReviewConfig(BaseModel):
    """Configuration for code review rules"""
    file_extensions: List[str] = Field(
        default_factory=lambda: [".py", ".js", ".ts", ".java", ".go", ".rb", ".php", ".cs"],
        description="File extensions to review"
    )
    excluded_paths: List[str] = Field(
        default_factory=lambda: ["node_modules/", "vendor/", "dist/", "build/"],
        description="Paths to exclude from review"
    )
    max_files_per_review: int = Field(20, description="Maximum number of files to review")
    max_lines_per_file: int = Field(500, description="Maximum lines per file to review")
    review_guidelines: Dict[str, str] = Field(
        default_factory=dict,
        description="Language-specific review guidelines"
    )

class AppConfig(BaseModel):
    """Main application configuration"""
    gitlab: GitLabConfig
    llm: LLMConfig
    code_review: CodeReviewConfig