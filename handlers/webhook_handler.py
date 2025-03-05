from fastapi import FastAPI, Request
import logging
from core.review_manager import process_merge_request

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

        process_merge_request(mr_iid, source_branch)

    return {"status": "received"}
