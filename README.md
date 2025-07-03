# ✨ Synthétiseur de Rêves

Une application web qui transforme vos rêves racontés en images et analyse leur ambiance émotionnelle.

## 🚀 Fonctionnalités

- 🎤 Enregistrement audio ou upload de fichiers audio
- 📝 Transcription automatique des rêves (via Groq Whisper)
- 🎨 Génération d'images à partir des descriptions (via Clipdrop)
- 🎭 Analyse émotionnelle des rêves (via Mistral AI)
- 📚 Historique des rêves avec leurs analyses

## 🛠️ Installation

1. Clonez le dépôt :

```bash
git clone https://github.com/votre-username/DreamAI.git
cd DreamAI
```

2. Installez les dépendances :

```bash
pip install -r requirements.txt
```

3. Configurez les variables d'environnement :
   - Créez un dossier .streamlit dedans `secrets.toml` à la racine du projet
   - Ajoutez vos clés API :

```env
ENVIRONMENT=development
GROQ_API_KEY=votre_cle_groq
CLIPDROP_API_KEY=votre_cle_clipdrop
MISTRAL_API_KEY=votre_cle_mistral
```

## 🚀 Démarrage

1. Lancez l'application :

```bash
streamlit run app.py
```

2. Ouvrez votre navigateur à l'adresse : http://XXX:8501

## 🌍 Déploiement

Pour déployer en production :

1. Configurez les variables d'environnement de production :

```env
ENVIRONMENT=production
GROQ_API_KEY=votre_cle_groq_prod
CLIPDROP_API_KEY=votre_cle_clipdrop_prod
MISTRAL_API_KEY=votre_cle_mistral_prod
```

2. Déployez sur Streamlit Cloud ou votre plateforme préférée.

## 📝 Configuration

Le projet utilise trois APIs externes :

- Groq Whisper pour la transcription audio
- Clipdrop pour la génération d'images
- Mistral AI pour l'analyse émotionnelle

Assurez-vous d'avoir des clés API valides pour chaque service.
