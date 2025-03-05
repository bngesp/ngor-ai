import logging
from core.gitlab_client import get_changed_files, get_file_content, post_comment
from core.llm_agent import review_file_content

def process_merge_request(mr_iid, source_branch):
    changed_files = get_changed_files(mr_iid)
    logging.info(f"Fichiers modifiés: {changed_files}")

    for file_path in changed_files:
        content = get_file_content(source_branch, file_path)
        if content:
            review_comment = review_file_content(file_path, content)
            response = post_comment(mr_iid, review_comment)

            if response:
                logging.info(f"Commentaire posté sur la MR pour {file_path}")
            else:
                logging.error(f"Impossible de poster le commentaire pour {file_path}")
