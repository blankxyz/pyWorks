from flask import Flask
from flask import render_template, request, session, url_for, flash, redirect

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('debug.html')


if __name__ == '__main__':
    app.run(port=8000)
