from eventocesar import db
from datetime import datetime

class Evento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email_responsavel = db.Column(db.String(120), nullable=False)
    area_demandante = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    horario = db.Column(db.Time, nullable=False)
    intervalo = db.Column(db.Boolean, default=False)
    publico_participante = db.Column(db.String(50), nullable=False)
    quantidade_pessoas = db.Column(db.Integer, nullable=True)
    sala_reservada = db.Column(db.Boolean, default=False)
    local_reservado = db.Column(db.String(100), nullable=True)
    coffee_break = db.Column(db.Boolean, default=False)
    necessidades_coffee_break = db.Column(db.String(20), nullable=False)
    formato = db.Column(db.String(20), nullable=False)
    link_zoom = db.Column(db.Boolean, nullable=False)


class EventoConfirmado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    evento_id = db.Column(db.Integer, db.ForeignKey('evento.id'), nullable=False)
    evento = db.relationship('Evento', backref='eventos_confirmados')
    confirmado = db.Column(db.Boolean, default=False, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

