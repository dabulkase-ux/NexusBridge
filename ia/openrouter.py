import re
import requests

from memoria.extrator_memoria import extrair_memoria
from memoria.memoria import adicionar_memoria

from config import API_KEY, BASE_URL
from ia.modelos import MODELOS
from ia.prompt import SYSTEM_PROMPT

from memoria.memoria import (
    gerar_contexto,
    salvar_conversa
)

from estado import estado


PALAVRAS_PROIBIDAS = [

    "okay",
    "the user",
    "i need",
    "let's",
    "reasoning",
    "analysis",
    "thought",
    "thinking",
    "assistant reasoning",
    "internal reasoning",
    "my reasoning",
    "follow the instructions",
    "system prompt",
    "assistant:",
    "user:",
    "step 1",
    "step one",
    "first,",
    "wait,",
    "we should",
    "chain of thought",

    "preciso responder",
    "vou responder",
    "devo responder",
    "preciso pensar",
    "vamos pensar",
    "raciocínio",
    "pensamento",
    "analisando"
]


# --------------------------------------------------
# LIMPEZA
# --------------------------------------------------

def limpar_resposta(texto):

    texto = texto.replace("\r", "")

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()


# --------------------------------------------------
# VALIDAÇÃO
# --------------------------------------------------

def resposta_invalida(texto):

    texto_lower = texto.lower()

    for palavra in PALAVRAS_PROIBIDAS:

        if palavra in texto_lower:
            return True

    return False


def resposta_em_ingles(texto):

    texto = texto.lower()

    indicadores = [

        "hello",
        "how can i",
        "thank you",
        "you're welcome",
        "sure",
        "certainly",
        "of course",
        "i'm",
        "i am",
        "the",
        "your",
        "assistant",
        "please"

    ]

    contador = 0

    for palavra in indicadores:

        if palavra in texto:
            contador += 1

    return contador >= 3


# --------------------------------------------------
# PAYLOAD
# --------------------------------------------------

def montar_payload(modelo, mensagem, memoria):

    mensagens = [

        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }

    ]

    if memoria:

        mensagens.append({

            "role": "system",

            "content":
                "Memória conhecida:\n\n"
                + memoria

        })

    mensagens.append({

        "role": "user",

        "content": mensagem

    })

    return {

        "model": modelo,

        "messages": mensagens,

        "temperature": 0.55,

        "max_tokens": 180,

        "reasoning": {
            "exclude": True
        }

    }


# --------------------------------------------------
# REQUISIÇÃO
# --------------------------------------------------

def enviar(payload):

    headers = {

        "Authorization": f"Bearer {API_KEY}",

        "Content-Type": "application/json"

    }

    resposta = requests.post(

        BASE_URL,

        headers=headers,

        json=payload,

        timeout=60

    )

    resposta.raise_for_status()

    return resposta.json()


# --------------------------------------------------
# EXTRAÇÃO
# --------------------------------------------------

def extrair_resposta(dados):

    texto = dados["choices"][0]["message"]["content"]

    texto = limpar_resposta(texto)

    if resposta_invalida(texto):
        raise Exception("Raciocínio detectado.")

    if resposta_em_ingles(texto):
        raise Exception("Resposta em inglês.")

    return texto


# --------------------------------------------------
# MODELO
# --------------------------------------------------

def tentar_modelo(modelo, mensagem, memoria):

    estado.definir_modelo(modelo)

    payload = montar_payload(

        modelo,
        mensagem,
        memoria

    )

    dados = enviar(payload)

    return extrair_resposta(dados)


# --------------------------------------------------
# ORDEM DOS MODELOS
# --------------------------------------------------

def ordem_modelos():

    lista = MODELOS.copy()

    if estado.modelo_atual in lista:

        lista.remove(

            estado.modelo_atual

        )

        lista.insert(

            0,

            estado.modelo_atual

        )

    return lista


# --------------------------------------------------
# RESPOSTA PRINCIPAL
# --------------------------------------------------

def responder(numero, mensagem):

    memoria = gerar_contexto(numero)

    erros = []

    for modelo in ordem_modelos():

        try:

            print(f"🧠 Tentando: {modelo}")

            resposta = tentar_modelo(

                modelo,
                mensagem,
                memoria

            )

            estado.registrar_resposta(

                mensagem,
                resposta

            )

            salvar_conversa(
                numero,
                mensagem,
                resposta
            )


            memoria_nova = extrair_memoria(
                mensagem,
                resposta
            )


            if memoria_nova:

                try:

                    import json

                    dados = json.loads(
                        memoria_nova
                    )


                    if dados.get("guardar"):

                        adicionar_memoria(
                            numero,
                            dados["memoria"]
                        )

                        print(
                            "🧠 Nova memória:",
                            dados["memoria"]
                        )


                except Exception:

                    pass



            print(f"✅ Usando: {modelo}")

            return resposta

        except Exception as erro:

            estado.registrar_erro(erro)

            print(f"❌ Falhou: {modelo}")

            erros.append(

                f"{modelo}: {erro}"

            )

    return (

        "Nenhum modelo conseguiu responder.\n\n"

        + "\n".join(erros)

    )
