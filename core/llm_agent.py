import logging
import openai
from config.settings import settings

openai.api_key = settings.openai_api_key

def load_base_prompt():
    with open("prompts/base_prompt.md", "r", encoding="utf-8") as f:
        return f.read()

def review_file_content(file_path, content):
    try:
        base_prompt = load_base_prompt()
        full_prompt = base_prompt.format(file_path=file_path, content=content)

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es un tech lead expert qui fait des revues de code."},
                {"role": "user", "content": full_prompt}
            ]
        )

        review = response['choices'][0]['message']['content']
        return f"### Review de code pour {file_path} :\n\n{review}"

    except Exception as e:
        logging.error(f"Erreur lors de la review LLM : {e}")
        return "Impossible de générer une review pour ce fichier."
