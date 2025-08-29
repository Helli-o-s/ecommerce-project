from flask import Flask, jsonify

app = Flask(__name__)

# In-memory database for products
products = {
    "101": {"name": "Wireless Mouse", "price": 24.99, "stock": 150},
    "102": {"name": "Mechanical Keyboard", "price": 79.99, "stock": 75},
    "103": {"name": "4K Webcam", "price": 129.50, "stock": 40},
}

@app.route("/products", methods=["GET"])
def get_products():
    """Returns the list of all products."""
    return jsonify(products)

@app.route("/products/<product_id>", methods=["GET"])
def get_product(product_id):
    """Returns the details of a specific product."""
    product = products.get(product_id)
    if product:
        return jsonify(product)
    return jsonify({"error": "Product not found"}), 404

if __name__ == '__main__':
    # Running on port 5001 to distinguish it from other services
    app.run(port=5001, debug=True)