# Walkthrough - Système de Collecte de Feedback

Nous avons implémenté un système de feedback complet (Thumbs Up/Down) pour capturer la qualité des réponses générées par le moteur RAG et permettre un futur affinement ("nourrir le moteur").

## Fonctionnalités Implémentées

### 1. Backend : API de Feedback
- **Schema** : Création de `FeedbackRequest` pour valider l'envoi de la question, de la réponse, du score (`up`/`down`) et du profil utilisateur.
- **Service** : Implémentation de `save_feedback` qui journalise les données en mode "append" dans le fichier `backend/data/feedback.jsonl`.
- **Endpoint** : Ajout de la route `POST /chat/feedback` dans le contrôleur de chat.

### 2. Frontend : Intégration UI
- **Capture du contexte** : La fonction `handleFeedbackSubmit` dans `ChatPage.jsx` identifie automatiquement la question posée par l'utilisateur (le message précédent) et la réponse de l'assistant pour les envoyer au backend.
- **Réactivité** : L'interface utilisateur est mise à jour instantanément lors du clic pour confirmer la prise en compte du feedback.

## Vérification Technique

Le succès du système a été validé par un script de test dédié :
- **Endpoint** : Réponse `200 OK` avec le statut `success`.
- **Persistance** : Vérification manuelle de l'écriture dans `backend/data/feedback.jsonl`.

```json
{
  "timestamp": "2026-04-02T01:13:03.123Z",
  "question": "Comment faire la priere ?",
  "answer": "La priere (Salat) se fait en plusieurs etapes...",
  "feedback": "up",
  "profile": { ... }
}
```

## Prochaines Étapes
Les données accumulées dans `feedback.jsonl` pourront être utilisées pour :
1. Identifier les réponses jugées "imprécises" et ajuster le prompt système.
2. Créer un dataset de paires Question/Verset idéales pour le Fine-Tuning ou l'optimisation des embeddings.
