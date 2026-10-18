import pytest
from unittest.mock import Mock, patch
from ..order_tracker import OrderTracker

# --- Fixtures for Unit Tests ---

@pytest.fixture
def mock_storage():
    """
    Provides a mock storage object for tests.
    This mock will be configured to simulate various storage behaviors.
    """
    mock = Mock()
    # By default, mock get_order to return None (no order found)
    mock.get_order.return_value = None
    # By default, mock get_all_orders to return an empty dict
    mock.get_all_orders.return_value = {}

    return mock

@pytest.fixture
def order_tracker(mock_storage):
    """
    Provides an OrderTracker instance initialized with the mock_storage.
    """
    return OrderTracker(mock_storage)

def test_add_order_successfully(order_tracker, mock_storage):
    """Tests adding a new order with default 'pending' status."""
    expected_order = {
        "order_id": "ORD-001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUS-001",
        "status": "pending"
    }


    result = order_tracker.add_order(
        expected_order['order_id'],
        expected_order['item_name'],
        expected_order['quantity'],
        expected_order['customer_id']
    )

    # We expect save_order to be called once
    mock_storage.save_order.assert_called_once()

    mock_storage.save_order.assert_called_once_with(expected_order['order_id'], expected_order)

    assert result == expected_order

def test_add_order_raises_error_if_exists(order_tracker, mock_storage):
    """Tests that adding an order with a duplicate ID raises a ValueError."""
    # Simulate that the storage finds an existing order
    mock_storage.get_order.return_value = [{"order_id": "ORD_EXISTING"}]

    with pytest.raises(ValueError, match="Order with ID 'ORD_EXISTING' already exists."):
        order_tracker.add_order("ORD_EXISTING", "New Item", 1, "CUST001")

def test_get_order_by_id_successfully(order_tracker, mock_storage):
    
    mock_storage.get_order.return_value = {
        "ORD-001": {
            "order_id": "ORD-001",
            "item_name": "Laptop",
            "quantity": 1,
            "customer_id": "CUS-001",
            "status": "pending"
        },
    }

    order_id = "ORD-001"

    result = order_tracker.get_order_by_id(order_id)

    mock_storage.get_order.assert_called_once()

    assert order_id in result

def test_get_order_by_id_raises_error_if_not_exists(order_tracker, mock_storage):
    """Tests that getting an order with a non-existing ID raises a ValueError."""
    # Simulate that the storage finds an existing order
    mock_storage.get_order.return_value = {
        "ORD-001": {
            "order_id": "ORD-001",
            "item_name": "Laptop",
            "quantity": 1,
            "customer_id": "CUS-001",
            "status": "pending"
        }
    }

    order_id = 'ORD-002'

    with pytest.raises(ValueError, match=f"Order with ID '{order_id}' does not exists."):
        order_tracker.get_order_by_id(order_id)

def test_update_order_status_successfully(order_tracker, mock_storage):
    
    mock_storage.get_order.return_value = {
        "ORD-001": {
            "order_id": "ORD-001",
            "item_name": "Laptop",
            "quantity": 1,
            "customer_id": "CUS-001",
            "status": "pending"
        }
    }

    result = order_tracker.update_order_status("ORD-001", "shipped")

    mock_storage.save_order.assert_called_once()

    print("STATUS_SUCCESS: ", result)

    assert result["status"] == "shipped"

def test_update_order_status_raises_error_if_not_exists(order_tracker, mock_storage):
    """Tests that getting an order with a non-existing ID raises a ValueError."""
    # Simulate that the storage finds an existing order
    mock_storage.get_order.return_value = {}

    order_id = 'ORD-002'

    with pytest.raises(ValueError, match=f"Order with ID '{order_id}' does not exists."):
        order_tracker.update_order_status(order_id, "shipped")

def test_update_order_status_raises_error_if_invalid_status(order_tracker, mock_storage):
    """Tests that getting an order with a non-existing status raises a ValueError."""
    # Simulate that the storage finds an existing order
    mock_storage.get_order.return_value = {
        "ORD-001": {
            "order_id": "ORD-001",
            "item_name": "Laptop",
            "quantity": 1,
            "customer_id": "CUS-001",
            "status": "pending"
        }
    }

    order_status = "in-progress"

    with pytest.raises(ValueError, match=f"Status '{order_status}' is invalid."):
        order_tracker.update_order_status("ORD-001", order_status)

def test_get_order_by_id_raises_error_if_not_exists(order_tracker, mock_storage):
    """Tests that getting an order with a non-existing ID raises a ValueError."""
    # Simulate that the storage finds an existing order
    mock_storage.get_order.return_value = {}

    order_id = 'ORD-002'

    with pytest.raises(ValueError, match=f"Order with ID '{order_id}' does not exists."):
        order_tracker.get_order_by_id(order_id)

def test_list_all_orders_successfully(order_tracker, mock_storage):
    
    mock_storage.get_all_orders.return_value = {
        "ORD-001": {
            "order_id": "ORD-001",
            "item_name": "Laptop",
            "quantity": 1,
            "customer_id": "CUS-001",
            "status": "pending"
        },
        "ORD-002": {
            "order_id": "ORD-002",
            "item_name": "Desktop",
            "quantity": 2,
            "customer_id": "CUS-002",
            "status": "invalid"
        }
    }

    result = order_tracker.list_all_orders()

    mock_storage.get_all_orders.assert_called_once()

    assert len(result) == 2

def test_list_all_orders_by_status_successfully(order_tracker, mock_storage):
    mock_storage.get_all_orders.return_value = {
        "ORD-001": {
            "order_id": "ORD-001",
            "item_name": "Laptop",
            "quantity": 1,
            "customer_id": "CUS-001",
            "status": "pending"
        },
        "ORD-002": {
            "order_id": "ORD-002",
            "item_name": "Desktop",
            "quantity": 2,
            "customer_id": "CUS-002",
            "status": "invalid"
        },
        "ORD-003": {
            "order_id": "ORD-003",
            "item_name": "Mouse",
            "quantity": 2,
            "customer_id": "CUS-003",
            "status": "invalid"
        }
    }    

    result = order_tracker.list_orders_by_status("invalid")
    mock_storage.get_all_orders.assert_called_once()

    assert len(result) == 2