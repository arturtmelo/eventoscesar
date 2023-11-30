from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, IntegerField, DateField, TimeField, SubmitField, RadioField
from wtforms.validators import InputRequired, Length, Email, DataRequired, Optional

def str_to_bool(value):
    if isinstance(value, bool):
        return value
    return value.lower() == 'true'


class FiltroForm(FlaskForm):
    ordenar_data = SelectField("Ordenar por datas", choices=[("asc", "Mais próximas"), ("desc", "Mais distantes")])
    categoria = SelectField("Filtrar por categoria", choices=[
        ("Todos", "Todos"),
        ("Programação", "Programação"),
        ("Design", "Design"),
        ("Trabalho", "Área de trabalho"),
        ("Outros", "Outros")
    ])
    filtrar = SubmitField("GO!")


class EventoForm(FlaskForm):
    nome = StringField('Nome do evento', validators=[DataRequired()])
    email_responsavel = StringField('E-mail do responsável', validators=[DataRequired(), Email()])
    area_demandante = StringField('Área demandante', validators=[DataRequired()])
    descricao = TextAreaField('Descrição do evento', validators=[DataRequired(), Length(max=23)])
    data_inicio = DateField('Data de início', format='%Y-%m-%d', validators=[DataRequired()])
    data_fim = DateField('Data de término', format='%Y-%m-%d', validators=[DataRequired()])
    horario = TimeField('Horário', format='%H:%M', validators=[DataRequired()])
    intervalo = BooleanField('Haverá intervalo?')
    publico_participante = StringField('Público participante', validators=[DataRequired()])
    quantidade_pessoas = IntegerField('Quantidade de pessoas', default=None, validators=[Optional()])
    sala_reservada = BooleanField('A sala será reservada?')
    local_reservado = StringField('Local reservado', validators=[Optional()])
    coffee_break = BooleanField('Haverá coffee break?')
    necessidades_coffee_break = SelectField('Necessidades para o coffee break', choices=[('cafe', 'Café'), ('petiscos', 'Petiscos'), ('refrigerante', 'Refrigerante')], validators=[Optional()])
    formato = SelectField('Formato', choices=[('Presencial', 'Presencial'), ('Online', 'Online'), ('Híbrido', 'Híbrido')], validators=[DataRequired()])
    link_zoom = RadioField('Será usado o Zoom?', choices=[('True', 'Sim'), ('False', 'Não')], default='False')
    botao_submit_cadastrarevento = SubmitField('Cadastrar Evento')