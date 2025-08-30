# order_service/app.py

import os
import requests
import jwt
from functools import wraps
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
db = SQLAlchemy(app)

PRODUCT_SERVICE_URL = "http://product-service:5001"

# --- Database Model (Unchanged) ---
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)

    def to_dict(self):
        """Converts the order object to a dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'quantity': self.quantity,
            'total_price': self.total_price
        }

# --- Token Verification Decorator (Unchanged) ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user_id = data['user_id']
        except Exception:
            return jsonify({'error': 'Token is invalid'}), 401
        return f(current_user_id, *args, **kwargs)
    return decorated

# --- API Endpoints ---

@app.route("/orders", methods=["POST"])
@token_required
def create_order(current_user_id):
    # This function's logic is unchanged
    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity")
    # ... (rest of the create_order logic is the same)
    if not product_id or not quantity: return jsonify({"error": "Product ID and quantity are required"}), 400
    try:
        product_response = requests.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}")
        if product_response.status_code == 404: return jsonify({"error": "Product not found"}), 404
        product_response.raise_for_status()
        product = product_response.json()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Could not connect to Product Service: {e}"}), 503
    if product["stock"] < quantity: return jsonify({"error": "Insufficient stock"}), 400
    total_price = product["price"] * quantity
    new_order = Order(user_id=current_user_id, product_id=product_id, product_name=product["name"], quantity=quantity, total_price=total_price)
    db.session.add(new_order)
    db.session.commit()
    return jsonify({"message": "Order created successfully", "order_id": new_order.id}), 201

# --- NEW: Endpoint to get a user's orders ---
@app.route("/orders", methods=["GET"])
@token_required
def get_orders(current_user_id):
    """Returns all orders placed by the current user."""
    orders = Order.query.filter_by(user_id=current_user_id).all()
    return jsonify([order.to_dict() for order in orders])

# --- NEW: Endpoint to cancel an order ---
@app.route("/orders/<int:order_id>", methods=["DELETE"])
@token_required
def cancel_order(current_user_id, order_id):
    """Cancels an order, verifying ownership first."""
    # Security Check: Find the order that both has the right ID AND belongs to the current user.
    order = Order.query.filter_by(id=order_id, user_id=current_user_id).first()

    # Edge Case: If the order doesn't exist or belongs to another user, return 404.
    if not order:
        return jsonify({"error": "Order not found or you do not have permission to cancel it"}), 404
    
    db.session.delete(order)
    db.session.commit()
    return jsonify({"message": "Order cancelled successfully"}), 200

# ... (init-db command and main block are unchanged) ...
@app.cli.command("init-db")
def init_db_command():
    db.create_all()
    print("Order database initialized.")
if __name__ == '__main__':
    app.run(port=5002, debug=True)