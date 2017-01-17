from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('test222.html')

@app.route('/testpost',methods=['POST'])
def testpost():
    aaa = request.form['test222']
    print request.method
    print aaa

    return 'post get'

if __name__ == '__main__':
    app.run()
