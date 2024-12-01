from flask import Flask, jsonify
import requests

app = Flask(__name__)

ORDER_SERVICE_URL = "http://order-app:5000/orders/"

@app.route('/get-orders', methods=['GET'])
def get_orders():
    try:
        response = requests.get(ORDER_SERVICE_URL)
        response.raise_for_status()
        orders = response.json()
        return jsonify(orders)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)  # Escolher porta diferente
