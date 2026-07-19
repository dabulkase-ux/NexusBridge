from dotenv import load_dotenv
import os


load_dotenv()


# ==============================
# OPENROUTER
# ==============================

API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)


MODEL = os.getenv(
    "MODEL",
    "deepseek/deepseek-chat-v3-0324:free"
)


BASE_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)



# ==============================
# IDENTIDADE DO NEXUS
# ==============================

NEXUS_NAME = "Nexus"


# Número principal do desenvolvedor
# Esse número nunca deve ser definido pela IA

CRIADOR_NUMERO = os.getenv(
    "CRIADOR_NUMERO",
    "5521986828948"
)



CRIADOR_NOME = "Arthur"



# ==============================
# SISTEMA
# ==============================

APP_NAME = "NexusBridge"



# ==============================
# VALIDAÇÃO
# ==============================

if not API_KEY:

    raise ValueError(
        "API do OpenRouter não encontrada no arquivo .env"
    )