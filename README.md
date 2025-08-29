Advanced QA Project: A Microservices E-commerce App
This project showcases a comprehensive, automated testing workflow for a distributed system. It features a simple e-commerce application built with a microservices architecture, fully containerized with Docker, and tested with a multi-layered strategy that includes API, End-to-End, and Contract tests.

The entire process is automated via a CI/CD pipeline using GitHub Actions, demonstrating a professional-grade approach to quality assurance in a modern software environment.

System Architecture 🏗️
The application is composed of two independent backend microservices that communicate with each other over a private network. This architecture allows for independent development, deployment, and scaling of services.

Product Service: A Flask API responsible for managing product data (name, price, stock).

Order Service: A Flask API that handles order creation. It communicates with the Product Service to validate product details and availability.

Multi-Layered Testing Strategy 🧪
This project demonstrates a robust, multi-layered approach to quality assurance suitable for complex, distributed systems:

API Tests: Each service's endpoints are tested in isolation to ensure their individual logic is correct.

End-to-End (E2E) Tests: User journeys that span across multiple services (e.g., creating a valid order) are tested to ensure the system works together as a whole.

Contract Tests: A Pact contract test is used to guarantee that the Order Service (the consumer) and Product Service (the provider) can communicate correctly. This allows for independent development and deployment with confidence, as it verifies the "contract" between services without requiring slow, full-scale integration tests for every change.

Tech Stack & Key Features 🛠️
Backend: Python & Flask

Containerization: Docker

Orchestration: Docker Compose

Testing Framework: PyTest

CI/CD: GitHub Actions

Key Concepts:

Microservices Architecture

REST APIs

End-to-End Testing

Consumer-Driven Contract Testing

How to Run the Project
Running the Full System
The entire multi-service application is managed by Docker Compose.

Clone the repository: git clone <repository-url>

Navigate to the project directory: cd qa-microservices-project

Ensure Docker Desktop is installed and running.

Build and start all services with a single command:

docker compose up --build

The Product Service will be available at http://localhost:5001.

The Order Service will be available at http://localhost:5002.

Running the Tests
The tests are designed to run against the live, containerized application.

First, start the application using docker compose up.

In a new terminal, navigate to the tests directory: cd tests

Create and activate a virtual environment.

Install test dependencies: pip install -r requirements.txt

Run API & E2E tests:

pytest test_api.py

Run Contract tests:

# Step 1: Generate the contract (does not require services to be running)
pytest test_contract.py

# Step 2: Verify the contract against the live Product Service
pact-verifier --provider-base-url=http://localhost:5001 --pact-url=./pacts/orderservice-productservice.json