from flask import render_template, redirect, url_for, request, flash, jsonify, session
from eventocesar import app, db
from eventocesar.forms import EventoForm, FiltroForm, str_to_bool
from eventocesar.models import Evento, EventoConfirmado
import os
import smtplib
from email.message import EmailMessage
from threading import Lock

lock = Lock()
eventos_em_exclusao = set()


def send_email(evento, subject, mensagem, emails_extras=None):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_user = os.environ['EMAIL_USER']
    smtp_password = os.environ['EMAIL_PASSWORD']

    destinatarios = [{'email': evento.email_responsavel, 'subject': subject}]

    if emails_extras:
        destinatarios += emails_extras  # emails extras

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)

        for destinatario in destinatarios:
            msg = EmailMessage()
            msg['From'] = smtp_user
            msg['To'] = destinatario['email']
            msg['Subject'] = destinatario['subject']
            msg.set_content(mensagem)

            server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")


@app.route("/")
def home():
    return render_template('home.html')

@app.route("/eventos", methods=["GET", "POST"])
def eventos():
    form_filtro = FiltroForm()
    if form_filtro.validate_on_submit() and 'filtrar' in request.form:
        ordenar_data = form_filtro.ordenar_data.data
        categoria = form_filtro.categoria.data
        query = Evento.query

        if ordenar_data == 'asc':
            query = query.order_by(Evento.data_inicio.asc())
        else:
            query = query.order_by(Evento.data_inicio.desc())

        if categoria != "Todos":
            query = query.filter(Evento.area_demandante == categoria)

        # Filter out events that are already approved
        eventos = [evento for evento in query.all() if not event_already_approved(evento.id)]
    else:
        eventos = [evento for evento in Evento.query.all() if not event_already_approved(evento.id)]

    return render_template("eventos.html", eventos=eventos, form_filtro=form_filtro)



@app.route("/eventos_excluidos", methods=["GET", "POST"])
def eventos_excluidos():
    form_filtro = FiltroForm()
    if form_filtro.validate_on_submit() and 'filtrar' in request.form:
        ordenar_data = form_filtro.ordenar_data.data
        categoria = form_filtro.categoria.data
        eventos_excluidos = Evento.query.filter(EventoConfirmado.confirmado.is_(False)).all()

        if ordenar_data == 'asc':
            eventos_excluidos.sort(key=lambda evento: evento.data_inicio)
        else:
            eventos_excluidos.sort(key=lambda evento: evento.data_inicio, reverse=True)

        if categoria != "Todos":
            eventos_excluidos = [evento for evento in eventos_excluidos if evento.area_demandante == categoria]
    else:
        eventos_excluidos = Evento.query.filter(EventoConfirmado.confirmado.is_(False)).all()

    return render_template("eventos_excluidos.html", eventos=eventos_excluidos, form_filtro=form_filtro)





@app.route("/aprovar_evento/<int:evento_id>", methods=['GET', 'POST'])
def aprovar_evento(evento_id):
    evento = Evento.query.get_or_404(evento_id)

    # Verificar se o evento já foi aprovado anteriormente
    if event_already_approved(evento_id):
        flash("Evento aprovado com sucesso!", "success")
        return redirect(url_for('eventos_aprovados'))

    evento_confirmado = EventoConfirmado(evento_id=evento_id, confirmado=True)
    db.session.add(evento_confirmado)
    db.session.commit()

    # Pesonalizar os emails para cada setor
    emails_extras = [
        {'email': 'email1', 'subject': 'Subject for email1'},
        {'email': 'email2', 'subject': 'Subject for email2'},
        {'email': 'email3', 'subject': 'Subject for email3'}
    ]

    send_email(evento, 'Evento Aprovado', f'Olá,\n\nSeu evento "{evento.nome}" foi aprovado pela Cesar.\nData do evento: {evento.data_inicio}\nÁrea demandante: {evento.area_demandante}\n\nAtenciosamente,\nEquipe EventoCesar', emails_extras)
    flash("Evento aprovado com sucesso!", "success")
    return redirect(url_for('eventos_aprovados'))



def event_already_approved(evento_id):
    evento_confirmado = EventoConfirmado.query.filter_by(evento_id=evento_id, confirmado=True).first()
    return evento_confirmado is not None


