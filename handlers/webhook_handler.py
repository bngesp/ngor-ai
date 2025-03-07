from fastapi import FastAPI, Request

from core.review_manager import MergeRequest
from core.review_manager import process_merge_request
import logging

app = FastAPI()


@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.json()
    if request.headers.get("X-Gitlab-Event") != "Merge Request Hook":
        return {"status": "ignored"}

    mr_data = payload['object_attributes']
    logging.info(f"Webhook reçu pour la MR: {mr_data['iid']}")
    try:
        logging.info(f"Traitement de la MR: {mr_data['iid']}")
        mr = MergeRequest(
            iid=mr_data['iid'],
            source_branch=mr_data['source_branch'],
            base_sha=mr_data['target']['commit']['sha'],
            start_sha=mr_data['source']['commit']['sha'],
            head_sha=mr_data['last_commit']['id']
        )

        process_merge_request(mr)
    except Exception as e:
        logging.error(f"Erreur lors du traitement de la MR: {e}")

    return {"status": "processed"}
