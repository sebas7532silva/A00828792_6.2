import tempfile
import unittest
from pathlib import Path

from customer import Customer


class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.tmp.name)
        self.customers_json = self.data_dir / "customers.json"
        self.customers_json.write_text("[]", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_create_customer_generates_id(self):
        c = Customer.create(self.customers_json, "Alice", "alice@test.com")
        self.assertTrue(c.customer_id.startswith("CUST-"))

    def test_get_customer(self):
        c = Customer.create(self.customers_json, "Alice", "alice@test.com")
        loaded = Customer.get(self.customers_json, c.customer_id)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.customer_id, c.customer_id)

    def test_update_customer(self):
        c = Customer.create(self.customers_json, "Alice", "alice@test.com")
        updated = Customer.update(self.customers_json, c.customer_id, "Alice2", "alice@test.com")
        self.assertEqual(updated.name, "Alice2")

    def test_delete_customer(self):
        c = Customer.create(self.customers_json, "Alice", "alice@test.com")
        Customer.delete(self.customers_json, c.customer_id)
        self.assertIsNone(Customer.get(self.customers_json, c.customer_id))

    def test_corrupted_json_does_not_crash(self):
        self.customers_json.write_text("{ bad json", encoding="utf-8")
        customers = Customer.list_all(self.customers_json)
        self.assertEqual(customers, [])
