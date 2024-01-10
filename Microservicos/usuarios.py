import json
from flask import Flask, request, jsonify


class ServicoUsuarios:
    def __init__(self, nome_arquivo="usuarios.json"):
        self.nome_arquivo = nome_arquivo
        self.carregar_usuarios()

    def carregar_usuarios(self):
        try:
            with open(self.nome_arquivo, "r") as arquivo:
                self.usuarios = json.load(arquivo)
        except FileNotFoundError:
            self.usuarios = []

    def salvar_usuarios(self):
        with open(self.nome_arquivo, "w") as arquivo:
            json.dump(self.usuarios, arquivo, indent=4)

    def criar_usuario(self, dados):
        usuario = {
            "id": len(self.usuarios) + 1,
            "nome": dados["nome"],
            "email": dados["email"],
            "senha": dados["senha"],
        }
        self.usuarios.append(usuario)
        self.salvar_usuarios()  # Salva os usuários após adicionar um novo
        return usuario

    def obter_usuarios(self):
        return self.usuarios

    def obter_usuario(self, id):
        for usuario in self.usuarios:
            if usuario["id"] == id:
                return usuario
        return None

    def atualizar_usuario(self, id, dados):
        for usuario in self.usuarios:
            if usuario["id"] == id:
                usuario["nome"] = dados["nome"]
                usuario["email"] = dados["email"]
                return usuario
        return None

    def excluir_usuario(self, id):
        for usuario in self.usuarios:
            if usuario["id"] == id:
                self.usuarios.remove(usuario)
                return True
        return False


app = Flask(__name__)

servico_usuarios = ServicoUsuarios()


@app.route("/usuarios", methods=["POST"])
def criar_usuario_endpoint():
    dados = json.loads(request.data)
    usuario = servico_usuarios.criar_usuario(dados)
    return jsonify(usuario), 201  # Status HTTP 201 - Criado


@app.route("/usuarios", methods=["GET"])
def obter_usuarios_endpoint():
    usuarios = servico_usuarios.obter_usuarios()
    return jsonify(usuarios), 200  # Status HTTP 200 - OK


@app.route("/usuarios/<int:id>", methods=["GET"])
def obter_usuario_endpoint(id):
    usuario = servico_usuarios.obter_usuario(id)
    if usuario:
        return jsonify(usuario), 200  # Status HTTP 200 - OK
    else:
        # Status HTTP 404 - Não Encontrado
        return jsonify({"erro": "Usuário não encontrado"}), 404


@app.route("/usuarios/<int:id>", methods=["PUT"])
def atualizar_usuario_endpoint(id):
    dados = json.loads(request.data)
    usuario = servico_usuarios.atualizar_usuario(id, dados)
    if usuario:
        return jsonify(usuario), 200  # Status HTTP 200 - OK
    else:
        # Status HTTP 404 - Não Encontrado
        return jsonify({"erro": "Usuário não encontrado"}), 404


@app.route("/usuarios/<int:id>", methods=["DELETE"])
def excluir_usuario_endpoint(id):
    resultado = servico_usuarios.excluir_usuario(id)
    if resultado:
        return jsonify({"sucesso": True}), 200  # Status HTTP 200 - OK
    else:
        # Status HTTP 404 - Não Encontrado
        return jsonify({"erro": "Usuário não encontrado"}), 404


if __name__ == "__main__":
    app.run(debug=True)
