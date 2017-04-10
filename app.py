# -*- coding: utf-8 -*-
from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
import configparser
from forms import User_Form, Profile_Form, Project_Form, EditProject_Form
from models import User, db, Project
from flask_mail import Mail, Message
import hashlib
from werkzeug.utils import secure_filename
import os
import math
import time

# configurar las imagen
UPLOAD_FOLDER = 'static/img/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
config = configparser.ConfigParser()
config.read('.env')
# configurar las imagen
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = config['DEFAULT']['SECRET_KEY']

app.config['MAIL_SERVER'] = config['DEFAULT']['EMAIL_HOST']
app.config['MAIL_USERNAME'] = config['DEFAULT']['EMAIL_HOST_USER']
app.config['MAIL_PASSWORD'] = config['DEFAULT']['EMAIL_HOST_PASSWORD']
app.config['MAIL_PORT'] = config['DEFAULT']['EMAIL_PORT']
app.config['MAIL_USE_SSL'] = config['DEFAULT']['EMAIL_SSL']



mail = Mail(app)

# Verificar que la imagen tiene la extension correcta
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Home
@app.route("/")
def index():
    if session.get('user'):
        my_user = User.query.filter_by(id=session['user']).first()
        return render_template('items/index.html', user=my_user, login=session['user'])
    else:
        my_user = None
        return render_template('items/index.html', user=my_user, login=False)
# Login 
@app.route("/login")
def login():
    form = User_Form(request.form)
    if request.args.get('email') and request.args.get('password1'):
        email = request.args.get('email')
        password = hashlib.md5(request.args.get('password1').encode('utf-8')).hexdigest()
        my_user = User.query.filter_by(email=email, password=password).first()
        if my_user:
            # Existe
            session['user'] = my_user.id
            return redirect(url_for('myProfile'))
        else:
            # lo tiramos
            flash('Su email o contraseña es incorrecto.', 'danger')
    if session.get('user'):
        my_user = User.query.filter_by(id=session['user']).first()
    else:
        my_user = None
    return render_template('items/login.html', user=my_user,form=form)

@app.route("/close")
def close_session():
    session.clear()
    return redirect(url_for('index'))
# Descubrir
@app.route("/discover")
def discover():
    if session.get('user'):
        my_user = User.query.filter_by(id=session['user']).first()
        projects = Project.query.all()
    else:
        my_user = None
        projects = Project.query.all()
        return render_template('items/discover.html', user=my_user, login=False, projects=projects)

    return render_template('items/discover.html', user=my_user, projects=projects)
# New
@app.route("/new")
def new():
    if session.get('user'):
        my_user = User.query.filter_by(id=session['user']).first()
        projects = Project.query.order_by(Project.project_created.desc())
    else:
        my_user = None
        projects = Project.query.order_by(Project.project_created.desc())
        return render_template('items/new.html', user=my_user, login=False, projects=projects)

    return render_template('items/new.html', user=my_user, projects=projects)
# Popular
@app.route("/popular")
def popular():
    if session.get('user'):
        my_user = User.query.filter_by(id=session['user']).first()
        projects = Project.query.order_by(Project.like.desc())
    else:
        my_user = None
        projects = Project.query.order_by(Project.like.desc())
        return render_template('items/popular.html', user=my_user, login=False, projects=projects)

    return render_template('items/popular.html', user=my_user, projects=projects)

# User profile
@app.route("/profile/", methods=['GET', 'POST'], defaults={'username': 'me'})
@app.route("/profile/<username>", methods=['GET', 'POST'])
def profile(username):
    if session.get('user'):
        my_user = User.query.filter_by(id=session['user']).first()
        nameUser= User.query.filter_by(username=username).first()
        id_user = nameUser.id
        project = Project.query.filter_by(id_user=id_user).first()
        projects = Project.query.filter_by(id_user=id_user).all()
        return render_template('items/profile.html', user=my_user, project=project, projects=projects, nameUser=nameUser)
    else:
        my_user = None
        id_user = nameUser.id
        project = Project.query.filter_by(id_user=id_user).first()
        nameUser= User.query.filter_by(username=username).first()
        projects = Project.query.filter_by(username=username).first()
        return render_template('items/profile.html', user=my_user, project=project, projects=projects, login=False, nameUser=nameUser)

