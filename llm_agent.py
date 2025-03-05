import logging
import os

import openai
from dotenv import load_dotenv

load_dotenv()


openai.api_key = os.getenv("OPENAI_API_KEY")

def review_file_content(file_path, content):
    """
    Envoie le contenu d'un fichier au LLM pour review.
    Retourne les commentaires/recommandations du modèle.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un tech lead expert qui fait des revues de code."},
                {"role": "user", "content": f"Voici le contenu du fichier {file_path}:\n\n{content}\n\nPeux-tu analyser ce fichier et donner des suggestions de code review (problèmes de style, de performance, de sécurité, de documentation, etc.) ?"}
            ]
        )
        review = response['choices'][0]['message']['content']
        structured_comment = f"### Review de code pour {file_path} :\n\n{review}"
        return structured_comment
    except Exception as e:
        logging.error(f"Erreur lors de la review LLM : {e}")
        return "Impossible de générer une review pour ce fichier."
