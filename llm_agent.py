import openai
import yaml
import logging

with open("config.yml", "r") as f:
    config = yaml.safe_load(f)

openai.api_key = config['openai']['api_key']

def review_file_content(file_path, content):
    """
    Envoie le contenu d'un fichier au LLM pour review.
    Retourne les commentaires/recommandations du modèle.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es un tech lead expert qui fait des revues de code."},
                {"role": "user", "content": f"Voici le contenu du fichier {file_path}:\n\n{content}\n\nPeux-tu analyser ce fichier et donner des suggestions de code review (problèmes de style, de performance, de sécurité, de documentation, etc.) ?"}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        logging.error(f"Erreur lors de la review LLM : {e}")
        return "Impossible de générer une review pour ce fichier."
