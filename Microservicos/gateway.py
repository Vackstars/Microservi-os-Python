from flask import Flask, request, jsonify
import requests
import random

app = Flask(__name__)

MS_USUARIO_1_URL = 'http://localhost:5000'
MS_USUARIO_2_URL = 'http://localhost:5002'

instancias_disponiveis = [MS_USUARIO_1_URL, MS_USUARIO_2_URL]


def enviar_requisicao_ms_usuario(dados, endpoint):
    response = requests.post(endpoint, json=dados)
    return response.json(), response.status_code


def escolher_instancia():
    # Embaralha a lista para escolha aleatória
    random.shuffle(instancias_disponiveis)
    for instancia in instancias_disponiveis:
        try:
            response = requests.get(instancia + '/usuarios')
            if response.status_code == 200:
                return instancia
        except requests.RequestException:
            continue
    return None  # Retorna None se nenhuma instância estiver disponível


@app.route("/usuarios", methods=["POST"])
def criar_usuario_endpoint():
    dados = request.json
    endpoint = escolher_instancia() + '/usuarios'
    return enviar_requisicao_ms_usuario(dados, endpoint)


@app.route("/usuarios", methods=["GET"])
def obter_usuarios_endpoint():
    instancia = escolher_instancia()
    if instancia:
        endpoint = instancia + '/usuarios'
        response = requests.get(endpoint)
        return jsonify(response.json()), response.status_code
    else:
        return jsonify({"erro": "Nenhuma instância disponível"}), 500


@app.route("/usuarios/<int:id>", methods=["GET"])
def obter_usuario_endpoint(id):
    endpoint = escolher_instancia() + f'/usuarios/{id}'
    return enviar_requisicao_ms_usuario({}, endpoint)


@app.route("/usuarios/<int:id>", methods=["PUT"])
def atualizar_usuario_endpoint(id):
    dados = request.json
    endpoint = escolher_instancia() + f'/usuarios/{id}'
    return enviar_requisicao_ms_usuario(dados, endpoint)


@app.route("/usuarios/<int:id>", methods=["DELETE"])
def excluir_usuario_endpoint(id):
    endpoint = escolher_instancia() + f'/usuarios/{id}'
    return enviar_requisicao_ms_usuario({}, endpoint)


@app.route("/consumir", methods=["GET"])
def consumir_fila():
    endpoint = escolher_instancia() + '/consumir'
    response = requests.get(endpoint)
    return jsonify(response.json()), response.status_code


if __name__ == "__main__":
    app.run(port=5003)