@app.route("/eventos_aprovados", methods=["GET", "POST"])
def eventos_aprovados():
    form_filtro = FiltroForm()
    if form_filtro.validate_on_submit() and 'filtrar' in request.form:
        ordenar_data = form_filtro.ordenar_data.data
        categoria = form_filtro.categoria.data
        eventos_confirmados_aprovados = EventoConfirmado.query.filter_by(confirmado=True).all()

        if ordenar_data == 'asc':
            eventos_confirmados_aprovados.sort(key=lambda ec: ec.evento.data_inicio)
        else:
            eventos_confirmados_aprovados.sort(key=lambda ec: ec.evento.data_inicio, reverse=True)

        if categoria != "Todos":
            eventos_confirmados_aprovados = [ec for ec in eventos_confirmados_aprovados if ec.evento.area_demandante == categoria]

        eventos_aprovados = [ec.evento for ec in eventos_confirmados_aprovados]
    else:
        eventos_confirmados_aprovados = EventoConfirmado.query.filter_by(confirmado=True).all()
        eventos_aprovados = [ec.evento for ec in eventos_confirmados_aprovados]

    return render_template("eventos_aprovados.html", eventos=eventos_aprovados, form_filtro=form_filtro)


@app.route("/filtro_eventos", methods=["POST"])
def filtro_eventos():
    form_filtro = FiltroForm()
    if form_filtro.validate_on_submit() and 'filtrar' in request.form:
        ordenar_data = form_filtro.ordenar_data.data
        categoria = form_filtro.categoria.data
        # Armazene as opções de filtro na sessão para poderem ser acessadas em outras rotas
        session['ordenar_data'] = ordenar_data
        session['categoria'] = categoria
    # Verifique se a página de referência é uma das páginas de eventos e redirecione para a página apropriada, caso contrário, redirecione para uma página padrão
    if request.referrer and '/eventos_aprovados' in request.referrer:
        return redirect(url_for('eventos_aprovados'))
    else:
        return redirect(url_for('eventos'))



@app.route("/necessidade_melhoria/<int:evento_id>", methods=["POST"])
def necessidade_melhoria(evento_id):
    evento = Evento.query.get_or_404(evento_id)
    evento.necessidade_melhoria = True
    db.session.commit()

    improvement_text = request.json.get("improvementText", "")

    send_email(evento, 'Necessidade de Melhoria', f'Olá,\n\nO evento "{evento.nome}" foi marcado como necessitando de melhorias pela Cesar.\n\nMelhorias sugeridas:\n{improvement_text}\n\nAtenciosamente,\nEquipe EventoCesar')
    flash("Necessidade de melhoria marcada com sucesso!", "success")
    return jsonify({"status": "success"}), 200




@app.route("/cadastro_evento", methods=["GET", "POST"])
def cadastro_evento():
    form_evento = EventoForm()
    if form_evento.validate_on_submit() and 'botao_submit_cadastrarevento' in request.form:
        nome = form_evento.nome.data
        data_inicio = form_evento.data_inicio.data

        # Verificar se já existe um evento com o mesmo nome e data de início
        evento_existente = Evento.query.filter_by(nome=nome, data_inicio=data_inicio).first()
        if evento_existente:
            flash("Evento cadastrado com sucesso!", "success")
            return redirect(url_for('cadastro_evento'))

        evento = Evento(
            nome=nome,
            email_responsavel=form_evento.email_responsavel.data,
            area_demandante=form_evento.area_demandante.data,
            descricao=form_evento.descricao.data,
            data_inicio=data_inicio,
            data_fim=form_evento.data_fim.data,
            horario=form_evento.horario.data,
            intervalo=form_evento.intervalo.data,
            publico_participante=form_evento.publico_participante.data,
            quantidade_pessoas=form_evento.quantidade_pessoas.data or None,
            sala_reservada=form_evento.sala_reservada.data,
            local_reservado=form_evento.local_reservado.data or None,
            coffee_break=form_evento.coffee_break.data,
            necessidades_coffee_break=form_evento.necessidades_coffee_break.data or None,
            formato=form_evento.formato.data,
            link_zoom=str_to_bool(form_evento.link_zoom.data)
        )
        db.session.add(evento)
        db.session.commit()

        send_email(evento, 'Confirmação de Cadastro de Evento', 'Parabéns você conseguiu aprovação')

        flash("Evento cadastrado com sucesso!", "success")
        return redirect(url_for('cadastro_evento'))

    return render_template("cadastro_evento.html", form_evento=form_evento)