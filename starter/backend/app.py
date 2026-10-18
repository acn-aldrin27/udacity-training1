from flask import Flask, request, jsonify, send_from_directory
from backend.order_tracker import OrderTracker
from backend.in_memory_storage import InMemoryStorage

app = Flask(__name__, static_folder='../frontend')
in_memory_storage = InMemoryStorage()
order_tracker = OrderTracker(in_memory_storage)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/api/orders', methods=['POST'])
def add_order_api():
    data = request.get_json()

    try:
        order_data = {
            "order_id": data.get("order_id"),
            "item_name": data.get("item_name"),
            "quantity": data.get("quantity"),
            "customer_id": data.get("customer_id"),
        }

        if data.get("status"):
            order_data["status"] = data.get("status")

        response = order_tracker.add_order(**order_data)

        return jsonify(response), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@app.route('/api/orders/<string:order_id>', methods=['GET'])
def get_order_api(order_id):
    try:
        find_by_id = order_tracker.get_order_by_id(order_id)
        return jsonify(find_by_id), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@app.route('/api/orders/<string:order_id>/status', methods=['PUT'])
def update_order_status_api(order_id):
    data = request.get_json()

    try:
        updated_ordr = order_tracker.update_order_status(order_id, data.get("new_status"))
        return jsonify(updated_ordr), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@app.route('/api/orders', methods=['GET'])
def list_orders_api():

    status = request.args.get('status')

    if status is None:
        order_list = list(order_tracker.list_all_orders().values())
        return jsonify(order_list), 200

    order_list_by_status = list(order_tracker.list_orders_by_status(status))
    
    return jsonify(order_list_by_status), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
