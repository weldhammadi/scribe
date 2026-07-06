# Scribe

Scribe est un outil en ligne de commande qui transforme un enregistrement audio (réunion, cours, note vocale) en compte rendu écrit et structuré.

Fonctionnement :

1. Vous fournissez un fichier audio.
2. Scribe le transcrit en texte brut via le modèle de transcription (Speech-to-Text) de [Groq](https://console.groq.com).
3. Scribe reformule ce texte en compte rendu structuré (titre, résumé, points clés, décisions/actions) via un LLM, également via Groq.

## Installation

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
```

Copiez `.env.example` en `.env` et renseignez-y votre clé API Groq (voir [console.groq.com](https://console.groq.com)).

## Lancement

```bash
python src/cli.py chemin/vers/audio.wav
```

*(section à compléter à l'étape feature/cli avec un exemple complet)*

## Structure du projet

- `src/` — code source de Scribe (configuration, transcription, compte rendu, CLI).
- `audio_samples/` — courts extraits audio d'exemple pour les tests.
- `prompts/` — prompts système utilisés pour piloter le LLM.

## Questions de réflexion

> Brouillon à retravailler et s'approprier avant la soutenance — pas des réponses finales.

**Q1 — Pourquoi le `.gitignore` doit-il exister avant d'écrire la moindre ligne de code manipulant des secrets ?**

Git conserve l'historique complet de chaque fichier commité. Si `.env` est créé et commité avant d'être ignoré, la clé API reste dans l'historique même après sa suppression ultérieure. Le `.gitignore` est donc une prévention, pas une correction.

**Q2 — Quels modèles STT et LLM propose Groq aujourd'hui, et lesquels choisissez-vous ? Justifiez (qualité, vitesse, coût).**

STT disponibles : `whisper-large-v3-turbo` ( ~0,04 $/h, ~12 % d'erreur) et `whisper-large-v3` ( ~0,111 $/h, ~10,3 % d'erreur).
LLM disponibles (extrait) : `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, `openai/gpt-oss-120b`/`20b`.

Choix retenu : 
`whisper-large-v3-turbo` pour la transcription, le gain de précision de `whisper-large-v3` ne justifie pas le surcoût pour cet usage.
`llama-3.3-70b-versatile` pour le compte rendu, structurer un texte (titre, points clés, décisions) sans rien inventer demande une meilleure compréhension du contexte qu'un modèle 8B, ce qui justifie le coût/latence supplémentaire.

**Q3 — Que renvoie exactement l'API en plus du texte (langue détectée, segments, horodatage...) ? Qu'est-ce qui pourrait être utile pour une évolution future de Scribe ?**

Avec `response_format="verbose_json"`, l'API renvoie, en plus de `text` : la langue détectée, la durée audio, et une liste de segments (texte + horodatage début/fin de chaque prise de parole) ; des horodatages au mot près sont aussi disponibles via `timestamp_granularities=["word"]`. Utile pour une évolution future : relier chaque point clé/décision du compte rendu à l'instant exact de l'enregistrement, ou détecter automatiquement la langue plutôt que de la figer en dur.

**Q4 — Quelle température choisissez-vous pour cet usage, et pourquoi ?**

Une température basse (0,2) : la tâche est de l'extraction/reformulation fidèle, pas de la génération créative. Une température plus haute augmenterait le risque que le modèle invente une décision ou une action absente de la transcription, ce que l'énoncé interdit explicitement.

**Q5 — Votre prompt système est envoyé à chaque requête : quel lien avec la notion de tokens en cache vue en cours ?**

Le prompt système est identique à chaque appel : c'est un préfixe de tokens constant. Les fournisseurs comme Groq peuvent mettre en cache le calcul de ce préfixe partagé et ne pas le retraiter entièrement à chaque requête, ce qui réduit latence et coût sur la partie fixe de la requête. C'est aussi pourquoi le prompt système est isolé dans son propre fichier plutôt que reconstruit dynamiquement : le garder stable maximise ce bénéfice de cache, alors que la transcription (partie variable) est envoyée séparément en tant que message utilisateur.
