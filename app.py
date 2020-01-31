from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World! 3 "

@app.route("/webhook", methods=["POST","GET"])
def webhook():
    return "webhook"