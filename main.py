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

    for path in [CUSTOMERS_JSON, HOTELS_JSON, RESERVATIONS_JSON]:
        if not path.exists():
            path.write_text("[]", encoding="utf-8")


def _print_hotels() -> None:
    hotels = Hotel.list_all(HOTELS_JSON)
    if not hotels:
        print("No hotels found.")
        return

    for h in hotels:
        print(
            f"{h.hotel_id} | {h.name} | {h.location} | "
            f"{h.available_rooms}/{h.total_rooms} available"
        )


def _print_customers() -> None:
    customers = Customer.list_all(CUSTOMERS_JSON)
    if not customers:
        print("No customers found.")
        return

    for c in customers:
        print(f"{c.customer_id} | {c.name} | {c.email}")


def _print_reservations() -> None:
    reservations = Reservation.list_all(RESERVATIONS_JSON)
    if not reservations:
        print("No reservations found.")
        return

    for r in reservations:
        print(
            f"{r.reservation_id} | customer={r.customer_id} | "
            f"hotel={r.hotel_id} | {r.status} | {r.created_at}"
        )


def main() -> None:
    """Run the CLI."""
    _ensure_files()

    while True:
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

        option = input("Select option: ").strip()

        try:
            if option == "1":
                name = input("Name: ").strip()
                email = input("Email: ").strip()
                customer = Customer.create(CUSTOMERS_JSON, name, email)
                print("Created:", customer)

            elif option == "2":
                customer_id = input("Customer ID: ").strip()
                Customer.delete(CUSTOMERS_JSON, customer_id)
                print("Customer deleted.")

            elif option == "3":
                customer_id = input("Customer ID: ").strip()
                name = input("New name: ").strip()
                email = input("New email: ").strip()
                updated = Customer.update(CUSTOMERS_JSON, customer_id, name, email)
                print("Updated:", updated)

            elif option == "4":
                _print_customers()

            elif option == "5":
                name = input("Hotel name: ").strip()
                location = input("Location: ").strip()
                total_rooms = int(input("Total rooms: ").strip())
                hotel = Hotel.create(HOTELS_JSON, name, location, total_rooms)
                print("Created:", hotel)

            elif option == "6":
                hotel_id = input("Hotel ID: ").strip()
                Hotel.delete(HOTELS_JSON, hotel_id)
                print("Hotel deleted.")

            elif option == "7":
                hotel_id = input("Hotel ID: ").strip()
                name = input("New name: ").strip()
                location = input("New location: ").strip()
                total_rooms = int(input("New total rooms: ").strip())
                updated = Hotel.update(HOTELS_JSON, hotel_id, name, location, total_rooms)
                print("Updated:", updated)

            elif option == "8":
                _print_hotels()

            elif option == "9":
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

            elif option == "10":
                reservation_id = input("Reservation ID: ").strip()
                updated = Reservation.cancel(
                    RESERVATIONS_JSON,
                    HOTELS_JSON,
                    reservation_id,
                )
                print("Updated:", updated)

            elif option == "11":
                _print_reservations()

            elif option == "12":
                print("Bye.")
                break

            else:
                print("Invalid option.")

        except ValueError as exc:
            print("[ERROR]", exc)


if __name__ == "__main__":
    main()
