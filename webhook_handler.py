from fastapi import FastAPI, Request
import yaml
import logging
from gitlab_client import get_changed_files, get_file_content, post_comment
from llm_agent import review_file_content

app = FastAPI()
logging.basicConfig(level=logging.INFO)

@app.post("/webhook")
async def handle_webhook(request: Request):
    payload = await request.json()
    event_type = request.headers.get("X-Gitlab-Event")

    if event_type == "Merge Request Hook":
        mr = payload['object_attributes']
        mr_iid = mr['iid']
        source_branch = mr['source_branch']

        logging.info(f"Nouvelle MR reçue: {mr['title']} (IID: {mr_iid})")

        changed_files = get_changed_files(mr_iid)
        logging.info(f"Fichiers modifiés: {changed_files}")

        for file_path in changed_files:
            content = get_file_content(source_branch, file_path)
            if content:
                # Faire la revue avec le LLM
                review_comment = review_file_content(file_path, content)

                # Poster le commentaire sur la MR
                response = post_comment(mr_iid, review_comment)
                if response:
                    logging.info(f"Commentaire posté sur la MR pour {file_path}")
                else:
                    logging.error(f"Impossible de poster le commentaire pour {file_path}")

    return {"status": "received"}
