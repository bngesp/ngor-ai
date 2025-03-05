import logging
from core.gitlab_client import get_changed_files, get_file_content, post_diff_comment
from core.llm_agent import review_file_content


class MergeRequest:
    def __init__(self, iid, source_branch, base_sha, start_sha, head_sha):
        self.iid = iid
        self.source_branch = source_branch
        self.base_sha = base_sha
        self.start_sha = start_sha
        self.head_sha = head_sha


def process_merge_request(mr):
    changes = get_changed_files(mr.iid)

    for change in changes:
        file_path = change['new_path']
        file_content = get_file_content(mr.source_branch, file_path)

        if file_content:
            comments = review_file_content(file_path, file_content)

            for line_number, comment in comments.items():
                post_diff_comment(mr, file_path, line_number, comment)
                logging.info(f"Commentaire ajouté sur {file_path} ligne {line_number}")
