import os
from dotenv import load_dotenv

load_dotenv()

GITLAB_API_BASE_URL = os.getenv("GITLAB_API_BASE_URL")
GITLAB_PROJECT_ID = os.getenv("GITLAB_PROJECT_ID")
GITLAB_PROJECT_TOKEN = os.getenv("GITLAB_PROJECT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

HEADERS = {
    "PRIVATE-TOKEN": GITLAB_PROJECT_TOKEN
}
