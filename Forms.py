from flask_wtf import FlaskForm
from wtforms import StringField, FormField, FieldList, TextAreaField, SubmitField, validators, PasswordField
import email_validator

class fieldForm(FlaskForm):
    value = StringField('')

class modifyForm(FlaskForm):
    fields = FieldList(FormField(fieldForm))

class historyForm(FlaskForm):
    email = StringField("Email")
    description = TextAreaField("Description")
    submit = SubmitField('Submit')

class emailForm(FlaskForm):
    email = StringField("Email")
    password = PasswordField("Password")
    submit = SubmitField('Submit')