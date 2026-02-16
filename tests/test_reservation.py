import tempfile
import unittest
from pathlib import Path

from customer import Customer
from hotel import Hotel
from reservation import Reservation


class TestReservation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.tmp.name)

        self.customers_json = self.data_dir / "customers.json"
        self.hotels_json = self.data_dir / "hotels.json"
        self.reservations_json = self.data_dir / "reservations.json"

        self.customers_json.write_text("[]", encoding="utf-8")
        self.hotels_json.write_text("[]", encoding="utf-8")
        self.reservations_json.write_text("[]", encoding="utf-8")

        self.customer = Customer.create(self.customers_json, "Alice", "alice@test.com")
        self.hotel = Hotel.create(self.hotels_json, "Hilton", "CDMX", 2)

    def tearDown(self):
        self.tmp.cleanup()

    def test_create_reservation_generates_id(self):
        r = Reservation.create(
            self.reservations_json,
            self.customers_json,
            self.hotels_json,
            self.customer.customer_id,
            self.hotel.hotel_id,
        )
        self.assertTrue(r.reservation_id.startswith("RES-"))

    def test_cancel_reservation(self):
        r = Reservation.create(
            self.reservations_json,
            self.customers_json,
            self.hotels_json,
            self.customer.customer_id,
            self.hotel.hotel_id,
        )

        updated = Reservation.cancel(self.reservations_json, self.hotels_json, r.reservation_id)
        self.assertEqual(updated.status, "CANCELED")

    def test_corrupted_reservations_json_does_not_crash(self):
        self.reservations_json.write_text("{ bad json", encoding="utf-8")
        reservations = Reservation.list_all(self.reservations_json)
        self.assertEqual(reservations, [])
