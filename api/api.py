from flask import Flask, request, jsonify

from ia.openrouter import responder


app = Flask(__name__)


@app.route("/chat", methods=["POST"])
def chat():

    dados = request.json


    mensagem = dados.get("mensagem")
    numero = dados.get("numero")


    if not mensagem:
        return jsonify({
            "erro": "Mensagem vazia"
        })


    if not numero:
        return jsonify({
            "erro": "Número não informado"
        })



    resposta = responder(
        numero,
        mensagem
    )


    return jsonify({
        "resposta": resposta
    })



if __name__ == "__main__":

    print("🤖 API Whatsapp-ia online")


    app.run(
        host="0.0.0.0",
        port=5000
    )
