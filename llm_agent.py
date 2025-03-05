import openai
import yaml
import logging

with open("config.yml", "r") as f:
    config = yaml.safe_load(f)

#openai.api_key = config['openai']['api_key']
openai.api_key = "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"

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
