from flask import Flask
from flask import request
from threading import Thread
import time
import requests

app = Flask(__name__)


@app.route('/')
def home():
    return "Всё работает! Я живой и готов к работе!"


def run():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()

# app = Flask(__name__)


# @app.route('/')
# def index():
#     return '''<body style="margin: 0; padding: 0;">
#     <iframe width="100%" height="100%" src="https://axocoder.vercel.app/" frameborder="0" allowfullscreen></iframe>
#   </body>'''


# def run():
#     app.run(host='0.0.0.0', port=8080)


# def keep_alive():
#     t = Thread(target=run)
#     t.start()
