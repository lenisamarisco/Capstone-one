import os
import json
import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from db import db  # Import db from db.py
from models import Recipe, User  # Import models

# Initialize the Flask app
app = Flask(__name__)

# Configure the app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Use a real database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your_secret_key')  # Use environment variable for security

# Initialize the db
db.init_app(app)

# Create a flag to check if it's the first request
is_first_request = True
mock_session = {}
@app.before_request
def before_request():
    global is_first_request
    if is_first_request:
        db.create_all()  # Create tables only before the first request
        is_first_request = False

# Serve favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/x-icon'
    )

# Example ingredient substitutions
ingredient_substitutions = {
    'milk': ['almond milk', 'soy milk', 'oat milk'],
    'eggs': ['flaxseed meal', 'banana', 'applesauce']
}

@app.route('/')
def index():
    return render_template('index.html')

# Recipe search route (calls external recipe API)
@app.route('/filter_recipes', methods=['POST'])
def filter_recipes():
    ingredients = request.json['ingredients']
    
    # Retrieve your API keys from environment variables or configuration
    EDAMAM_API_KEY = '872bd5bf6359ec9288249af806c13245'
    EDAMAM_APP_ID = '63eba0ec'
    SPOONACULAR_API_KEY = '808f16d500b342f2848e5cb957889554'

    if not EDAMAM_API_KEY or not EDAMAM_APP_ID:
        return jsonify({'error': 'API keys are missing from environment variables'}), 400

    # Edamam API URL
    EDAMAM_API_URL = 'https://api.edamam.com/api/recipes/v2'
    edamam_url = f"{EDAMAM_API_URL}?type=public&q={','.join(ingredients)}&app_id={EDAMAM_APP_ID}&app_key={EDAMAM_API_KEY}"

    # Spoonacular API URL
    SPOONACULAR_API_URL = 'https://api.spoonacular.com/recipes/complexSearch'
    spoonacular_url = f"{SPOONACULAR_API_URL}?apiKey={SPOONACULAR_API_KEY}&query={','.join(ingredients)}"

    try:
        edamam_recipes = []
        if "edamam_recipes" in mock_session:
            edamam_recipes = mock_session["edamam_recipes"]
        if not edamam_recipes:     
        # Send request to Edamam API
            print("making edamam api calls") 
            edamam_response = requests.get(edamam_url)
            if edamam_response.status_code==200:
                edamam_recipes = edamam_response.json()
                
        
        spoonacular_recipes = []
        if "spoonacular_recipes" in mock_session:
            spoonacular_recipes = mock_session["spoonacular_recipes"]
        if not spoonacular_recipes:     
        # Send request to Spoonacular API
            print("making spoonacular api calls") 
            spoonacular_response = requests.get(spoonacular_url)
            if spoonacular_response.status_code==200:
               spoonacular_recipes = spoonacular_response.json()

        if edamam_recipes and spoonacular_recipes:
           # edamam_recipes = edamam_response.json()
           # spoonacular_recipes = spoonacular_response.json()

            mock_session["edamam_recipes"]= edamam_recipes
            mock_session["spoonacular_recipes"]= spoonacular_recipes
            
            # Combine recipes from both APIs
            
            recipes_list = []

            # Edamam recipes
            recipes_list.extend([{
                'name': recipe['recipe']['label'],
                'image': recipe['recipe']['image'],
                'description': recipe['recipe'].get('description', 'No description available'),
                'url': recipe['recipe']['url']
            } for recipe in edamam_recipes['hits']])

            # Spoonacular recipes
            recipes_list.extend([{
                'name': recipe['title'],
                'image': recipe['image'],
                'description': 'No description available',  # Spoonacular does not provide descriptions directly
                'url': f"https://spoonacular.com/recipes/{recipe['title'].replace(' ', '-').lower()}-{recipe['id']}"
            } for recipe in spoonacular_recipes['results']])

            return jsonify(recipes_list)
        else:
            return jsonify({'error': f"API request failed with status code {edamam_response.status_code} or {spoonacular_response.status_code}"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f"Request failed: {str(e)}"}), 500

@app.route('/substitute_ingredient', methods=['POST'])
def substitute_ingredient():
    ingredient = request.json['ingredient']
    substitutes = ingredient_substitutions.get(ingredient, [])
    return jsonify(substitutes)

# User sign-up route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Hash the password (no need for method='sha256')
        hashed_password = generate_password_hash(password)
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        
        if existing_user:
            return render_template('register.html', message="Username already exists")

        # Create a new user
        new_user = User(username=username,password_hash= hashed_password, email=email)
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login'))

    return render_template('register.html')

# User login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id  # Store user id in session
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', message="Invalid username or password")

    return render_template('login.html')

# User dashboard route
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)

# User logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# Run the app
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, port=port)
