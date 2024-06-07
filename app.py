from flask import render_template, request, flash, redirect, url_for, jsonify, abort
from flask_login import current_user, login_required,login_user, logout_user
import atexit
from datetime import datetime
import math
import random
from functools import wraps
import signal




# eCommerce/app/models.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'clave_secreta'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
bootstrap = Bootstrap(app)


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

###   ERRORS   AND   AUTHENTICATION ###

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin==True:
            abort(403) 
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_admin==True:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403


@login_manager.user_loader
def load_user(username):
    return User.query.get(username)


####    VIEWS    ####

@app.route('/register', methods=['GET','POST'])
def register():
    
    mensaje=None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        age = request.form['age']
        address = request.form['address']
        nation = request.form['nation']
        
       
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            mensaje="This username is occupied"
            return render_template('register.html',mensaje=mensaje)

        new_user = User(username=username, key=password, age=age, address=address, nation=nation)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        
       
        return redirect(url_for('search'))
        
        
    return render_template('register.html')



@app.route('/', methods=['GET', 'POST'])
def hello():
    mensaje = None
    logout_user()
    
    if request.method == 'POST':
        user = request.form['username']
        password = request.form['password']
        
        usuario1 = User.query.filter_by(username=user).first()
        
        if usuario1 and usuario1.key == password:
            login_user(usuario1)
            if usuario1.is_admin==False:
                return redirect(url_for('search'))
            else:
                return redirect(url_for('admin_main'))
            
        else:
            mensaje = "User or password wrong."
            return render_template('index.html', mensaje=mensaje)  # Renderizar index.html con el mensaje de error
    
    return render_template('index.html', mensaje=mensaje)



@app.before_request
def before_request():
    if hasattr(app, 'closing'):
        logout_user()
        
        return
    
    return




@app.route('/user')
@login_required
@user_required
def user():
    productos = Product.query.all()
    usuarios = User.query.all()
    return render_template('user.html',productos=productos, usuarios=usuarios)


@app.route('/logout')
@login_required
@user_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/search', methods=['GET'])
@login_required
@user_required
def search(mensaje=""):
   
    query = request.args.get('query')  
    message = request.args.get('message','')
    if query:
        results = Product.query.filter(Product.name.ilike(f'%{query}%')).all()
        if results is None:
            results = Product.query.filter(Product.id.ilike(f'%{query}%')).all()
        
    else:
        results = Product.query.all()
    
    
    return render_template('search.html', contador=len(current_user.cart), query=query, results=results, message=message)


@app.route('/admin_main', methods=['GET','POST'])
@login_required
@admin_required
def admin_main():
    return render_template('admin_main.html')


@app.route('/siu/<int:producto_id>', methods=['GET','POST'])
@login_required
@user_required
def siu(producto_id):
    
    if current_user.add_to_cart(Product.query.get(producto_id)) == False:
        message = "The product is already in the cart"
    else:
        message = "Product added to the cart"
    
    return redirect("/search?message=" + message)



@app.route('/siu2/<int:producto_id>', methods=['GET'])
@login_required
@user_required
def siu2(producto_id):    
    #print("Bef ", current_user.cart)
    current_user.remove_from_cart(Product.query.get(producto_id))
    #print("Aft ", current_user.cart)

    return redirect('/cart')



@app.route('/checkout', methods=['GET','POST'])
@login_required
@user_required
def checkout():
    total = sum(product.price for product in current_user.cart)
    
    if request.method == 'POST':
        fullname = request.form['fullname']
        CardNumber = request.form['cardnumber']
        address = request.form['address']
        random_number = random.random()
        

       
        order_number = math.floor(random_number * 1000000)
        id=current_user.username
        new_order=Sale()
        order_number = order_number if order_number else str(random.randint(100000, 999999))
            
        new_sale = Sale(
                OrderNumber=order_number,
                date=datetime.now(),
                price=total,
                client=current_user.username, 
                fullname=fullname,
                address=address, 
                CardNumber=CardNumber,
                products=current_user.cart
        )
        db.session.add(new_sale)
        db.session.commit()
        
       
        

        return redirect(url_for('checkout2', order_number=order_number))
    return render_template('checkout.html', total=total)

@app.route('/checkout2/<int:order_number>', methods=['GET'])
@login_required
@user_required
def checkout2(order_number):
    sale = Sale.query.get_or_404(order_number)
    return render_template('checkout2.html', sale=sale, products_id=sale.get_products() )

@app.route('/sales')
@login_required
@admin_required
def sales():
    sales_list = Sale.query.all()
    total=0
    for s in sales_list:
        total+=s.price
    return render_template('sales.html', sales_list=sales_list, total=total)

@app.route('/cart', methods=['GET','POST'])
@login_required
@user_required
def cart():
    mensaje=None
    if(len(current_user.cart)==0):
        mensaje="The cart is empty"
   
    return render_template('cart.html', mensaje=mensaje)

