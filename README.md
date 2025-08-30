Advanced QA Project: A Secure Microservices E-commerce App
This repository showcases a comprehensive, automated testing workflow for a distributed system. It features a complete e-commerce application built with a microservices architecture, fully containerized with Docker, and secured with token-based authentication.

The project is validated by a multi-layered testing strategy that includes API, End-to-End, and Contract tests. The entire build, test, and verification process is automated via a CI/CD pipeline using GitHub Actions.

System Architecture 🏗️
The application is composed of four independent, containerized services that communicate over a private network. A persistent PostgreSQL database provides the data layer.

Frontend Service: A Flask-based user interface that renders HTML and interacts with the backend APIs.

User Service: A Flask API responsible for user registration, login, and JWT token generation.

Product Service: A Flask API that manages all product data.

Order Service: A secure Flask API that handles order creation and history, requiring a valid JWT for access.

Database: A PostgreSQL database that stores user, product, and order information.

Multi-Layered Testing Strategy 🧪
This project demonstrates a robust, multi-layered approach to quality assurance suitable for complex, distributed systems:

API & End-to-End Tests: Written with PyTest, these tests validate the entire system's functionality. They cover individual service endpoints, security rules (e.g., rejecting requests without a valid token), and complete user journeys that span across multiple services.

Contract Tests: A Pact contract test is used to guarantee that the Order Service (the consumer) and Product Service (the provider) can communicate correctly. This allows for independent development and deployment with confidence, as it verifies the "contract" between services without requiring slow, full-scale integration tests for every change.

Tech Stack & Key Features 🛠️
Backend: Python & Flask

Frontend: Flask & Jinja2 Templates

Database: PostgreSQL & SQLAlchemy

Containerization: Docker

Orchestration: Docker Compose

CI/CD: GitHub Actions

Testing: PyTest, Requests, Pact

Key Concepts:

Microservices Architecture

REST APIs & Token-Based Authentication (JWT)

Persistent Database Management

Consumer-Driven Contract Testing

Automated CI/CD Pipelines

How to Run the Project Locally
The entire multi-service application is managed by Docker Compose.

Prerequisites: Ensure you have Docker and Docker Compose installed on your machine.

Clone the Repository: git clone <repository-url>

Navigate to Project Directory: cd qa-microservices-project

Build and Start All Services:

docker compose up --build

Initialize Databases: In a new terminal, run the init-db command for each backend service to create the necessary tables.

docker compose exec product-service flask init-db
docker compose exec order-service flask init-db
docker compose exec user-service flask init-db

Access the Application: Open your web browser and navigate to http://localhost:5000.

How to Run the Automated Tests
The tests are designed to run against the live, containerized application.

First, ensure the application is running via docker compose up.

Navigate to the tests directory: cd tests

Create and activate a virtual environment and install dependencies: pip install -r requirements.txt

Run API & Security Tests:

pytest test_api.py

Run Contract Tests:

# Step 1: Generate the contract (consumer test)
pytest test_contract.py

# Step 2: Verify the contract against the live Product Service
pact-verifier --provider-base-url=http://localhost:5001 --pact-url=./pacts/orderservice-productservice.json
