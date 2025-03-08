from fastapi import FastAPI, Request

from core.gitlab_client import get_changed_files
from core.review_manager import MergeRequest
from core.review_manager import process_merge_request
import logging

app = FastAPI()


@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.json()
    logging.info(f"Requête reçue: {payload}")
    if request.headers.get("X-Gitlab-Event") != "Merge Request Hook":
        return {"status": "ignored"}

    mr_data = payload['object_attributes']
    logging.info(f"Webhook reçu pour la MR: {mr_data['iid']}")
    try:
        logging.info(f"Traitement de la MR: {mr_data['iid']}")
        changed_files = get_changed_files(mr_data['iid'])
        # mr = MergeRequest(
        #     iid=mr_data['iid'],
        #     source_branch=mr_data['source_branch'],
        #     base_sha=mr_data['diff_refs']['base_sha'],
        #     start_sha=mr_data['diff_refs']['start_sha'],
        #     head_sha=mr_data['diff_refs']['head_sha']
        # )
        logging.info(f"Fichiers modifiés: {changed_files}")
        # process_merge_request(mr)
    except Exception as e:
        logging.error(f"Erreur lors du traitement de la MR: {e}")

    return {"status": "processed"}
