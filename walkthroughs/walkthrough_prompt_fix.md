# Walkthrough - Affinement du Prompt par les Feedbacks

Grâce au système de feedback (Thumb Down) implémenté, nous avons identifié et corrigé une erreur doctrinale majeure sur la fréquence du Hajj.

## Problématique Identifiée
- **Question** : "Est-ce que le Hajj est obligatoire ?"
- **Erreur** : Le modèle affirmait que le Hajj était "obligatoire chaque année" en interprétant mal des hadiths conditionnels ("Si j'avais dit oui...").
- **Cause** : Faiblesse de raisonnement logique du modèle sur des structures grammaticales complexes (contrefactuelles).

## Solution Apportée : Durcissement du System Prompt

Nous avons mis à jour `backend/app/services/llm.py` avec de nouvelles directives de rigueur :

### 1. Règle d'Interprétation Logique
- **Directive** : Interdiction formelle de transformer un raisonnement hypothétique en affirmation de fait.
- **Impact** : Le modèle comprend désormais que les propos du Prophète (p.b.u.h) dans les hadiths cités niaient justement l'obligation annuelle.

### 2. Sanctuarisation des Piliers
- **Ajout** : Rappel explicite dans le prompt que le Hajj s'accomplit **une seule fois dans la vie**.
- **Sécurité** : Cette "vérité fondamentale" sert d'ancre pour éviter toute dérive, même si les sources RAG sont ambiguës.

## Résultats de la Correction

Après ajustement, la simulation RAG donne désormais :
- **Réponse Corrigée** : "Le Hajj n'est pas obligatoire chaque année."
- **Précision** : Le modèle restitue fidèlement le sens profond des sources sans inventer de règles.

> [!TIP]
> Ce processus démontre la valeur du fichier `feedback.jsonl` : il permet de transformer chaque erreur signalée par l'utilisateur en une amélioration immédiate de la "sagesse" du système.
