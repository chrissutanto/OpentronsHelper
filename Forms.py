from flask_wtf import FlaskForm
from wtforms import StringField, FormField, FieldList, TextField, SubmitField

class fieldForm(FlaskForm):
    value = StringField('')

class modifyForm(FlaskForm):
    fields = FieldList(FormField(fieldForm))

class historyForm(FlaskForm):
    email = StringField("Email")
    description = TextField("Description")
    submit = SubmitField('Submit')