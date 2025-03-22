# Ngor-AI

Ngor-ai est un systeme multiagent ia qui sont des tech lead et 
sont responsable de faire le review de code. 
L'idée est de connecté à gitlab par webhook et quand il y'a un merge request il recupere les diff 
et les envoyé à un llm via un prompt spécialisé et recuperer la reponse et mettre un commentaire. 
Cet agent ia a été ecris en python. 

Voici les différentes étapes et fonctionnalités clés pour Ngor-AI :

## Connexion à GitLab via Webhook
Configurer un webhook GitLab pour détecter les événements de merge request.

Filtrer les événements pertinents (ex : merge_request_opened, merge_request_updated).

Récupérer les informations essentielles (auteur, source branch, target branch, modifications).

## Récupération des Diffs
Extraire les fichiers modifiés et leurs diffs.

Identifier les ajouts, suppressions et modifications ligne par ligne.

Traiter les fichiers volumineux en les découpant si nécessaire.

## Envoi au LLM
Construire un prompt structuré :

Contexte du projet.

Style de code attendu.

Règles spécifiques (standards internes, conventions).

Liste des diffs à analyser.

Gérer les limitations de tokens en segmentant les requêtes.

## Analyse et Génération des Commentaires
Récupérer la réponse du LLM.

Extraire les suggestions pertinentes et les associer aux lignes de code concernées.

Filtrer les commentaires inutiles ou redondants.

Prioriser les problèmes critiques (sécurité, performance, bugs).

## Ajout des Commentaires sur GitLab
Utiliser l’API GitLab pour publier les commentaires sur la merge request.

Associer chaque commentaire à la bonne ligne du diff.

Gérer les erreurs d’API et les quotas de requêtes.

## Interface de Configuration et Personnalisation
Permettre d’adapter les règles de revue selon le projet.

Option pour activer/désactiver l’IA selon les types de fichiers.

Tableau de bord pour voir les analyses passées.

## Sécurité et Performance
Stocker les tokens GitLab de manière sécurisée.

Limiter les appels API pour éviter les surcharges.

Gérer les erreurs réseau et les cas où l’IA ne répond pas.

## Améliorations Futures
Intégrer un apprentissage basé sur les feedbacks des développeurs.

Ajouter des analyses spécifiques (détection de code smells, vulnérabilités).

Supporter d'autres plateformes (GitHub, Bitbucket).