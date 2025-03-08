import requests
import base64
import logging
from config.settings import GITLAB_API_BASE_URL, GITLAB_PROJECT_ID, HEADERS


def get_changed_files(mr_iid):
    url = f"{GITLAB_API_BASE_URL}/projects/{GITLAB_PROJECT_ID}/merge_requests/{mr_iid}/changes"
    response = requests.get(url, headers=HEADERS)
    logging.info(f"Récupération des fichiers modifiés pour la MR {mr_iid}")
    if response.status_code != 200:
        logging.error(f"Erreur GitLab: {response.status_code} - {response.text}")
        return []
    return response.json()['changes']


def get_file_content(branch, file_path):
    url = f"{GITLAB_API_BASE_URL}/projects/{GITLAB_PROJECT_ID}/repository/files/{file_path}?ref={branch}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        logging.error(f"Erreur lecture fichier {file_path}: {response.status_code}")
        return None
    return base64.b64decode(response.json()['content']).decode('utf-8')


def post_diff_comment(mr, file_path, line_number, comment):
    url = f"{GITLAB_API_BASE_URL}/projects/{GITLAB_PROJECT_ID}/merge_requests/{mr.iid}/discussions"

    data = {
        "body": comment,
        "position": {
            "base_sha": mr.base_sha,
            "start_sha": mr.start_sha,
            "head_sha": mr.head_sha,
            "new_path": file_path,
            "new_line": line_number
        }
    }

    response = requests.post(url, headers=HEADERS, json=data)
    if response.status_code != 201:
        logging.error(f"Erreur lors de la création du commentaire: {response.status_code} - {response.text}")
        return None
    return response.json()
