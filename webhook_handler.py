from fastapi import FastAPI, Request
import yaml
import logging
from gitlab_client import get_changed_files

with open("config.yml", "r") as f:
    config = yaml.safe_load(f)

app = FastAPI()
logging.basicConfig(level=logging.INFO)

@app.post("/webhook")
async def handle_webhook(request: Request):
    payload = await request.json()
    event_type = request.headers.get("X-Gitlab-Event")

    if event_type == "Merge Request Hook":
        mr = payload['object_attributes']
        mr_iid = mr['iid']  # Important : c'est l'IID, pas l'ID global

        logging.info(f"Nouvelle MR reçue: {mr['title']} (IID: {mr_iid})")

        # Récupérer les fichiers modifiés
        changed_files = get_changed_files(mr_iid)
        logging.info(f"Fichiers modifiés: {changed_files}")

    return {"status": "received"}
