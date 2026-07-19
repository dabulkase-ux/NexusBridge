import requests

from config import API_KEY, BASE_URL, MODEL


def extrair_memoria(mensagem, resposta):

    prompt = f"""

Analise essa conversa.

Usuário:
{mensagem}

Assistente:
{resposta}


Sua função é identificar informações importantes
sobre o usuário que devem ser lembradas futuramente.

Guarde apenas informações permanentes.

Exemplos que devem ser lembrados:

- nome
- profissão
- projetos pessoais
- preferências
- objetivos
- informações importantes


Não guarde:

- cumprimentos
- perguntas comuns
- emoções momentâneas
- informações temporárias


Responda APENAS em JSON.

Formato:

{{
"guardar": true,
"memoria": "informação"
}}

Caso não exista nada importante:

{{
"guardar": false,
"memoria": ""
}}

"""


    payload = {

        "model": MODEL,

        "messages": [

            {
                "role": "system",
                "content":
                "Você é um extrator de memória."
            },

            {
                "role": "user",
                "content": prompt
            }

        ],

        "temperature": 0.1,

        "max_tokens": 100

    }


    headers = {

        "Authorization":
        f"Bearer {API_KEY}",

        "Content-Type":
        "application/json"

    }


    try:

        resposta_api = requests.post(
            BASE_URL,
            headers=headers,
            json=payload,
            timeout=30
        )


        dados = resposta_api.json()


        texto = dados["choices"][0]["message"]["content"]


        return texto


    except Exception as erro:

        print(
            "Erro no extrator:",
            erro
        )

        return None