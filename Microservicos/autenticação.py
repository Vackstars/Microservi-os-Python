from flask import Flask, request, jsonify
from usuarios import ServicoUsuarios


class ServicoAutenticacao:
    def __init__(self, servico_usuarios):
        self.servico_usuarios = servico_usuarios

    def carregar_usuarios(self):
        # Carrega os usuários antes de tentar autenticar
        self.servico_usuarios.carregar_usuarios()

    def login(self, dados):
        self.carregar_usuarios()  # Carrega os usuários antes de tentar autenticar

        if "email" in dados and "senha" in dados:
            email = dados["email"]
            senha = dados["senha"]

            for usuario in self.servico_usuarios.obter_usuarios():
                if usuario["email"] == email and usuario["senha"] == senha:
                    # Status HTTP 200 - OK
                    return {"mensagem": "Login concluído"}, 200

            # Debugging
            print("Usuários disponíveis para autenticação:",
                  self.servico_usuarios.obter_usuarios())
            print("Email e senha fornecidos:", email, senha)

        # Status HTTP 401 - Unauthorized
        return {"erro": "Credenciais inválidas"}, 401


app = Flask(__name__)

servico_usuarios = ServicoUsuarios()
servico_autenticacao = ServicoAutenticacao(servico_usuarios)


@app.route("/login", methods=["POST"])
def endpoint_login():
    dados = request.json
    return servico_autenticacao.login(dados)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
