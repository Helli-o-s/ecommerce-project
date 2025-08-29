import pytest
import requests
from pact import Consumer, Provider, Like

# Define the Pact mock server's host and port
PACT_MOCK_HOST = 'localhost'
PACT_MOCK_PORT = 1234

@pytest.fixture(scope="session")
def pact():
    """Set up the Pact Consumer and Provider."""
    pact = Consumer('OrderService').has_pact_with(
        Provider('ProductService'),
        host_name=PACT_MOCK_HOST,
        port=PACT_MOCK_PORT,
        pact_dir='./pacts'  # This is where the contract file will be saved
    )
    pact.start_service()
    yield pact
    pact.stop_service()

def test_get_product(pact):
    """
    Tests that the Order Service can successfully get a product
    from the Product Service.
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

    # 2. Run the actual consumer code against the Pact mock server
    with pact:
        # This is the function from our Order Service that calls the Product Service.
        # We pass it the URL of the Pact mock server.
        product_url = f"http://{PACT_MOCK_HOST}:{PACT_MOCK_PORT}/products/102"
        response = requests.get(product_url)
        
        # 3. Assert that the consumer code handled the response correctly
        assert response.status_code == 200
        assert response.json()['name'] == 'Mechanical Keyboard'