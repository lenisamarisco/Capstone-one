from db import db  # Import db from the db.py file
from werkzeug.security import generate_password_hash, check_password_hash

# Recipe model
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.String(300), nullable=False)
    instructions = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Recipe('{self.name}', '{self.ingredients}')"

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    def set_password(self, password):
        """Sets the password after hashing it"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Checks the given password with the stored hashed password"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
