from pydantic import BaseSettings

class Settings(BaseSettings):
    gitlab_api_base_url: str
    gitlab_project_id: str
    gitlab_project_token: str
    openai_api_key: str

    class Config:
        env_file = ".env"

settings = Settings()
