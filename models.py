from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app import db



class Sale(db.Model):
    OrderNumber = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    price = db.Column(db.Float)
    client = db.Column(db.Integer)
    fullname = db.Column(db.String)
    address = db.Column(db.String(70))
    CardNumber = db.Column(db.String)
    products = db.relationship('Product', backref='sale')

    def get_products(self):
        a=[]
        for p in self.products:
            a.append(p.name)
        print(a)
        return a



class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float)
    description = db.Column(db.String(200))
    user_id = db.Column(db.String, db.ForeignKey('user.username'))
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.OrderNumber'))

    

class User(db.Model):
    username = db.Column(db.String(30), primary_key=True)
    key = db.Column(db.String, nullable=False)
    age= db.Column(db.Integer)
    address=db.Column(db.String)
    nation=db.Column(db.String(25))
    cart = db.relationship('Product', backref='user')
    is_admin = db.Column(db.Boolean, default=False)

    def  add_to_cart(self,producto):
        for p in self.cart:
            if p.id==producto.id:
                return False
        self.cart.append(producto)
        print("AÑADIDO CORRECTAMENTE")
        db.session.commit()
        print(self.cart)
        return True
            
        

    def  remove_from_cart(self,producto):
        for p in self.cart:
            if p.id == producto.id:
                self.cart.remove(p)
                db.session.commit()
                return True
        return False

    def is_active(self):
        return True  
    def get_id(self):
        return(self.username)
    def is_authenticated(self):
        return True  