@app.route('/add_videogame', methods=['GET','POST'])
@login_required
@admin_required
def add_videogame():
    mensaje=None
    if request.method == 'POST':
        id = request.form.get('id')
        name = request.form.get('name')
        price = request.form.get('price')
        description = request.form.get('description')
        user_id = request.form.get('user_id')
        sale_id = request.form.get('sale_id')
        
        
        new_product = Product(id=id, name=name, price=price, description=description, user_id=user_id, sale_id=sale_id)
        
        try:
            db.session.add(new_product)
            db.session.commit()
            mensaje = "Product successfully added"
            return render_template('add_videogame.html', mensaje=mensaje)
        
        except:
            mensaje = "Error adding product"
            return render_template('add_videogame.html',mensaje=mensaje)
        
        
    return render_template('add_videogame.html')


@app.route('/add_admin', methods=['GET','POST'])
@admin_required
def add_admin():
    mensaje=None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        age = request.form['age']
        address = request.form['address']
        nation = request.form['nation']
        
       
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            mensaje="This username is occupied"
            return render_template('add_admin.html',mensaje=mensaje)

        new_user = User(username=username, key=password, age=age, address=address, nation=nation, is_admin=True)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        mensaje="Admin added correctly"
       
    return render_template('add_admin.html',mensaje=mensaje)

@app.route('/modify_videogame', methods=['GET','POST'])
@admin_required
def modify_videogame(mensaje=""):
    query = request.args.get('query')  
    message = request.args.get('message','')
    if query:
        results = Product.query.filter(Product.name.ilike(f'%{query}%')).all()
        if results is None:
            results = Product.query.filter(Product.id.ilike(f'%{query}%')).all()
        
    else:
        results = Product.query.all()
    
    
    return render_template('modify_videogame.html', contador=len(current_user.cart), query=query, results=results, message=message)


@app.route('/modify_videogame2', methods=['GET','POST'])
@admin_required
def modify_videogame2(mensaje=""):
    product_id = request.args.get('product_id')
    videogame = Product.query.get(product_id)
    if request.method == 'POST':
        id = request.form.get('id')
        name = request.form.get('name')
        price = request.form.get('price')
        description = request.form.get('description')
        
        videogame = Product.query.get(id)
        if videogame:
            videogame.name = name
            videogame.price = price
            videogame.description = description
            db.session.commit()
        return redirect('/admin_main')


    
    return render_template('modify_videogame2.html', videogame=videogame)




### MAIN  ###

if __name__ == '__main__':
    with app.app_context():  
        
        db.drop_all()
        db.create_all()

        usuarios = [
            User(username="Felipe", key="f123"),
            User(username="Ana", key="a456"),
            User(username="Juan", key="j789"),
            User(username="Maria", key="m987"),
            User(username="Carlos", key="c654"),
            User(username="admin1", key="a1",is_admin=True)
        ]

       
    
        
        for usuario in usuarios:
            db.session.add(usuario)


        


        productos = [
            Product(id="1", name="Call of Duty: Modern Warfare", price=59.99),
            Product(id="2", name="FIFA 22", price=49.99),
            Product(id="3", name="Assassin's Creed Valhalla", price=59.99),
            Product(id="4", name="The Last of Us Part II", price=49.99),
            Product(id="5", name="Cyberpunk 2077", price=49.99),
            Product(id="6", name="Red Dead Redemption 2", price=59.99),
            Product(id="7", name="Minecraft", price=19.99),
            Product(id="8", name="Grand Theft Auto V", price=29.99),
            Product(id="9", name="Fortnite: Darkfire Bundle", price=29.99),
            Product(id="10", name="God of War", price=19.99),
            Product(id="11", name="Mario Kart 8 Deluxe", price=59.99),
            Product(id="12", name="The Legend of Zelda: Breath of the Wild", price=59.99),
            Product(id="13", name="Super Mario Odyssey", price=59.99),
            Product(id="14", name="Animal Crossing: New Horizons", price=59.99),
            Product(id="15", name="Battlefield 2042", price=59.99),
            Product(id="16", name="Halo Infinite", price=59.99),
            Product(id="17", name="Overwatch", price=39.99),
            Product(id="18", name="Apex Legends: Bloodhound Edition", price=19.99),
            Product(id="19", name="Final Fantasy VII Remake", price=49.99),
            Product(id="20", name="DOOM Eternal", price=39.99),
            Product(id="21", name="Mortal Kombat 11", price=39.99),
            Product(id="22", name="League of Legends: RP (1380)", price=19.99),
            Product(id="23", name="Among Us", price=4.99),
            Product(id="24", name="Rocket League", price=19.99),
            Product(id="25", name="Pokémon Sword and Shield", price=59.99)
        ]

        for producto in productos:
            db.session.add(producto)

        db.session.commit()
        
        

    app.run(debug=True, port=80)
    
    
