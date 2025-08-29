import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory database for orders
orders = []
order_id_counter = 1

# The URL for the Product Service. For now, it's hardcoded.
# We will improve this later with Docker Compose.
PRODUCT_SERVICE_URL = "http://product-service:5001"

# in order_service/app.py

@app.route("/orders", methods=["POST"])
def create_order():
    """
    Creates a new order.
    Expects a JSON payload like: {"product_id": "102", "quantity": 2}
    """
    global order_id_counter
    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity")

    if not product_id or not quantity:
        return jsonify({"error": "Product ID and quantity are required"}), 400

    # --- Microservice Communication (Corrected Logic) ---
    try:
        product_response = requests.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}")
        
        # Step 1: Specifically check for the 404 case first.
        if product_response.status_code == 404:
            return jsonify({"error": "Product not found"}), 404
        
        # Step 2: For any other errors, raise an exception.
        product_response.raise_for_status()
        
        product = product_response.json()

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Could not connect to Product Service: {e}"}), 503
    # --- End of Communication ---
    
    if product["stock"] < quantity:
        return jsonify({"error": "Insufficient stock"}), 400

    total_price = product["price"] * quantity
    new_order = {
        "order_id": order_id_counter,
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "total_price": total_price
    }
    orders.append(new_order)
    order_id_counter += 1

    return jsonify(new_order), 201

if __name__ == '__main__':
    # Running on port 5002 to avoid conflicts
    app.run(port=5002, debug=True)