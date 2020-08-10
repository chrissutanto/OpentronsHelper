from flask_wtf import FlaskForm
from wtforms import StringField, FormField, FieldList, TextAreaField, SubmitField, validators
import email_validator

class fieldForm(FlaskForm):
    value = StringField('')

class modifyForm(FlaskForm):
    fields = FieldList(FormField(fieldForm))

class historyForm(FlaskForm):
    email = StringField("Email")
    description = TextAreaField("Description")
    submit = SubmitField('Submit')