@app.route("/myprofile", methods=['GET', 'POST'])
def myProfile():
    if session.get('user'):
        my_user = User.query.filter_by(id=session['user']).first()
        project = Project.query.filter_by(id_user=session['user']).first()
        projects = Project.query.filter_by(id_user=session['user']).all()
        return render_template('items/myprofile.html', user=my_user, project=project, projects=projects)

@app.route("/editprofile", methods=['GET', 'POST'])
def edit_profile():
    form = Profile_Form()
    my_user = User.query.filter_by(id=session['user']).first()
    if request.method == 'POST':
        #Comprobamos si desean cambiar la contraseña
        if form.password_anterior.data and form.password_nueva.data:
            # Comprobamos que la contraseña anterior es igual a la actual
            if  hashlib.md5(form.password_anterior.data.encode('utf-8')).hexdigest() == my_user.password:
                # Cambiamos en la base de datos
                my_user.password = hashlib.md5(form.password_nueva.data.encode('utf-8')).hexdigest()
                db.session.add(my_user)
                try:
                    db.session.commit()
                    flash('La contraseña ha sido modificada', 'success')
                except:
                    db.session.rollback()
                    flash('Ha ocurrido un error', 'danger')
            else:
                flash('Su contraseña anterior no es correcta', 'danger')
        # Cambiar Username
        my_user.username = form.username.data
        db.session.add(my_user)
        try:
            db.session.commit()
            flash('La contraseña ha sido modificada', 'success')
        except:
            db.session.rollback()
            flash('Ha ocurrido un error', 'danger')
        # Cambiar el avatar
        file = form.avatar.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            hora_unix = int(time.time())
            ruta = str(hora_unix) + filename
            file.save(os.path.join('static/img/projects/', ruta))
            # borrar imagen anterior
            if my_user.avatar != 'img/projects/default.png':
                os.remove(os.path.join('static', my_user.avatar))
            # Guardamos ruta en la base de datos
            my_user.avatar = os.path.join('img/projects/', ruta)
            db.session.add(my_user)
            try:
                db.session.commit()
            except:
                db.session.rollback()
                flash('Ha ocurrido un error', 'danger')
        else:
            flash('Debe ser una imagen.')
        # Cambiar el banner
        file = form.banner.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            hora_unix = int(time.time())
            ruta = str(hora_unix) + filename
            file.save(os.path.join('static/img/banner/', ruta))
            # borrar imagen anterior
            if my_user.banner != 'img/banner/default.jpg':
                os.remove(os.path.join('static', my_user.banner))
            # Guardamos ruta en la base de datos
            my_user.banner = os.path.join('img/banner/', ruta)
            db.session.add(my_user)
            try:
                db.session.commit()
            except:
                db.session.rollback()
                flash('Ha ocurrido un error', 'danger')
        else:
            flash('Debe ser una imagen.')

        # Redireccionar
        flash('Actualizado correctamente', 'success')
        return redirect(url_for('myProfile'))
        
        
    return render_template('items/editProfile.html', form=form, user=my_user)

@app.route("/uploadproject", methods=['GET', 'POST'])
def uploadproject():
    form = Project_Form()
    if request.method == 'POST'and form.validate():
        # Movemos la imagen a static
        file = form.image.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            hora_unix = int(time.time())
            ruta = str(hora_unix) + filename
            file.save(os.path.join('static/img/projects/', ruta))
        else:
            flash('Debe ser una imagen.')
        # Guardamos la info en la base de datos
        my_user = User.query.filter_by(id=session['user']).first()
        username = my_user.username
        my_project = Project(form.name.data, form.description.data, ruta, session['user'], username)
        db.session.add(my_project)
        try:
            db.session.commit()
            flash('Añadido correctamente', 'success')
            return redirect(url_for('myProfile'))
        except:
            db.session.rollback()
            flash('Ha ocurrido un error', 'danger')
    else:
        # Mostramos errores
        errores = form.errors.items()
        for campo, mensajes in errores:
            for mensaje in mensajes:
                flash(mensaje, 'danger')
    # obtenemos el usuario
    my_user = User.query.filter_by(id=session['user']).first()
    
    return render_template('items/uploadproject.html', form=form, user=my_user)

