#!/usr/bin/env python
# coding=utf-8

from flask import Flask, render_template
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField from wtforms.validators import Required

def is_me(form, field): #自定义check函数
    if field.data != 'yes':
        raise validators.ValidationError('Must input "yes"')<br>#FormField对象

class addressForm(Form):
    city = IntegerField('city', [validators.required()])
    area = IntegerField('area', [validators.required()])
    building = StringField('building')

#使用的例子 StringField IntegerField DateTimeField RadioField SelectField TextField TextAreaField FormField PasswordField SubmitField
class NameForm(Form):
    me = StringField('Is your self info?',[is_me,validators.Length(min=1,max=3)])
    name = StringField('What is your name?',
                       [validators.InputRequired('name'),
                       validators.Regexp('\w+', message="Must contain 0-9 aA-zZ")],
                       description='must input your name.',default=u'songyq')
    birthday  = DateTimeField('Your Birthday', format='%m/%d/%y')
    sex  = RadioField('Sex', choices=[(1,'man'),(2,'women')])
    age = DecimalField('How old are you?',
                       [validators.DataRequired('must be number!'),
                        validators.NumberRange(min=10, max=100, message='10~100')],
                       description='must input your age.')
    national = SelectField('national', choices=[('cn', 'china'), ('en', 'usa'), ('jp', 'japan')])
    address1 = TextAreaField('Address1', [validators.optional(), validators.length(max=200)])
    address2 = FormField(addressForm)
    phone = IntegerField('What is your phone number?',
                         [validators.InputRequired('phone')],
                         description='must input your phone.')
    password = PasswordField('New Password',
                             [validators.Required()])
    confirm = PasswordField('Repeat Password',
                            [validators.Required(),
                             validators.EqualTo('password', message='Passwords must match')])
    accept_tos = BooleanField('singe boy', [validators.Required()])
    email = TextField('Email Address', [validators.Length(min=6, message=(u'Little short for an email address?')),
                                        validators.Email(message=(u'That\'s not a valid email address.'))])
    submit = SubmitField('Submit')