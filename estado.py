from time import time


class EstadoIA:

    def __init__(self):

        self.inicio = time()

        self.modelo_atual = None
        self.modelo_anterior = None

        self.ultima_pergunta = ""
        self.ultima_resposta = ""

        self.ultimo_erro = ""

        self.falhas_seguidas = 0
        self.total_falhas = 0
        self.total_respostas = 0

        self.memoria_carregada = False

        self.status = "Inicializando"


    def definir_modelo(self, modelo):

        self.modelo_anterior = self.modelo_atual
        self.modelo_atual = modelo


    def registrar_resposta(self, pergunta, resposta):

        self.ultima_pergunta = pergunta
        self.ultima_resposta = resposta

        self.total_respostas += 1
        self.falhas_seguidas = 0

        self.status = "Online"


    def registrar_erro(self, erro):

        self.ultimo_erro = str(erro)

        self.total_falhas += 1
        self.falhas_seguidas += 1

        self.status = "Erro"


    def tempo_online(self):

        return round(time() - self.inicio, 2)


    def resumo(self):

        return {
            "modelo": self.modelo_atual,
            "status": self.status,
            "tempo_online": self.tempo_online(),
            "respostas": self.total_respostas,
            "falhas": self.total_falhas,
            "falhas_seguidas": self.falhas_seguidas
        }


estado = EstadoIA()
