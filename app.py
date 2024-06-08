from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_bootstrap import Bootstrap  # Agrega esta línea para importar Bootstrap
from datetime import datetime
import math
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Clave secreta para la sesión
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'  # URL de la base de datos SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Desactiva el seguimiento de modificaciones
db = SQLAlchemy(app)  # Inicializa SQLAlchemy con la app Flask
login_manager = LoginManager(app)  # Inicializa el gestor de login
bootstrap = Bootstrap(app)  # Inicializa Bootstrap



@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')
