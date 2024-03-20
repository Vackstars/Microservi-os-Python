from flask import Flask, request, jsonify
import pika
import json
from py_eureka_client import eureka_client


app = Flask(__name__)

# Configurar conexão RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='usuario')



class ServicoAutenticacao:
    def login(self, dados):
        email = dados["email"]
        senha = dados["senha"]

        message = json.dumps({"email": email, "senha": senha})
        channel.basic_publish(exchange='', routing_key='usuario', body=message)

        return {"mensagem": "A solicitação foi enviada para autenticação."}, 200


servico_autenticacao = ServicoAutenticacao()


@app.route("/login", methods=["POST"])
def endpoint_login():
    dados = request.json
    return servico_autenticacao.login(dados)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
