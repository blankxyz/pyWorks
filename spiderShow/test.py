from flask import Flask, render_template
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from flask import request, url_for, flash, redirect

app = Flask(__name__)

class User():
    def __init__(self,username,email,password):
        username = username
        email = email
        password = password


class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=25)])
    email = TextField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.Required()])

@app.route('/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(form.username.data, form.email.data,
                    form.password.data)
        print user
        flash('Thanks for registering')
        return redirect(url_for('login'))
    return render_template('test.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
