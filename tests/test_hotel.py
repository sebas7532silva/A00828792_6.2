import tempfile
import unittest
from pathlib import Path

from hotel import Hotel


class TestHotel(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.tmp.name)
        self.hotels_json = self.data_dir / "hotels.json"
        self.hotels_json.write_text("[]", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_create_hotel_generates_id(self):
        h = Hotel.create(self.hotels_json, "Hilton", "CDMX", 5)
        self.assertTrue(h.hotel_id.startswith("HOT-"))

    def test_reserve_and_cancel_room(self):
        h = Hotel.create(self.hotels_json, "Hilton", "CDMX", 2)

        updated = Hotel.reserve_room(self.hotels_json, h.hotel_id)
        self.assertEqual(updated.reserved_rooms, 1)

        updated2 = Hotel.cancel_room_reservation(self.hotels_json, h.hotel_id)
        self.assertEqual(updated2.reserved_rooms, 0)

    def test_corrupted_json_does_not_crash(self):
        self.hotels_json.write_text("{ bad json", encoding="utf-8")
        hotels = Hotel.list_all(self.hotels_json)
        self.assertEqual(hotels, [])
