# tests/test_api.py

import requests
import random
import string

# Base URLs for our running services
PRODUCT_SERVICE_URL = "http://127.0.0.1:5001"
ORDER_SERVICE_URL = "http://127.0.0.1:5002"
USER_SERVICE_URL = "http://127.0.0.1:5003"

# --- Helper Function for Authentication ---

def get_auth_token():
    """Helper function to register and log in a new user, returning an auth token."""
    # Create a unique email for each test run to ensure isolation
    random_suffix = ''.join(random.choices(string.ascii_lowercase, k=8))
    email = f"testuser_{random_suffix}@example.com"
    password = "a-secure-password"

    # Register the new user
    register_response = requests.post(
        f"{USER_SERVICE_URL}/register",
        json={"email": email, "password": password}
    )
    assert register_response.status_code == 201, "Failed to register user for test"

    # Log in to get the token
    login_response = requests.post(
        f"{USER_SERVICE_URL}/login",
        json={"email": email, "password": password}
    )
    assert login_response.status_code == 200, "Failed to log in user for test"
    
    token = login_response.json().get("token")
    assert token, "Token not found in login response"
    return token

# ========== User Service Tests ==========

def test_user_registration_and_login():
    """Tests the full user registration and login flow."""
    random_suffix = ''.join(random.choices(string.ascii_lowercase, k=8))
    email = f"user_{random_suffix}@example.com"
    password = "a-strong-password"
    
    # Test successful registration
    register_payload = {"email": email, "password": password}
    response = requests.post(f"{USER_SERVICE_URL}/register", json=register_payload)
    assert response.status_code == 201
    
    # Edge Case: Test registering the same user again (should fail)
    response = requests.post(f"{USER_SERVICE_URL}/register", json=register_payload)
    assert response.status_code == 409 # Conflict
    
    # Test successful login
    login_payload = {"email": email, "password": password}
    response = requests.post(f"{USER_SERVICE_URL}/login", json=login_payload)
    assert response.status_code == 200
    assert "token" in response.json()
    
    # Edge Case: Test login with wrong password (should fail)
    bad_login_payload = {"email": email, "password": "wrong-password"}
    response = requests.post(f"{USER_SERVICE_URL}/login", json=bad_login_payload)
    assert response.status_code == 401 # Unauthorized

# ========== Product Service Tests (Unchanged) ==========

def test_get_all_products():
    """Tests if the /products endpoint returns a list of products."""
    response = requests.get(f"{PRODUCT_SERVICE_URL}/products")
    assert response.status_code == 200
    products = response.json()
    assert isinstance(products, list)
    assert len(products) > 0

# ========== Secure Order Service Tests ==========

def test_create_order_success():
    """Tests creating a valid order with a valid token."""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"product_id": 101, "quantity": 2}
    
    response = requests.post(f"{ORDER_SERVICE_URL}/orders", headers=headers, json=payload)
    
    assert response.status_code == 201
    assert "Order created successfully" in response.json()["message"]

def test_create_order_insufficient_stock():
    """Tests creating an order for a product with insufficient stock."""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"product_id": 102, "quantity": 999} # Stock is 75
    
    response = requests.post(f"{ORDER_SERVICE_URL}/orders", headers=headers, json=payload)
    
    assert response.status_code == 400
    assert "Insufficient stock" in response.json()["error"]

# --- Security Edge Case Tests ---

def test_create_order_no_token():
    """Tests that creating an order without a token fails."""
    headers = {"Content-Type": "application/json"}
    payload = {"product_id": 101, "quantity": 1}
    
    response = requests.post(f"{ORDER_SERVICE_URL}/orders", headers=headers, json=payload)
    
    assert response.status_code == 401
    assert "Token is missing" in response.json()["error"]

def test_create_order_invalid_token():
    """Tests that creating an order with a bad/invalid token fails."""
    token = "a-completely-invalid-token"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"product_id": 101, "quantity": 1}
    
    response = requests.post(f"{ORDER_SERVICE_URL}/orders", headers=headers, json=payload)
    
    assert response.status_code == 401
    assert "Token is invalid" in response.json()["error"]