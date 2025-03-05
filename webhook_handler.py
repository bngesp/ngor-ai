from fastapi import FastAPI, Request
import yaml
import logging

# Charger la config
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
        logging.info(f"Nouvelle MR reçue: {mr['title']} (#{mr['id']})")
        logging.info(f"Description: {mr['description']}")
        logging.info(f"Source branch: {mr['source_branch']} → Target branch: {mr['target_branch']}")
        logging.info(f"MR Status: {mr['state']}")

    return {"status": "received"}
