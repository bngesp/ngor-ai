# Ngor-AI

Ngor-AI est un système multi-agent IA agissant comme des tech leads responsables de faire la revue de code. 

L'idée est de se connecter à GitLab via des webhooks et, lorsqu'une merge request est créée, de récupérer les diffs, les envoyer à un LLM via un prompt spécialisé, récupérer la réponse et ajouter des commentaires pertinents.

## Fonctionnalités

- 🔄 Connexion à GitLab via webhook pour détecter les merge requests
- 📝 Extraction et analyse des diffs de code
- 🧠 Analyse par IA utilisant des LLMs (comme GPT-4)
- 💬 Génération de commentaires de revue de code pertinents
- 🔗 Publication automatique des commentaires sur la merge request
- ⚙️ Configuration personnalisable pour différents projets et langages

## Installation

```bash
# Cloner le repository
git clone https://github.com/yourusername/ngor-ai.git
cd ngor-ai

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer le fichier .env avec vos propres clés et configurations
```

## Configuration

Modifiez le fichier `.env` pour configurer l'application :

```
# GitLab Configuration
GITLAB_API_URL=https://gitlab.com/api/v4
GITLAB_ACCESS_TOKEN=your_personal_access_token
GITLAB_WEBHOOK_SECRET=your_webhook_secret
GITLAB_PROJECT_IDS=123,456  # Comma-separated list of project IDs to monitor

# LLM Configuration
OPENAI_API_KEY=your_openai_api_key
LLM_MODEL_NAME=gpt-4  # or anthropic-claude-3-sonnet, etc.
LLM_MAX_TOKENS=4000
LLM_TEMPERATURE=0.1

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

## Utilisation

### Étapes de lancement

1. **Préparer l'environnement**
   ```bash
   # Activer l'environnement virtuel si ce n'est pas déjà fait
   source venv/bin/activate  # Sur Windows: venv\Scripts\activate
   ```

2. **Vérifier la configuration**
   ```bash
   # Assurez-vous que le fichier .env est correctement configuré
   cat .env
   ```

3. **Démarrer le serveur**
   ```bash
   # Lancer l'application
   python -m app.main
   ```

4. **Vérifier que le serveur est en marche**
   ```bash
   # Tester que l'API répond
   curl http://localhost:8000/health
   # Vous devriez voir: {"status":"healthy"}
   ```

Le serveur démarrera sur `http://0.0.0.0:8000` par défaut (ou selon vos paramètres HOST et PORT).

### Configuration du webhook GitLab

1. Dans votre projet GitLab, allez dans Settings > Webhooks
2. Ajoutez un nouveau webhook avec l'URL de votre instance Ngor-AI (ex: `https://votre-domaine.com/api/v1/gitlab-webhook`)
3. Sélectionnez le trigger `Merge request events`
4. Ajoutez le secret défini dans votre fichier .env comme "Secret Token"
5. Sauvegarder le webhook

### Tester le webhook

1. Créez une merge request test dans votre projet GitLab
2. Vérifiez les logs de Ngor-AI pour confirmer que l'événement a été reçu:
   ```bash
   # Dans un terminal séparé
   tail -f ngor-ai.log  # Si vous avez configuré un fichier de log
   ```
3. Vérifiez sur GitLab que des commentaires ont été ajoutés à la merge request

## Déploiement en production

Pour un déploiement en production, nous recommandons:

1. **Utiliser un serveur WSGI/ASGI**
   ```bash
   # Exemple avec Gunicorn
   pip install gunicorn
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
   ```

2. **Configurer un proxy inverse (Nginx ou similaire)**
   
3. **Configurer SSL pour les connexions sécurisées**

4. **Utiliser un gestionnaire de processus comme Supervisor**
   ```
   [program:ngor-ai]
   command=/chemin/vers/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
   directory=/chemin/vers/ngor-ai
   user=www-data
   autostart=true
   autorestart=true
   stopasgroup=true
   killasgroup=true
   ```

## Tests

```bash
# Exécuter tous les tests
python -m unittest discover

# Exécuter un test spécifique
python -m unittest tests.test_llm_service
```

## Personnalisation

Vous pouvez personnaliser les règles de revue de code en modifiant les paramètres dans `app/models/config.py`.

## Contribuer

Les contributions sont les bienvenues ! Veuillez ouvrir une issue ou une pull request pour toute amélioration ou correction de bug.

## Licence

MIT License