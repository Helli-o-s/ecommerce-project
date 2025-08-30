# user_service/app.py

import os
import datetime
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-super-secret-key') # It's better to set this in the environment
db = SQLAlchemy(app)

# --- Database Model ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        """Hashes the password and stores it."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)

# --- API Endpoints ---
@app.route("/register", methods=["POST"])
def register():
    """Handles user registration."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # --- Edge Case Handling ---
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email address already in use"}), 409 # 409 Conflict
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters long"}), 400
    # --- End of Edge Cases ---

    new_user = User(email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@app.route("/login", methods=["POST"])
def login():
    """Handles user login and JWT generation."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    # --- Security Consideration ---
    # Check if user exists AND if the password is correct in one go.
    # Return a generic error to prevent attackers from knowing if an email is registered.
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401 # 401 Unauthorized

    # --- Token Generation ---
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({"token": token})

# --- Database Initialization Command ---
@app.cli.command("init-db")
def init_db_command():
    """Creates the database tables for the User service."""
    db.create_all()
    print("User database initialized.")

if __name__ == '__main__':
    app.run(port=5003, debug=True)