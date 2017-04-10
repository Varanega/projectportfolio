from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FileField, TextAreaField
from wtforms.validators import InputRequired, Length, Email
from datetime import datetime

class User_Form(FlaskForm):
    username = StringField('Username', validators=[InputRequired('Debe introducir un nombre de usuario'),
                                              Length(1, 100, 'El nombre es demasiado largo')])
    email = StringField('E-mail', validators=[InputRequired('Debe introducir un e-mail'), Length(1, 80, 'El e-mail es demasiado largo'), Email('Tu e-mail no tiene una estructura correcta')])
    password1 = PasswordField('Contraseña', validators=[InputRequired('Necesitas indicar una contraseña')])
    password2 = PasswordField('Contraseña', validators=[InputRequired('Repita contraseña')])
    submit = SubmitField('Sign up')

class Profile_Form(FlaskForm):
    username = StringField('Username', validators=[InputRequired('Debe introducir un nombre de usuario'), Length(1, 100, 'El nombre es demasiado largo')])
    banner = FileField('El banner debe medir 828x175px')
    avatar = FileField('El avatar debe medir 200x200px')
    password_anterior = PasswordField('Contraseña actual', validators=[InputRequired('Necesitas indicar una contraseña')])
    password_nueva = PasswordField('Contraseña nueva', validators=[InputRequired('Necesitas indicar una contraseña')])
    submit = SubmitField('Modificar')

class Project_Form(FlaskForm):
    name =  StringField('Título del proyecto', validators=[InputRequired('Debe introducir un título para el proyecto'), Length(1, 100, 'El título es demasiado largo')])
    description =  TextAreaField('Descripción del proyecto', validators=[InputRequired('Debe introducir una descripción para el proyecto'), Length(1, 500, 'La descripción es demasiado largo')])
    image = FileField('La miniatura debe medir 202x158px')
    submit = SubmitField('Añadir')

class EditProject_Form(FlaskForm):
    name =  StringField('Título del proyecto', validators=[InputRequired('Debe introducir un título para el proyecto'), Length(1, 100, 'El título es demasiado largo')])
    description =  TextAreaField('Descripción del proyecto', validators=[InputRequired('Debe introducir una descripción para el proyecto'), Length(1, 500, 'La descripción es demasiado largo')])
    image = FileField('La miniatura debe medir 202x158px')
    submit = SubmitField('Modificar')