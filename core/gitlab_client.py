import logging
import requests
from config.settings import settings
import base64

HEADERS = {"PRIVATE-TOKEN": settings.gitlab_project_token}

def get_changed_files(mr_iid):
    url = f"{settings.gitlab_api_base_url}/projects/{settings.gitlab_project_id}/merge_requests/{mr_iid}/changes"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        logging.error(f"Erreur API GitLab: {response.status_code} - {response.text}")
        return []

    data = response.json()
    return [change['new_path'] for change in data['changes']]

def get_file_content(branch, file_path):
    url = f"{settings.gitlab_api_base_url}/projects/{settings.gitlab_project_id}/repository/files/{file_path}?ref={branch}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        logging.error(f"Impossible de récupérer le fichier {file_path}: {response.status_code} - {response.text}")
        return None

    file_data = response.json()
    return base64.b64decode(file_data['content']).decode('utf-8')

def post_comment(mr_iid, comment):
    url = f"{settings.gitlab_api_base_url}/projects/{settings.gitlab_project_id}/merge_requests/{mr_iid}/notes"
    data = {"body": comment}
    response = requests.post(url, headers=HEADERS, data=data)

    if response.status_code != 201:
        logging.error(f"Erreur lors du post du commentaire: {response.status_code} - {response.text}")
        return None

    return response.json()
