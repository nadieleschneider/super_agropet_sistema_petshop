from datetime import datetime
import os
from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configura o Banco de Dados local (cria um arquivo 'super_agropet.db' na pasta)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "super_agropet.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# --- MODELOS DO BANCO DE DADOS ---
class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    cpf = db.Column(db.String(20), nullable=True)
    endereco = db.Column(db.String(200), nullable=True)
    pets = db.relationship("Pet", backref="tutor", lazy=True)


class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(50), nullable=False)
    raca = db.Column(db.String(50), nullable=True)
    peso = db.Column(db.Float, nullable=True)
    porte = db.Column(db.String(30), nullable=True)
    cliente_id = db.Column(
        db.Integer, db.ForeignKey("cliente.id"), nullable=False
    )
    atendimentos = db.relationship("Atendimento", backref="pet_obj", lazy=True)


class Atendimento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(20), nullable=False)
    horario = db.Column(db.String(10), nullable=False)
    servico = db.Column(db.String(100), nullable=False)
    lamina = db.Column(db.String(30), nullable=True)
    perfume = db.Column(db.String(10), nullable=True)
    detalhes = db.Column(db.String(300), nullable=True)
    valor = db.Column(db.Float, nullable=False)
    status = db.Column(
        db.String(30), default="Agendado"
    )  # Agendado ou Concluído
    pet_id = db.Column(db.Integer, db.ForeignKey("pet.id"), nullable=False)


# Cria o banco de dados se ele não existir
with app.app_context():
    db.create_all()

SERVICOS_PREÇOS = {
    "Banho Simples": 40.00,
    "Banho + Tosa Higiênica": 60.00,
    "Tosa Completa + Banho": 90.00,
    "Apenas Corte de Unha / Limpeza de Ouvido": 25.00,
}


@app.route("/")
def index():
    # Busca atendimentos do dia ou pendentes
    atendimentos = Atendimento.query.order_by(Atendimento.horario).all()
    clientes = Cliente.query.all()
    pets = Pet.query.all()
    return render_template(
        "index.html",
        atendimentos=atendimentos,
        clientes=clientes,
        pets=pets,
        servicos=SERVICOS_PREÇOS,
    )


@app.route("/adicionar_cliente", methods=["POST"])
def adicionar_cliente():
    novo_cliente = Cliente(
        nome=request.form.get("nome"),
        telefone=request.form.get("telefone"),
        cpf=request.form.get("cpf"),
        endereco=request.form.get("endereco"),
    )
    db.session.add(novo_cliente)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/adicionar_pet", methods=["POST"])
def adicionar_pet():
    novo_pet = Pet(
        nome=request.form.get("nome"),
        especie=request.form.get("especie"),
        raca=request.form.get("raca"),
        peso=float(request.form.get("peso") or 0),
        porte=request.form.get("porte"),
        cliente_id=int(request.form.get("cliente_id")),
    )
    db.session.add(novo_pet)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/agendar", methods=["POST"])
def agendar():
    novo_agendamento = Atendimento(
        data=datetime.now().strftime("%d/%m/%Y"),
        horario=request.form.get("horario"),
        servico=request.form.get("servico"),
        lamina=request.form.get("lamina", "N/A"),
        perfume=request.form.get("perfume", "Sim"),
        detalhes=request.form.get("detalhes", ""),
        valor=float(request.form.get("valor") or 0),
        status="Agendado",
        pet_id=int(request.form.get("pet_id")),
    )
    db.session.add(novo_agendamento)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/concluir/<int:id>")
def concluir(id):
    item = Atendimento.query.get_or_404(id)
    item.status = "Concluído"
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/remover/<int:id>")
def remover(id):
    item = Atendimento.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)