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

def get_api_key(api_name: str) -> str:
    """
    Récupère une clé API depuis st.secrets, les variables d'environnement, ou demande à l'utilisateur.
    
    Args:
        api_name (str): Nom de l'API (Groq, Clipdrop, Mistral)
    
    Returns:
        str: La clé API
        
    Raises:
        ConfigError: Si la clé API n'est pas trouvée et que l'environnement est en production
    """
    key_env_var = f"{api_name.upper()}_API_KEY"
    
    # Vérifier d'abord les variables d'environnement
    key = os.environ.get(key_env_var)
    
    # Ensuite, vérifier st.secrets si pas trouvé dans env
    if not key:
        try:
            key = st.secrets.get(api_name.lower())
        except Exception as e:
            logger.warning(f"Impossible de lire st.secrets pour {api_name}: {e}")
    
    # En production, on ne veut pas de saisie manuelle
    is_production = os.environ.get("ENVIRONMENT") == "production"
    
    if not key and is_production:
        error_msg = f"Clé API {api_name} non configurée en production"
        logger.error(error_msg)
        raise ConfigError(error_msg)
    
    # En développement, permettre la saisie manuelle
    if not key and not is_production:
        logger.warning(f"Clé API {api_name} non trouvée dans la configuration")
        st.warning(f"⚠️ Veuillez configurer votre clé API {api_name} dans .streamlit/secrets.toml ou comme variable d'environnement {key_env_var}")
        key_input = st.text_input(
            f"Ou entrez votre clé API {api_name} ici pour le développement :",
            key=f"{api_name.lower()}_key_input",
            type="password"
        )
        if key_input:
            key = key_input
            logger.info(f"Clé API {api_name} saisie manuellement")
        else:
            st.stop()
    
    return key 