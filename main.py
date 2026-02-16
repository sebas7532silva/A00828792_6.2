"""
main.py

Simple console program for evidence:
- Create Customer
- Create Hotel
- Create Reservation
- Cancel Reservation
- Display information

Uses JSON files in ./data
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict

from customer import Customer
from hotel import Hotel
from reservation import Reservation


DATA_DIR = Path("data")
CUSTOMERS_JSON = DATA_DIR / "customers.json"
HOTELS_JSON = DATA_DIR / "hotels.json"
RESERVATIONS_JSON = DATA_DIR / "reservations.json"


def _ensure_files() -> None:
    """Create empty JSON files if missing."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for path in (CUSTOMERS_JSON, HOTELS_JSON, RESERVATIONS_JSON):
        if not path.exists():
            path.write_text("[]", encoding="utf-8")


def _print_hotels() -> None:
    hotels = Hotel.list_all(HOTELS_JSON)
    if not hotels:
        print("No hotels found.")
        return

    for hotel in hotels:
        print(
            f"{hotel.hotel_id} | {hotel.name} | {hotel.location} | "
            f"{hotel.available_rooms}/{hotel.total_rooms} available"
        )


def _print_customers() -> None:
    customers = Customer.list_all(CUSTOMERS_JSON)
    if not customers:
        print("No customers found.")
        return

    for customer in customers:
        print(f"{customer.customer_id} | {customer.name} | {customer.email}")


def _print_reservations() -> None:
    reservations = Reservation.list_all(RESERVATIONS_JSON)
    if not reservations:
        print("No reservations found.")
        return

    for reservation in reservations:
        print(
            f"{reservation.reservation_id} | customer={reservation.customer_id} | "
            f"hotel={reservation.hotel_id} | {reservation.status} | "
            f"{reservation.created_at}"
        )


def _create_customer() -> None:
    name = input("Name: ").strip()
    email = input("Email: ").strip()
    customer = Customer.create(CUSTOMERS_JSON, name, email)
    print("Created:", customer)


def _delete_customer() -> None:
    customer_id = input("Customer ID: ").strip()
    Customer.delete(CUSTOMERS_JSON, customer_id)
    print("Customer deleted.")


def _modify_customer() -> None:
    customer_id = input("Customer ID: ").strip()
    name = input("New name: ").strip()
    email = input("New email: ").strip()
    updated = Customer.update(CUSTOMERS_JSON, customer_id, name, email)
    print("Updated:", updated)


def _create_hotel() -> None:
    name = input("Hotel name: ").strip()
    location = input("Location: ").strip()
    total_rooms = int(input("Total rooms: ").strip())
    hotel = Hotel.create(HOTELS_JSON, name, location, total_rooms)
    print("Created:", hotel)


def _delete_hotel() -> None:
    hotel_id = input("Hotel ID: ").strip()
    Hotel.delete(HOTELS_JSON, hotel_id)
    print("Hotel deleted.")


def _modify_hotel() -> None:
    hotel_id = input("Hotel ID: ").strip()
    name = input("New name: ").strip()
    location = input("New location: ").strip()
    total_rooms = int(input("New total rooms: ").strip())
    updated = Hotel.update(HOTELS_JSON, hotel_id, name, location, total_rooms)
    print("Updated:", updated)


def _create_reservation() -> None:
    customer_id = input("Customer ID: ").strip()
    hotel_id = input("Hotel ID: ").strip()

    reservation = Reservation.create(
        RESERVATIONS_JSON,
        CUSTOMERS_JSON,
        HOTELS_JSON,
        customer_id,
        hotel_id,
    )
    print("Created:", reservation)


def _cancel_reservation() -> None:
    reservation_id = input("Reservation ID: ").strip()
    updated = Reservation.cancel(RESERVATIONS_JSON, HOTELS_JSON, reservation_id)
    print("Updated:", updated)


def _print_menu() -> None:
    print("\nReservation System")
    print("1) Create Customer")
    print("2) Delete Customer")
    print("3) Modify Customer")
    print("4) Display Customers")
    print("5) Create Hotel")
    print("6) Delete Hotel")
    print("7) Modify Hotel")
    print("8) Display Hotels")
    print("9) Create Reservation")
    print("10) Cancel Reservation")
    print("11) Display Reservations")
    print("12) Exit")


def main() -> None:
    """Run the CLI."""
    _ensure_files()

    actions: Dict[str, Callable[[], None]] = {
        "1": _create_customer,
        "2": _delete_customer,
        "3": _modify_customer,
        "4": _print_customers,
        "5": _create_hotel,
        "6": _delete_hotel,
        "7": _modify_hotel,
        "8": _print_hotels,
        "9": _create_reservation,
        "10": _cancel_reservation,
        "11": _print_reservations,
    }

    while True:
        _print_menu()
        option = input("Select option: ").strip()

        if option == "12":
            print("Bye.")
            break

        try:
            action = actions.get(option)
            if action is None:
                print("Invalid option.")
            else:
                action()
        except ValueError as exc:
            print("[ERROR]", exc)


if __name__ == "__main__":
    main()
