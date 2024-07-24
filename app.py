from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import check_password_hash

# Aplicación init
# Crear la instancia de SQLAlchemy
db = SQLAlchemy()

def create_app():
    # Crear la aplicación Flask
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['SECRET_KEY'] = 'PASSWORD'

    # Inicializar SQLAlchemy con la aplicación Flask
    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app

app = create_app()

#Login Manager
Login_manager = LoginManager()
Login_manager.init_app(app)
Login_manager.login_view = 'login'

#Tablas de la base de datos
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(80), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    precio = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Producto {self.titulo}>'
    

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(80))


@Login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Rutas
@app.route('/')
def Home():
    productos = Producto.query.all() # Fetch todos los productos en la base de datos
    return render_template('home.html', productos=productos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        # check if user exists and password is correct
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('Home'))  # Use 'Home' instead of 'home'
        
        return 'Invalid username or password'
    
    return render_template('login.html')

# Rutas de los productos
@app.route('/productos', methods=['GET','POST'])
@login_required
def crear_producto():
    if request.method == 'POST':
        titulo = request.form.get('productName')
        descripcion = request.form.get('productDescription')
        precio = request.form.get('productPrice')
        product = Producto(titulo=titulo, descripcion=descripcion, precio=precio)
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('Home'))
    return render_template('create_product.html')

@app.route('/producto/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def Eliminar_Producto(id):
    producto = Producto.query.get(id)
    if producto:
        db.session.delete(producto)
        db.session.commit()
    return redirect(url_for('Home'))  # Note: I assume you meant 'Home', not 'home'



# Run aplicación
if __name__ == '__main__':
    app.run(debug=True)