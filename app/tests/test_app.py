import unittest
from app.main import app
import requests_mock

class TestAdminApp(unittest.TestCase):
    
    def setUp(self):
        # Configura o cliente de teste do Flask
        self.app = app.test_client()
        self.app.testing = True

    @requests_mock.Mocker()
    def test_get_orders_success(self, mock_request):
        # Simula uma resposta de sucesso do serviço de pedidos
        mock_request.get("http://order-app:5000/orders/", json=[{"id": 1, "item": "Burger"}], status_code=200)
        
        response = self.app.get('/get-orders')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [{"id": 1, "item": "Burger"}])

    @requests_mock.Mocker()
    def test_get_orders_failure(self, mock_request):
        # Simula um erro do serviço de pedidos
        mock_request.get("http://order-app:5000/orders/", status_code=500, text='Internal Server Error')
        
        response = self.app.get('/get-orders')
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)

    @requests_mock.Mocker()
    def test_get_orders_invalid_url(self, mock_request):
        # Simulando erro no endpoint
        mock_request.get('http://order-app:5000/orders/', status_code=404)
        
        response = self.app.get('/get-orders')
        
        # Verifica se o código de status retornado é 500
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)

if __name__ == '__main__':
    unittest.main()
