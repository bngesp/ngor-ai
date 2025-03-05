import yaml
import requests
import logging

# Charger la config
with open("config.yml", "r") as f:
    config = yaml.safe_load(f)

GITLAB_API_BASE = "https://gitlab.com/api/v4"
PROJECT_ID = config['gitlab']['project_id']
PRIVATE_TOKEN = config['gitlab']['token']

HEADERS = {
    "PRIVATE-TOKEN": PRIVATE_TOKEN
}

def get_changed_files(mr_iid):
    """
    Récupère les fichiers modifiés dans une MR donnée (par IID de la MR).
    """
    url = f"{GITLAB_API_BASE}/projects/{PROJECT_ID}/merge_requests/{mr_iid}/changes"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        logging.error(f"Erreur API GitLab: {response.status_code} - {response.text}")
        return []

    data = response.json()
    return [change['new_path'] for change in data['changes']]
