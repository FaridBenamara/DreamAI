import streamlit as st
import datetime
import logging
from api_clients import transcribe_audio, generate_image, analyze_emotion
import io

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration de la page
st.set_page_config(
    page_title="Synthétiseur de Rêves",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialise les variables de session si elles n'existent pas"""
    if "dream_history" not in st.session_state:
        st.session_state.dream_history = []
    if "transcription" not in st.session_state:
        st.session_state.transcription = None
    if "generated_image" not in st.session_state:
        st.session_state.generated_image = None
    if "emotion" not in st.session_state:
        st.session_state.emotion = None

def reset_dream_state():
    """Réinitialise l'état du rêve actuel"""
    st.session_state.transcription = None
    st.session_state.generated_image = None
    st.session_state.emotion = None

def save_dream_to_history():
    """Sauvegarde le rêve actuel dans l'historique"""
    if all([st.session_state.transcription, st.session_state.emotion]):
        dream_entry = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "transcription": st.session_state.transcription,
            "emotion": st.session_state.emotion,
            "image_generated": st.session_state.generated_image is not None
        }
        st.session_state.dream_history.append(dream_entry)
        logger.info("Nouveau rêve ajouté à l'historique")

def main():
    try:
        initialize_session_state()
        
        st.title("✨ Synthétiseur de Rêves ✨")
        st.write("Bienvenue dans l'application qui transforme vos rêves racontés en images et analyse leur ambiance émotionnelle.")

        # Section 1: Saisie du rêve
        st.header("1. Racontez ou téléchargez votre rêve")
        audio_option = st.radio(
            "Comment souhaitez-vous saisir votre rêve ?",
            ("Enregistrer l'audio", "Uploader un fichier audio")
        )

        audio_data = None
        if audio_option == "Uploader un fichier audio":
            audio_file = st.file_uploader("Téléchargez un fichier audio (.wav, .mp3 ou .m4a)", type=["wav", "mp3", "m4a"])
            if audio_file:
                st.audio(audio_file, format=audio_file.type)
                st.success("✅ Fichier audio uploadé avec succès !")
                audio_data = audio_file
        else:
            recorded_audio = st.audio_input(label="Cliquez pour enregistrer votre rêve", key="audio_recorder")
            if recorded_audio:
                st.success("✅ Audio enregistré avec succès !")
                audio_data = io.BytesIO(recorded_audio.getvalue())
                audio_data.name = "recorded_audio.wav"

        # Placeholders pour l'affichage des résultats
        transcription_placeholder = st.empty()
        image_placeholder = st.empty()
        emotion_placeholder = st.empty()

        # Affichage des résultats existants
        if st.session_state.transcription:
            transcription_placeholder.write(f"**Transcription :** {st.session_state.transcription}")

        if st.session_state.generated_image:
            image_placeholder.image(st.session_state.generated_image, caption="Votre rêve en image", use_container_width=True)

        if st.session_state.emotion:
            emotion_placeholder.write(f"**Émotion du rêve :** {st.session_state.emotion}")

        # Section 2: Transcription
        if audio_data:
            st.header("2. Transcription de votre rêve")
            if st.button("Transcrire le rêve", key="transcribe_button"):
                reset_dream_state()  # Réinitialiser l'état pour un nouveau rêve
                transcription_placeholder.empty()
                with st.spinner("🎯 Transcription en cours..."):
                    st.session_state.transcription = transcribe_audio(audio_data)
                
                if "Erreur" in st.session_state.transcription:
                    transcription_placeholder.error(st.session_state.transcription)
                    st.session_state.transcription = None
                else:
                    transcription_placeholder.success("✨ Transcription terminée !")
                    transcription_placeholder.write(f"**Transcription :** {st.session_state.transcription}")

        # Section 3: Génération d'image
        if st.session_state.transcription:
            st.header("3. Visualisation de votre rêve")
            if st.button("Générer l'image du rêve", key="generate_image_button"):
                image_placeholder.empty()
                with st.spinner("🎨 Génération de l'image en cours..."):
                    generated_image_result = generate_image(st.session_state.transcription)
                
                if isinstance(generated_image_result, str) and "Erreur" in generated_image_result:
                    image_placeholder.error(generated_image_result)
                    st.session_state.generated_image = None
                else:
                    st.session_state.generated_image = generated_image_result
                    image_placeholder.success("🖼️ Image générée avec succès !")
                    image_placeholder.image(st.session_state.generated_image, caption="Votre rêve en image", use_container_width=True)

        # Section 4: Analyse émotionnelle
        if st.session_state.transcription:
            st.header("4. Analyse émotionnelle du rêve")
            if st.button("Analyser l'émotion du rêve", key="analyze_emotion_button"):
                emotion_placeholder.empty()
                with st.spinner("💭 Analyse émotionnelle en cours..."):
                    emotion_result = analyze_emotion(st.session_state.transcription)
                
                if "Erreur" in emotion_result:
                    emotion_placeholder.error(emotion_result)
                    st.session_state.emotion = None
                else:
                    st.session_state.emotion = emotion_result
                    emotion_placeholder.success("🎭 Analyse émotionnelle terminée !")
                    emotion_placeholder.write(f"**Émotion du rêve :** {st.session_state.emotion}")
                    save_dream_to_history()

        # Historique des Rêves (Sidebar)
        st.sidebar.header("📚 Historique des Rêves")
        if st.session_state.dream_history:
            for i, dream in enumerate(reversed(st.session_state.dream_history)):
                with st.sidebar.expander(f"Rêve du {dream['timestamp']}"):
                    st.write(f"**Transcription :** {dream['transcription'][:100]}...")
                    st.write(f"**Émotion :** {dream['emotion']}")
                    st.write("**Image :** " + ("Oui ✅" if dream["image_generated"] else "Non ❌"))
        else:
            st.sidebar.info("📝 Vos rêves passés et leurs analyses seront affichés ici.")

        st.write("---")
        st.write("Développé avec ❤️ pour le projet « Synthétiseur de rêves »")

    except Exception as e:
        logger.error(f"Erreur inattendue dans l'application: {e}")
        st.error("Une erreur inattendue s'est produite. Veuillez réessayer ou contacter le support.")

if __name__ == "__main__":
    main() 