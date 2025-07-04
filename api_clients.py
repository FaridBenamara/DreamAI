import logging
from groq import Groq
import requests
import io
from config import get_api_key

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Mapping des émotions vers les emojis
EMOTION_EMOJIS = {
    "Heureux": "😊",
    "Joyeux": "😊",
    "Content": "😊",
    "Stressant": "😰",
    "Stressé": "😰",
    "Anxieux": "😰",
    "Neutre": "😐",
    "Calme": "😌",
    "Triste": "😢",
    "Mélancolique": "😢",
    "Déprimé": "😢",
    "Excité": "🤩",
    "Enthousiaste": "🤩",
    "Passionné": "🤩",
    "Effrayant": "😱",
    "Effrayé": "😱",
    "Terrifié": "😱",
    "Surpris": "😲",
    "Étonné": "😲",
    "En colère": "😠",
    "Furieux": "😠",
    "Amoureux": "🥰",
    "Paisible": "😌"
}

# Récupérer les clés API
try:
    GROQ_API_KEY = get_api_key("Groq")
    CLIPDROP_API_KEY = get_api_key("Clipdrop")
    MISTRAL_API_KEY = get_api_key("Mistral")
    groq_client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    logger.error(f"Erreur lors de l'initialisation des clés API: {e}")
    raise

def get_emotion_with_emoji(emotion_text: str) -> str:
    """
    Retourne l'émotion avec son emoji correspondant.
    Si l'émotion n'est pas dans le dictionnaire, retourne juste l'émotion.
    """
    emotion_text = emotion_text.strip()
    emoji = EMOTION_EMOJIS.get(emotion_text, "❓")
    return f"{emotion_text} {emoji}"

def transcribe_audio(audio_file_data):
    """
    Transcrire un fichier audio en texte à l'aide de l'API Groq Whisper.
    audio_file_data peut être un objet UploadedFile de Streamlit ou un BytesIO.
    """
    try:
        logger.info("Début de la transcription audio")
        
        # Préparation du fichier audio
        if isinstance(audio_file_data, io.BytesIO):
            file_name = getattr(audio_file_data, 'name', 'audio.wav')
            file_content = audio_file_data.getvalue()
        else:
            file_name = audio_file_data.name
            file_content = audio_file_data.getvalue()

        # Envoi à l'API Groq
        transcript = groq_client.audio.transcriptions.create(
            file=(file_name, file_content),
            model="whisper-large-v3",
            prompt="Le rêve décrit est..."
        )
        
        logger.info("Transcription audio réussie")
        return transcript.text
    except Exception as e:
        logger.error(f"Erreur lors de la transcription audio: {e}")
        return f"Erreur lors de la transcription audio : {e}"

def generate_image(prompt_text: str):
    """
    Génère une image à partir d'un texte à l'aide de l'API Clipdrop Text-to-Image.
    """
    try:
        logger.info("Début de la génération d'image")
        response = requests.post(
            "https://clipdrop-api.co/text-to-image/v1",
            headers={"x-api-key": CLIPDROP_API_KEY},
            files={"prompt": (None, prompt_text, "text/plain")},
            timeout=30
        )

        response.raise_for_status()
        logger.info("Génération d'image réussie")
        return response.content
    except requests.exceptions.Timeout:
        logger.error("Timeout lors de la génération de l'image")
        return "Erreur : Le serveur met trop de temps à répondre"
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de la génération de l'image: {e}")
        return f"Erreur lors de la génération de l'image : {e}"

def analyze_emotion(text: str):
    """
    Analyse l'émotion d'un texte à l'aide de l'API Mistral AI Chat Completions.
    Retourne l'émotion avec un emoji correspondant.
    """
    try:
        logger.info("Début de l'analyse émotionnelle")
        chat_response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {MISTRAL_API_KEY}"
            },
            json={
                "model": "mistral-small-latest",
                "messages": [
                    {
                        "role": "system",
                        "content": """Vous êtes un classificateur d'émotions de rêves.
                        Analysez le texte du rêve et renvoyez un seul mot parmi les suivants :
                        Heureux, Stressant, Neutre, Triste, Excité, Effrayant, Surpris, En colère, Amoureux, Paisible"""
                    },
                    {"role": "user", "content": text}
                ],
                "max_tokens": 10,
                "temperature": 0.7
            },
            timeout=30
        )

        chat_response.raise_for_status()
        emotion_result = chat_response.json()
        
        if emotion_result and emotion_result.get("choices") and emotion_result["choices"][0].get("message"):
            emotion = emotion_result["choices"][0]["message"]["content"].strip()
            logger.info("Analyse émotionnelle réussie")
            return get_emotion_with_emoji(emotion)
        else:
            logger.warning("Réponse d'analyse émotionnelle invalide")
            return "Aucun résultat d'émotion trouvé ❓"
    except requests.exceptions.Timeout:
        logger.error("Timeout lors de l'analyse émotionnelle")
        return "Erreur : Le serveur met trop de temps à répondre ⏱️"
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse émotionnelle: {e}")
        return f"Erreur lors de l'analyse émotionnelle : {e} ❌" 