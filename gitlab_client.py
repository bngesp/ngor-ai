import yaml
import requests
import logging

with open("config.yml", "r") as f:
    config = yaml.safe_load(f)

GITLAB_API_BASE = "https://gitlab.com/api/v4"
PROJECT_ID = config['gitlab']['project_id']
PRIVATE_TOKEN = config['gitlab']['token']

HEADERS = {
    "PRIVATE-TOKEN": PRIVATE_TOKEN
}

def get_changed_files(mr_iid):
    url = f"{GITLAB_API_BASE}/projects/{PROJECT_ID}/merge_requests/{mr_iid}/changes"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        logging.error(f"Erreur API GitLab: {response.status_code} - {response.text}")
        return []

    data = response.json()
    return [change['new_path'] for change in data['changes']]

def get_file_content(branch, file_path):
    """
    Récupère le contenu d'un fichier sur une branche donnée.
    """
    url = f"{GITLAB_API_BASE}/projects/{PROJECT_ID}/repository/files/{file_path}?ref={branch}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        logging.error(f"Impossible de récupérer le fichier {file_path}: {response.status_code} - {response.text}")
        return None

    file_data = response.json()
    import base64
    return base64.b64decode(file_data['content']).decode('utf-8')


def post_comment(mr_iid, comment):
    """
    Poste un commentaire sur la Merge Request spécifiée.
    """
    url = f"{GITLAB_API_BASE}/projects/{PROJECT_ID}/merge_requests/{mr_iid}/notes"
    data = {
        "body": comment
    }
    response = requests.post(url, headers=HEADERS, data=data)

    if response.status_code != 201:
        logging.error(f"Erreur lors du post du commentaire: {response.status_code} - {response.text}")
        return None

    return response.json()
