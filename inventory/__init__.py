from flask import Flask, render_template, redirect, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt  # Import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
login_manager = LoginManager(app)
login_manager.login_view = "Process_login"
# Configure the database URI and secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:VBD%40356598@localhost/flaskdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'

# Initialize database and Bcrypt
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)  # Initialize Bcrypt with the app

# User model with hashed password handling
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model,UserMixin):
    email = db.Column(db.String(30), primary_key=True)
    password = db.Column(db.String(512), nullable=False)

    def __init__(self, email, password):
        self.email = email
        self.password = self._hash_password(password)

    def _hash_password(self, password):
        # Use bcrypt to hash the password
        return bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        # Use bcrypt to check the hashed password
        return bcrypt.check_password_hash(self.password, password)
    def get_id(self):
        return self.email

class add_table(db.Model):
    product_id=db.Column(db.String(10), primary_key=True)
    name=db.Column(db.String(20), nullable=False)
    qty=db.Column(db.Integer(), nullable=False)
    price=db.Column(db.Integer(), nullable=False)
    
    def __init__(self,product_id,name,qty,price):
        self.product_id = product_id
        self.name = name
        self.qty = qty
        self.price = price


class sold_table(db.Model):
    product_id=db.Column(db.String(10), db.ForeignKey('add_table.product_id'),primary_key=True )
    name=db.Column(db.String(20),nullable=False)
    qty=db.Column(db.Integer(),nullable=False)
    
    def __init__(self,product_id,name,qty):
        self.product_id = product_id
        self.name = name
        self.qty = qty

if __name__ == "__main__":
    app.run(debug=True)

from . import route
    