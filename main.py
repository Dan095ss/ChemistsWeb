import pusher
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from .models import Message
from . import db

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


