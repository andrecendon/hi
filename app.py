import Flask
from flask import render_template, request, flash, redirect, url_for, jsonify, abort
from flask_login import current_user, login_required,login_user, logout_user
import atexit
from datetime import datetime
import math
import random
from functools import wraps
import signal
app = Flask(__name__)



@app.route('/', methods=['GET', 'POST'])
def hello():
    mensaje = None
    
    return render_template('index.html', mensaje=mensaje)

@app.route('/register', methods=['GET','POST'])
def register():
    
    mensaje=None
    if request.method == 'POST':
       
        
       
        return redirect(url_for('search'))
        
        
    return render_template('register.html')
