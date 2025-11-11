from flask import Flask
from threading import Thread
import logging

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    # Hide Flask startup warnings
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
