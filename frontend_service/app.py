# frontend_service/app.py

import os
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, make_response

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-default-secret-key')

# Service URLs
USER_SERVICE_URL = os.environ.get("USER_SERVICE_URL", "http://127.0.0.1:5003")
PRODUCT_SERVICE_URL = os.environ.get("PRODUCT_SERVICE_URL", "http://127.0.0.1:5001")
ORDER_SERVICE_URL = os.environ.get("ORDER_SERVICE_URL", "http://127.0.0.1:5002")

# --- Page Rendering Routes ---

@app.route("/")
def home():
    auth_token = request.cookies.get('auth_token')
    try:
        product_response = requests.get(f"{PRODUCT_SERVICE_URL}/products")
        product_response.raise_for_status()
        products = product_response.json()
    except requests.exceptions.RequestException:
        products = []
        flash("Could not connect to the Product Service.", "error")
        
    return render_template("index.html", products=products, logged_in=bool(auth_token))

@app.route("/register", methods=["GET", "POST"])
def register():
    # This function's logic is unchanged
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        try:
            response = requests.post(f"{USER_SERVICE_URL}/register", json={"email": email, "password": password})
            if response.status_code == 201:
                flash("Registration successful! Please log in.", "success")
                return redirect(url_for("login"))
            else:
                flash(response.json().get("error", "Registration failed."), "error")
        except requests.exceptions.RequestException:
            flash("Could not connect to the User Service.", "error")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    # This function's logic is unchanged
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        try:
            response = requests.post(f"{USER_SERVICE_URL}/login", json={"email": email, "password": password})
            if response.status_code == 200:
                auth_token = response.json().get("token")
                resp = make_response(redirect(url_for("home")))
                resp.set_cookie('auth_token', auth_token, httponly=True, samesite='Lax')
                flash("Login successful!", "success")
                return resp
            else:
                flash(response.json().get("error", "Invalid credentials."), "error")
        except requests.exceptions.RequestException:
            flash("Could not connect to the User Service.", "error")
    return render_template("login.html")

# --- NEW: Route for the "My Orders" page ---
@app.route("/orders")
def view_orders():
    """Fetches and displays the current user's order history."""
    auth_token = request.cookies.get('auth_token')
    if not auth_token:
        flash("You must be logged in to view your orders.", "error")
        return redirect(url_for("login"))

    headers = {"Authorization": f"Bearer {auth_token}"}
    orders = []
    try:
        response = requests.get(f"{ORDER_SERVICE_URL}/orders", headers=headers)
        if response.status_code == 200:
            orders = response.json()
        else:
            flash("Could not retrieve your orders.", "error")
    except requests.exceptions.RequestException:
        flash("Could not connect to the Order Service.", "error")

    return render_template("orders.html", orders=orders, logged_in=True)

# --- Action Routes ---

@app.route("/logout")
def logout():
    # This function's logic is unchanged
    resp = make_response(redirect(url_for("home")))
    resp.delete_cookie('auth_token')
    flash("You have been logged out.", "success")
    return resp

@app.route("/order/<int:product_id>", methods=["POST"])
def create_order(product_id):
    # This function's logic is unchanged
    auth_token = request.cookies.get('auth_token')
    if not auth_token:
        flash("You must be logged in to place an order.", "error")
        return redirect(url_for("login"))
    quantity = int(request.form.get("quantity", 1))
    headers = {"Authorization": f"Bearer {auth_token}"}
    payload = {"product_id": product_id, "quantity": quantity}
    try:
        response = requests.post(f"{ORDER_SERVICE_URL}/orders", headers=headers, json=payload)
        if response.status_code == 201:
            order_id = response.json().get("order_id")
            flash(f"Order #{order_id} created successfully!", "success")
        else:
            flash(f"Order failed: {response.json().get('error')}", "error")
    except requests.exceptions.RequestException:
        flash("Could not connect to the Order Service.", "error")
    return redirect(url_for("home"))

# --- NEW: Route to handle order cancellation ---
@app.route("/orders/cancel/<int:order_id>", methods=["POST"])
def cancel_order(order_id):
    """Sends a request to cancel a specific order."""
    auth_token = request.cookies.get('auth_token')
    if not auth_token:
        flash("You must be logged in to cancel an order.", "error")
        return redirect(url_for("login"))

    headers = {"Authorization": f"Bearer {auth_token}"}
    try:
        response = requests.delete(f"{ORDER_SERVICE_URL}/orders/{order_id}", headers=headers)
        if response.status_code == 200:
            flash("Order cancelled successfully.", "success")
        else:
            flash(response.json().get("error", "Could not cancel order."), "error")
    except requests.exceptions.RequestException:
        flash("Could not connect to the Order Service.", "error")

    return redirect(url_for("view_orders"))

if __name__ == '__main__':
    app.run(port=5000, debug=True)