from flask import Flask, Request, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import pika
import json
from py_eureka_client import eureka_client


app = Flask(__name__)

# Configuração do SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
db = SQLAlchemy(app)

# Classe de Modelo de Usuário


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(80))
    email = db.Column(db.String(120))
    senha = db.Column(db.String(120))

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'senha': self.senha
        }


# Configurar conexão RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='usuario')

# Cria as tabelas no banco de dados
with app.app_context():
    db.create_all()


@app.route("/consumir", methods=["GET"])
def consumir_fila():
    method_frame, header_frame, body = channel.basic_get(queue='usuario')
    if method_frame:
        dados = json.loads(body)
        email = dados["email"]
        senha = dados["senha"]

        usuario = Usuario.query.filter_by(email=email, senha=senha).first()
        if usuario:
            mensagem = {"mensagem": "Login autorizado"}
        else:
            mensagem = {"mensagem": "Login não autorizado"}

        channel.basic_ack(delivery_tag=method_frame.delivery_tag)

        return jsonify(mensagem), 200
    else:
        return jsonify({"mensagem": "Sem mensagens na fila"}), 404

# Serviço de Usuários


@app.route("/usuarios", methods=["POST"])
def criar_usuario_endpoint():
    dados = request.json
    usuario = Usuario(nome=dados["nome"],
                      email=dados["email"], senha=dados["senha"])
    db.session.add(usuario)
    db.session.commit()
    return jsonify(usuario.to_dict()), 201


@app.route("/usuarios", methods=["GET"])
def obter_usuarios_endpoint():
    usuarios = Usuario.query.all()
    return jsonify([usuario.to_dict() for usuario in usuarios]), 200


@app.route("/usuarios/<int:id>", methods=["GET"])
def obter_usuario_endpoint(id):
    usuario = Usuario.query.get(id)
    if usuario:
        return jsonify(usuario.to_dict()), 200
    else:
        return jsonify({"erro": "Usuário não encontrado"}), 404


@app.route("/usuarios/<int:id>", methods=["PUT"])
def atualizar_usuario_endpoint(id):
    dados = request.json
    usuario = Usuario.query.get(id)
    if usuario:
        usuario.nome = dados["nome"]
        usuario.email = dados["email"]
        usuario.senha = dados["senha"]
        db.session.commit()
        return jsonify(usuario.to_dict()), 200
    else:
        return jsonify({"erro": "Usuário não encontrado"}), 404


@app.route("/usuarios/<int:id>", methods=["DELETE"])
def excluir_usuario_endpoint(id):
    usuario = Usuario.query.get(id)
    if usuario:
        db.session.delete(usuario)
        db.session.commit()
        return jsonify({"sucesso": True}), 200
    else:
        return jsonify({"erro": "Usuário não encontrado"}), 404


if __name__ == "__main__":
    app.run(port=5002)
