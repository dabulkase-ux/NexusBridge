import json
import os
from datetime import datetime

from config import (
    CRIADOR_NUMERO,
    CRIADOR_NOME
)


PASTA_USUARIOS = "dados/usuarios"



# ==============================
# PASTAS
# ==============================

def garantir_pasta():

    if not os.path.exists(PASTA_USUARIOS):
        os.makedirs(PASTA_USUARIOS)



def caminho_usuario(numero):

    garantir_pasta()

    return os.path.join(
        PASTA_USUARIOS,
        f"{numero}.json"
    )



# ==============================
# CRIAÇÃO
# ==============================

def criar_usuario(numero):

    tipo = (
        "criador"
        if numero == CRIADOR_NUMERO
        else "usuario"
    )


    nome = (
        CRIADOR_NOME
        if numero == CRIADOR_NUMERO
        else None
    )


    agora = datetime.now().isoformat()


    return {

        "numero": numero,


        "perfil": {

            "nome": nome,

            "tipo": tipo,

            "nivel": (
                "admin"
                if tipo == "criador"
                else "normal"
            )

        },


        "memorias": [],


        "historico": [],


        "estatisticas": {

            "mensagens": 0,

            "primeiro_contato": agora,

            "ultimo_acesso": agora

        },


        "criado_em": agora

    }



# ==============================
# CARREGAMENTO
# ==============================

def carregar_usuario(numero):

    caminho = caminho_usuario(numero)


    if not os.path.exists(caminho):

        usuario = criar_usuario(numero)

        salvar_usuario(
            numero,
            usuario
        )

        return usuario



    try:

        with open(
            caminho,
            "r",
            encoding="utf-8"
        ) as arquivo:

            usuario = json.load(arquivo)



        atualizar_estrutura(
            usuario,
            numero
        )


        return usuario



    except Exception:

        usuario = criar_usuario(numero)

        salvar_usuario(
            numero,
            usuario
        )

        return usuario




# ==============================
# COMPATIBILIDADE
# ==============================

def atualizar_estrutura(usuario, numero):


    if "perfil" not in usuario:

        usuario["perfil"] = {}


    usuario["perfil"].setdefault(
        "nome",
        None
    )


    usuario["perfil"].setdefault(
        "tipo",
        "usuario"
    )


    usuario["perfil"].setdefault(
        "nivel",
        "normal"
    )



    if "memorias" not in usuario:

        usuario["memorias"] = []



    if "historico" not in usuario:

        usuario["historico"] = []



    if "estatisticas" not in usuario:

        usuario["estatisticas"] = {

            "mensagens": 0,

            "primeiro_contato":
                datetime.now().isoformat(),

            "ultimo_acesso":
                datetime.now().isoformat()

        }



    # garante criador mesmo em arquivos antigos

    if numero == CRIADOR_NUMERO:

        usuario["perfil"]["tipo"] = "criador"

        usuario["perfil"]["nivel"] = "admin"

        usuario["perfil"]["nome"] = CRIADOR_NOME



    salvar_usuario(
        numero,
        usuario
    )



# ==============================
# SALVAR
# ==============================

def salvar_usuario(numero, dados):

    caminho = caminho_usuario(numero)


    with open(
        caminho,
        "w",
        encoding="utf-8"
    ) as arquivo:


        json.dump(
            dados,
            arquivo,
            indent=4,
            ensure_ascii=False
        )



# ==============================
# HISTÓRICO
# ==============================

def salvar_conversa(numero, usuario, ia):

    memoria = carregar_usuario(numero)


    memoria["historico"].append({

        "usuario": usuario,

        "ia": ia,

        "data":
            datetime.now().isoformat()

    })


    memoria["estatisticas"]["mensagens"] += 1


    memoria["estatisticas"]["ultimo_acesso"] = (
        datetime.now().isoformat()
    )


    salvar_usuario(
        numero,
        memoria
    )



# ==============================
# MEMÓRIAS IMPORTANTES
# ==============================

def adicionar_memoria(numero, texto):

    memoria = carregar_usuario(numero)


    if texto not in memoria["memorias"]:

        memoria["memorias"].append(
            texto
        )


    salvar_usuario(
        numero,
        memoria
    )



# ==============================
# PERFIL
# ==============================

def atualizar_perfil(numero, campo, valor):

    memoria = carregar_usuario(numero)


    memoria["perfil"][campo] = valor


    salvar_usuario(
        numero,
        memoria
    )



def obter_perfil(numero):

    memoria = carregar_usuario(numero)


    return memoria["perfil"]



# ==============================
# CONTEXTO PARA IA
# ==============================

def gerar_contexto(numero, limite=10):

    memoria = carregar_usuario(numero)


    contexto = ""



    perfil = memoria["perfil"]


    if perfil["nome"]:

        contexto += (
            f"Nome do usuário: "
            f"{perfil['nome']}\n"
        )



    contexto += (
        f"Tipo de usuário: "
        f"{perfil['tipo']}\n"
    )



    if memoria["memorias"]:


        contexto += (
            "\nMemórias importantes:\n"
        )


        for item in memoria["memorias"]:

            contexto += (
                f"- {item}\n"
            )



    historico = memoria["historico"][-limite:]



    if historico:

        contexto += (
            "\nHistórico recente:\n"
        )


        for item in historico:


            contexto += (
                f"Usuário: {item['usuario']}\n"
                f"Assistente: {item['ia']}\n\n"
            )



    return contexto