import openai
import logging
from config.settings import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


def review_file_content(file_path, content):
    prompt = f"""
    Tu es un expert en code review. Analyse le fichier {file_path} et signale les lignes problématiques.

    Format attendu:
    ligne: numéro | commentaire: explication claire du problème

    Contenu du fichier:
    {content}
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es un tech lead qui fait des revues de code."},
                {"role": "user", "content": prompt}
            ]
        )

        review_text = response['choices'][0]['message']['content']
        comments = {}

        for line in review_text.split("\n"):
            if line.startswith("ligne:"):
                try:
                    parts = line.split("|")
                    line_number = int(parts[0].split(":")[1].strip())
                    comment = parts[1].split("commentaire:")[1].strip()
                    comments[line_number] = comment
                except Exception as e:
                    logging.warning(f"Impossible de parser la ligne: {line}")

        return comments

    except Exception as e:
        logging.error(f"Erreur lors de la review par LLM: {e}")
        return {}
