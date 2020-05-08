from equation import Equation
from time import sleep

from flask import Flask, request, render_template
import logging
import json
import random

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info(f'Response: {response!r}')
    return json.dumps(response)


def handle_dialog(res, req):
    if req['session']['new']:
        res['response'][
            'text'] = 'Вставьте химическое уравнение с элементами в\nскобках, за которым следует число атомов:'
        return
    res['response']['text'] = 'Вставьте химическое уравнение с элементами в\nскобках, за которым следует число атомов:'
    example = req['request']['original_utterance']


def set_balance(res, req, example):
    try:
        equation = Equation(example)
        res['response']['text'] = 'Сбалансированное уравнение: ' + equation.balance()
        return
    except IndexError:
        res['response']['text'] = 'ERROR...'
        res['response']['end_session'] = True
        return


@main.route('/')
def run_balance():
    # print('=================================================')
    # print('Вставьте химическое уравнение с элементами в\nскобках, за которым следует число атомов:')
    # print('Example: (H)2 + (O)2 = (H)2(O)1')
    user_input = request.form.get('equ_first')
    try:
        equation = Equation(user_input)
        print('Сбалансированное уравнение: ' + equation.balance())
        run_balance()
    except IndexError:
        print('Не верно...')
        run_balance()
    return render_template('index.html')


run_balance()

