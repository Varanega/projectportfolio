from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import hashlib
import time
from datetime import datetime
import configparser


app = Flask(__name__)
config = configparser.ConfigParser()
config.read('.env')

config['DEFAULT']['DEBUG']
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://' + config['DEFAULT']['DB_USER'] + '@' + config['DEFAULT']['DB_HOST'] + '/' + config['DEFAULT']['DB_NAME']
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(32))
    avatar = db.Column(db.String(500))
    banner = db.Column(db.String(500))
    active = db.Column(db.Boolean())
    token = db.Column(db.String(32))
    project = db.relationship('Project', backref='user', lazy='dynamic')
    user_created = db.Column(db.DateTime)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = hashlib.md5(password.encode('utf-8')).hexdigest()
        self.active = False
        self.avatar = 'img/avatars/default.png'
        self.banner = 'img/banner/default.jpg'
        #Generar un token de 32 caracteres aleatorios
        self.token = hashlib.md5(str(time.time()).encode('utf-8')).hexdigest()
        self.user_created = datetime.utcnow()

    def __repr__(self):
        return '<User %r>' % self.username

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(500))
    image = db.Column(db.String(500))
    like = db.Column(db.Integer)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'))
    username = db.Column(db.String(80))
    project_created = db.Column(db.DateTime)

    def __init__(self, name, description, ruta, id_user, username):
        self.name = name
        self.description = description
        self.image = ruta
        self.like = 0
        self.id_user = id_user
        self.username = username
        self.project_created = datetime.utcnow()

    def __repr__(self):
        return '<Project %r>' % self.name
        