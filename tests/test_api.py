import requests

# Base URLs for our running services
PRODUCT_SERVICE_URL = "http://127.0.0.1:5001"
ORDER_SERVICE_URL = "http://127.0.0.1:5002"

# ========== Product Service Tests ==========

def test_get_all_products():
    """Tests if the /products endpoint returns a list of products."""
    response = requests.get(f"{PRODUCT_SERVICE_URL}/products")
    assert response.status_code == 200
    products = response.json()
    assert isinstance(products, dict)
    assert "101" in products  # Check for a known product ID

def test_get_valid_product():
    """Tests fetching a single, valid product."""
    response = requests.get(f"{PRODUCT_SERVICE_URL}/products/102")
    assert response.status_code == 200
    product = response.json()
    assert product["name"] == "Mechanical Keyboard"
    assert "price" in product

def test_get_invalid_product():
    """Tests fetching a non-existent product, expecting a 404 error."""
    response = requests.get(f"{PRODUCT_SERVICE_URL}/products/999")
    assert response.status_code == 404
    assert "error" in response.json()

# ========== Order Service Tests (End-to-End) ==========

def test_create_order_success():
    """
    Tests the full end-to-end flow of creating a valid order.
    This test requires both services to be running and communicating.
    """
    payload = {"product_id": "103", "quantity": 5}
    response = requests.post(f"{ORDER_SERVICE_URL}/orders", json=payload)
    
    assert response.status_code == 201  # 201 Created
    order = response.json()
    assert order["product_name"] == "4K Webcam"
    assert order["quantity"] == 5
    assert order["total_price"] == 129.50 * 5

def test_create_order_insufficient_stock():
    """Tests creating an order for a product with insufficient stock."""
    # Product 103 has 40 in stock
    payload = {"product_id": "103", "quantity": 100}
    response = requests.post(f"{ORDER_SERVICE_URL}/orders", json=payload)
    
    assert response.status_code == 400
    assert "Insufficient stock" in response.json()["error"]

def test_create_order_product_not_found():
    """Tests creating an order for a product that does not exist."""
    payload = {"product_id": "999", "quantity": 1}
    response = requests.post(f"{ORDER_SERVICE_URL}/orders", json=payload)
    
    assert response.status_code == 404
    assert "Product not found" in response.json()["error"]