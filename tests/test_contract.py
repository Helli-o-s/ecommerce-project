# tests/test_contract.py

import pytest
import requests
from pact.matchers import Like
from pact import Consumer, Provider

# Define the Pact mock server's host and port
PACT_MOCK_HOST = 'localhost'
PACT_MOCK_PORT = 1234
PACT_DIR = './pacts'

@pytest.fixture(scope="session")
def pact():
    """
    Set up the Pact Consumer and Provider, start the mock service,
    and tear it down after the test session.
    """
    # Define the consumer and provider
    pact = Consumer('OrderService').has_pact_with(
        Provider('ProductService'),
        host_name=PACT_MOCK_HOST,
        port=PACT_MOCK_PORT,
        pact_dir=PACT_DIR
    )
    # Start the Pact mock server
    pact.start_service()
    yield pact
    # Stop the server after all tests in the session are complete
    pact.stop_service()


def test_get_product(pact):
    """
    Defines the contract for getting a product and then verifies that
    a request to the mock server returns the expected response.
    """
    # 1. Define the expected interaction (the "contract")
    expected = {
        'name': Like('Mechanical Keyboard'),
        'price': Like(79.99),
        'stock': Like(75)
    }
    (pact
     .given('a product with ID 102 exists')
     .upon_receiving('a request for a single product')
     .with_request(method='GET', path='/products/102')
     .will_respond_with(200, body=expected))

    # 2. The 'with pact:' block verifies the interaction and writes the contract file
    #    if the code inside runs without raising an exception.
    with pact:
        # 3. Make the actual request to the mock server
        response = requests.get(f"http://{PACT_MOCK_HOST}:{PACT_MOCK_PORT}/products/102")
        
        # 4. Assert that the response from the mock server is correct
        assert response.status_code == 200
        assert response.json()['name'] == 'Mechanical Keyboard'