@app.route("/like/<project>")
def add_like(project):
    project_like = Project.query.filter_by(id=project).first()
    project_like.like = project_like.like + 1
    db.session.add(project_like)
    db.session.commit()
    return ''

@app.route("/editproject/<int:id>", methods=['GET', 'POST'])
def editProject(id):
    my_project = Project.query.filter_by(id=id).first()
    form = EditProject_Form()
    my_user = User.query.filter_by(id=session['user']).first()
    last_image = my_project.image
    if request.method == 'POST':
        # Cambiar titulo del proyecto
        my_project.name = form.name.data
        my_project.description = form.description.data
        db.session.add(my_project)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        # Cambiar la imagen del proyecto
        file = form.image.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            hora_unix = int(time.time())
            ruta = str(hora_unix) + filename
            file.save(os.path.join('static/img/projects/', ruta))
            # borrar imagen anterior
            if my_project.image == last_image:
                os.remove(os.path.join('static', my_project.image))
            # Guardamos ruta en la base de datos
            my_project.image = os.path.join('img/projects/', ruta)
            db.session.add(my_project)
            try:
                db.session.commit()
            except:
                db.session.rollback()
                flash('Ha ocurrido un error', 'danger')
        else:
            flash('Debe ser una imagen.')
        # Redireccionar
        flash('Actualizado correctamente', 'success')
        return redirect(url_for('myProfile'))

    return render_template('items/editProject.html', form=form, user=my_user, project=my_project)

@app.route("/deleteproject")
def deleteProject():
    my_project =  Project.query.filter_by(id_user=session['user']).first()
    db.session.delete(my_project)
    try:
        db.session.commit()
        flash('Proyecto eliminado', 'success')
    except:
        db.session.rollback()
        flash('Ha ocurrido un error', 'danger')
    return redirect(url_for('profile'))

# Sing up
@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = User_Form(request.form)
    #Comprobar el email esta en la base de datos
    if request.method == 'POST' and  form.validate():
        email= form.email.data
        my_user= User.query.filter_by(email=email).first()
        if not my_user:
            # Comprobar si coinciden las password
            if form.password1.data == form.password2.data:
                my_user = User(form.username.data, form.email.data, form.password1.data)
                db.session.add(my_user)
                try:
                    db.session.commit()
                    #Envio de email
                    msg = Message("Wellcome",
                                    sender="no-reply@projectportfolio.es",
                                    recipients=[form.email.data])
                    link_token = f'http://localhost:5000/confirmar/{my_user.token}'
                    msg.html = render_template('email/confirmar.html', link_token=link_token)
                    mail.send(msg)
                    #informamos al usuario
                    flash('Le acabamos de enviar un email con las instrucciones. Gracias.', 'success')
                
                    return redirect(url_for('login'))
                except:
                    db.session.rollback()
                    flash('Ha ocurrido un error', 'danger')
            else:
                flash('Las contraseñas no coinciden', 'danger')
        else:
            flash('El e-mail ya esta registrado', 'danger')
    else:
        #Mostramos errores
        errores = form.errors.items()
        for campo, mensajes in errores:
            for mensaje in mensajes:
                flash(mensaje, 'danger')

    if session.get('user'):
        my_user = User.query.filter_by(id=session['user']).first()
    else:
        my_user = None
    return render_template('items/signup.html', user=my_user,form=form)

@app.route("/confirmar/<token>")
def confirmar(token):
    my_user = User.query.filter_by(token=token).first()
    if my_user:
        my_user.active = True
        db.session.add(my_user)
        try:
            flash('Su cuenta ha sido activada.', 'success')
            db.session.commit()
        except:
            db.session.rollback()
    else:
        flash('Enlace caducado', 'danger')
    return redirect(url_for('login'))

@app.route("/search")
def search():
    projects = Project.query.all()
    if request.args.get('q'):
        projects = Project.query.filter(Project.name.contains(request.args.get('q'))).all()
    if session.get('user'):
        my_user = User.query.filter_by(id=session['user']).first()
    else:
        my_user = None

    return render_template('items/search.html', projects=projects, user=my_user)

if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0")
