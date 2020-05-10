import pusher
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from .models import Message
from bs4 import BeautifulSoup as bs
from . import db
import requests as req

from .equation import Equation
from time import sleep

import logging
import json
import random

main = Blueprint('main', __name__)

pusher_client = pusher.Pusher(
    app_id='996676',
    key='fc2a090ac7e3a54357b1',
    secret='6c148af6fdf7524d0619',
    cluster='ap3',
    ssl=True
)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/calculator_one')
def mn():
    return render_template('calculator_one.html')


@main.route('/send', methods=['POST'])
def send():
    try:
        user_input = request.form.get('equ')
        equation = Equation(user_input)
        calc_success = 'Сбалансированное уравнение: ' + equation.balance()
        return render_template('calculator_one.html', t_class='alert alert-success alert-with-icon', total=calc_success)
    except IndexError:
        return render_template('calculator_one.html', t_class='alert alert-danger alert-with-icon',
                               total='Ошибка ввода!')


@main.route('/calculator_two')
def calculator_two():
    return render_template('calculator_two.html')


@main.route('/send_t', methods=['POST'])
def send_t():
    global request_t
    user_input = request.form.get('equ_t')
    if len(user_input.split(" ")) == 1:
        elem1 = user_input[0:user_input.index("+"):]
        elem2 = user_input[user_input.index("+") + 1::]
        return render_template('calculator_two.html', t_class='alert alert-success alert-with-icon',
                               total=elem1 + elem2)
    elif len(user_input.split(" ")) == 3:
        elem1, plus, elem2 = user_input.split(" ")
        url = "https://chemequations.com/ru/?s=" + elem1 + "+%2B+" + elem2 + "&ref=input"
        session = req.session()
        request_t = session.get(url)
    if request_t.status_code == 200:
        soup = bs(request_t.content, "html.parser")
        h1 = soup.find("h1")
        if h1 == None:
            h1 = soup.find("div", attrs={'class': 'alert alert-danger center'})
            h1 = h1.text
            return render_template('calculator_two.html', t_class='alert alert-danger alert-with-icon', total=h1)
        elif h1 != None:
            h1 = h1.text
        return render_template('calculator_two.html', t_class='alert alert-success alert-with-icon', total=h1)
    else:
        return render_template('calculator_two.html', t_class='alert alert-danger alert-with-icon',
                               total='Упс. Походу произошла поломка! Проблемы с сервером! (не с уравнением)')


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)


@main.route('/chat')
@login_required
def chat():
    messages = Message.query.all()

    return render_template('chat.html', messages=messages, name=current_user.name)


@main.route('/message', methods=['POST'])
def message():
    try:

        username = request.form.get('username')
        message = request.form.get('message')

        new_message = Message(username=username, message=message)
        db.session.add(new_message)
        db.session.commit()

        pusher_client.trigger('chat-channel', 'new-message', {'username': username, 'message': message})

        return jsonify({'result': 'success'})

    except:

        return jsonify({'result': 'failure'})
