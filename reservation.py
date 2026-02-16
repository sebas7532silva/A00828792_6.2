"""
reservation.py

Implements:
- Reservation class
- JSON persistence
- Create reservation (customer + hotel)
- Cancel reservation

Auto-ID generation: RES-0001, RES-0002, ...

Req 5: If JSON file is corrupted/invalid, print error and continue.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from customer import Customer
from hotel import Hotel


@dataclass(frozen=True)
class Reservation:
    """Represents a reservation."""

    reservation_id: str
    customer_id: str
    hotel_id: str
    created_at: str
    status: str = "ACTIVE"  # ACTIVE | CANCELED

    @staticmethod
    def _load_raw(json_path: Path) -> List[Dict[str, Any]]:
        """Load list from JSON. If invalid, print error and return empty."""
        if not json_path.exists():
            return []

        try:
            text = json_path.read_text(encoding="utf-8").strip()
            if not text:
                return []

            data = json.loads(text)
            if not isinstance(data, list):
                print(
                    f"[ERROR] Invalid structure in {json_path}: expected list."
                    "Continuing with empty list."
                )
                return []

            valid: List[Dict[str, Any]] = []
            for item in data:
                if isinstance(item, dict):
                    valid.append(item)
                else:
                    print(
                        f"[ERROR] Invalid item in {json_path}: expected dict. "
                        "Skipping item."
                    )
            return valid

        except json.JSONDecodeError as exc:
            print(
                f"[ERROR] Corrupted JSON in {json_path}: {exc}. "
                "Continuing with empty list."
            )
            return []

    @staticmethod
    def _save_raw(json_path: Path, data: List[Dict[str, Any]]) -> None:
        """Save list to JSON."""
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    @staticmethod
    def _next_id(existing: List[Dict[str, Any]]) -> str:
        """Generate next reservation ID."""
        max_num = 0
        for item in existing:
            rid = str(item.get("reservation_id", ""))
            if rid.startswith("RES-"):
                try:
                    num = int(rid.split("-")[1])
                    max_num = max(max_num, num)
                except (IndexError, ValueError):
                    continue
        return f"RES-{max_num + 1:04d}"

    @staticmethod
    def get(json_path: Path, reservation_id: str) -> Optional[Reservation]:
        """Get a reservation by ID."""
        for item in Reservation._load_raw(json_path):
            if str(item.get("reservation_id")) == reservation_id:
                try:
                    return Reservation(
                        reservation_id=str(item["reservation_id"]),
                        customer_id=str(item["customer_id"]),
                        hotel_id=str(item["hotel_id"]),
                        created_at=str(item["created_at"]),
                        status=str(item.get("status", "ACTIVE")),
                    )
                except (KeyError, TypeError):
                    print(
                        "[ERROR] Invalid reservation record in file. "
                        "Skipping corrupted record."
                    )
                    return None
        return None

    @staticmethod
    def list_all(json_path: Path) -> List[Reservation]:
        """List all reservations."""
        result: List[Reservation] = []
        for item in Reservation._load_raw(json_path):
            try:
                result.append(
                    Reservation(
                        reservation_id=str(item["reservation_id"]),
                        customer_id=str(item["customer_id"]),
                        hotel_id=str(item["hotel_id"]),
                        created_at=str(item["created_at"]),
                        status=str(item.get("status", "ACTIVE")),
                    )
                )
            except (KeyError, TypeError):
                print(
                    "[ERROR] Invalid reservation record in file. "
                    "Skipping corrupted record."
                )
        return result

    @staticmethod
    def create(
        reservations_json: Path,
        customers_json: Path,
        hotels_json: Path,
        customer_id: str,
        hotel_id: str,
    ) -> Reservation:
        """Create a reservation linking customer and hotel."""
        if Customer.get(customers_json, customer_id) is None:
            raise ValueError("customer not found")

        if Hotel.get(hotels_json, hotel_id) is None:
            raise ValueError("hotel not found")

        Hotel.reserve_room(hotels_json, hotel_id)

        data = Reservation._load_raw(reservations_json)
        reservation_id = Reservation._next_id(data)

        reservation = Reservation(
            reservation_id=reservation_id,
            customer_id=customer_id,
            hotel_id=hotel_id,
            created_at=datetime.utcnow().isoformat(timespec="seconds"),
            status="ACTIVE",
        )

        data.append(
            {
                "reservation_id": reservation.reservation_id,
                "customer_id": reservation.customer_id,
                "hotel_id": reservation.hotel_id,
                "created_at": reservation.created_at,
                "status": reservation.status,
            }
        )
        Reservation._save_raw(reservations_json, data)
        return reservation

    @staticmethod
    def cancel(
        reservations_json: Path,
        hotels_json: Path,
        reservation_id: str,
    ) -> Reservation:
        """Cancel a reservation."""
        data = Reservation._load_raw(reservations_json)
        updated: Optional[Reservation] = None

        for idx, item in enumerate(data):
            if str(item.get("reservation_id")) == reservation_id:
                status = str(item.get("status", "ACTIVE"))
                if status == "CANCELED":
                    return Reservation.get(reservations_json, reservation_id)

                hotel_id = str(item["hotel_id"])
                Hotel.cancel_room_reservation(hotels_json, hotel_id)

                item["status"] = "CANCELED"
                data[idx] = item

                updated = Reservation(
                    reservation_id=str(item["reservation_id"]),
                    customer_id=str(item["customer_id"]),
                    hotel_id=hotel_id,
                    created_at=str(item["created_at"]),
                    status="CANCELED",
                )
                break

        if updated is None:
            raise ValueError("reservation not found")

        Reservation._save_raw(reservations_json, data)
        return updated
