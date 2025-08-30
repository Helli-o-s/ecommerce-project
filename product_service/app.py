# product_service/app.py

import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure the database connection using the environment variable
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Product database model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        """Converts the product object to a dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'stock': self.stock
        }

@app.route("/products", methods=["GET"])
def get_products():
    """Returns the list of all products from the database."""
    products = Product.query.all()
    return jsonify([product.to_dict() for product in products])

@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """Returns the details of a specific product from the database."""
    product = Product.query.get(product_id)
    if product:
        return jsonify(product.to_dict())
    return jsonify({"error": "Product not found"}), 404

# A command to initialize the database and seed it with data
@app.cli.command("init-db")
def init_db_command():
    """Creates the database tables and seeds them with initial data."""
    db.create_all()
    # Seed with some initial products if the table is empty
    if Product.query.count() == 0:
        db.session.add(Product(id=101, name="Wireless Mouse", price=24.99, stock=150))
        db.session.add(Product(id=102, name="Mechanical Keyboard", price=79.99, stock=75))
        db.session.add(Product(id=103, name="4K Webcam", price=129.50, stock=40))
        db.session.commit()
    print("Database initialized and seeded.")

if __name__ == '__main__':
    app.run(port=5001, debug=True)