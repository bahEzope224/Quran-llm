# Walkthrough - Historical Accuracy (Assia vs Aisha)

Cette intervention corrige une hallucination历史上 grave détectée via les feedbacks utilisateurs : la confusion entre **Assia** (femme de Pharaon) et **Aïcha** (femme du Prophète).

## Problème Identifié
- **Biais de Recherche** : Le retriever ne trouvait pas assez de sources sur "Assia" (très peu citée par son nom propre) et se rabattait sur "Aisha", phonétiquement proche et omniprésente dans les Hadiths.
- **Confusion Initiale** : L'IA affirmait que "Assia était la femme de Muhammad", ce qui est factualement faux.

## Solutions Déployées

### 1. 🧬 Chirurgie Lexicale (Backend)
- **Purge Selective** : Dans `rag_pipeline.py`, si le mot "Assia" est détecté, le mot "Aisha" est désormais **interdit** dans la requête de recherche pour éviter toute pollution.
- **Expansion Thématique** : La recherche sur Assia injecte automatiquement le terme "Pharaoh/Pharaon" pour cibler les versets coraniques et les récits de Moïse.

### 2. 🛡️ Guardrails Anti-Hallucination
- **Instruction Système** : Ajout d'une règle stricte dans `llm.py` interdisant de "prêter" les caractéristiques d'une personne (Aisha) à une autre (Assia) même si les noms se ressemblent.

## Résultat de la Vérification
- [x] **Identité** : L'IA identifie maintenant Assia comme "femme de Pharaon".
- [x] **Sources** : Bien que le Hadith de Sahih Muslim cite les deux femmes comme modèles de perfection, l'IA ne les fusionne plus.
- [x] **Stabilité** : Aucune mention erronée de mariage avec le Messager n'est plus produite.

> [!IMPORTANT]
> Cette méthode de "Purge Lexicale" sera appliquée à l'avenir pour d'autres confusions classiques (ex: Maryam/Miriam, etc.) afin de garantir une rigueur doctrinale absolue.
