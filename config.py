import streamlit as st
import os
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConfigError(Exception):
    """Exception personnalisée pour les erreurs de configuration"""
    pass

def is_streamlit_cloud():
    """Vérifie si l'application tourne sur Streamlit Cloud"""
    return os.environ.get("STREAMLIT_RUNTIME") == "1"

def get_api_key(api_name: str) -> str:
    """
    Récupère une clé API depuis st.secrets, les variables d'environnement, ou demande à l'utilisateur.
    
    Args:
        api_name (str): Nom de l'API (Groq, Clipdrop, Mistral)
    
    Returns:
        str: La clé API
        
    Raises:
        ConfigError: Si la clé API n'est pas trouvée
    """
    key_env_var = f"{api_name.upper()}_API_KEY"
    api_name_lower = api_name.lower()
    
    # Vérifier d'abord les variables d'environnement
    key = os.environ.get(key_env_var)
    
    # Ensuite, vérifier st.secrets
    if not key:
        try:
            key = st.secrets[api_name_lower]
            logger.info(f"Clé API {api_name} trouvée dans st.secrets")
        except Exception as e:
            logger.warning(f"Clé API {api_name} non trouvée dans st.secrets: {e}")
    
    # Si toujours pas de clé, vérifier si nous sommes en développement
    if not key:
        is_production = os.environ.get("ENVIRONMENT") == "production" or is_streamlit_cloud()
        
        if is_production:
            error_msg = f"""
            ⚠️ Configuration manquante pour {api_name} ⚠️
            
            Veuillez configurer la clé API dans Streamlit Cloud :
            1. Allez dans les paramètres de l'application
            2. Section "Secrets"
            3. Ajoutez : {api_name_lower} = "votre_cle_api"
            """
            logger.error(f"Clé API {api_name} non configurée")
            raise ConfigError(error_msg)
        
        # En développement local, permettre la saisie manuelle
        st.warning(f"⚠️ Veuillez configurer votre clé API {api_name}")
        st.info(f"""
        Pour configurer en local :
        1. Créez un fichier `.streamlit/secrets.toml`
        2. Ajoutez votre clé : {api_name_lower} = "votre_cle_api"
        """)
        
        key_input = st.text_input(
            f"Ou entrez votre clé API {api_name} ici pour le développement :",
            key=f"{api_name_lower}_key_input",
            type="password"
        )
        
        if key_input:
            key = key_input
            logger.info(f"Clé API {api_name} saisie manuellement")
        else:
            st.stop()
    
    return key 