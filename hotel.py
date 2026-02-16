"""
hotel.py

Implements:
- Hotel class
- JSON persistence (create, delete, display, modify)
- Reserve a room
- Cancel a reservation (room)
- Auto-ID generation: HOT-0001, HOT-0002, ...

Req 5: If JSON file is corrupted/invalid, print error and continue.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class Hotel:
    """Represents a hotel."""

    hotel_id: str
    name: str
    location: str
    total_rooms: int
    reserved_rooms: int = 0

    @property
    def available_rooms(self) -> int:
        """Return available rooms."""
        return self.total_rooms - self.reserved_rooms

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
                    f"[ERROR] Invalid structure in {json_path}: expected list. "
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
        """Generate next hotel ID."""
        max_num = 0
        for item in existing:
            hid = str(item.get("hotel_id", ""))
            if hid.startswith("HOT-"):
                try:
                    num = int(hid.split("-")[1])
                    max_num = max(max_num, num)
                except (IndexError, ValueError):
                    continue
        return f"HOT-{max_num + 1:04d}"

    @staticmethod
    def create(json_path: Path, name: str, location: str, total_rooms: int) -> Hotel:
        """Create a hotel and persist it."""
        if not name.strip():
            raise ValueError("name cannot be empty")
        if not location.strip():
            raise ValueError("location cannot be empty")
        if total_rooms <= 0:
            raise ValueError("total_rooms must be > 0")

        data = Hotel._load_raw(json_path)
        hotel_id = Hotel._next_id(data)

        hotel = Hotel(
            hotel_id=hotel_id,
            name=name.strip(),
            location=location.strip(),
            total_rooms=int(total_rooms),
            reserved_rooms=0,
        )

        data.append(
            {
                "hotel_id": hotel.hotel_id,
                "name": hotel.name,
                "location": hotel.location,
                "total_rooms": hotel.total_rooms,
                "reserved_rooms": hotel.reserved_rooms,
            }
        )
        Hotel._save_raw(json_path, data)
        return hotel

    @staticmethod
    def delete(json_path: Path, hotel_id: str) -> None:
        """Delete a hotel by ID."""
        data = Hotel._load_raw(json_path)
        new_data = [x for x in data if str(x.get("hotel_id")) != hotel_id]
        if len(new_data) == len(data):
            raise ValueError("hotel not found")
        Hotel._save_raw(json_path, new_data)

    @staticmethod
    def get(json_path: Path, hotel_id: str) -> Optional[Hotel]:
        """Get a hotel by ID."""
        for item in Hotel._load_raw(json_path):
            if str(item.get("hotel_id")) == hotel_id:
                try:
                    return Hotel(
                        hotel_id=str(item["hotel_id"]),
                        name=str(item["name"]),
                        location=str(item["location"]),
                        total_rooms=int(item["total_rooms"]),
                        reserved_rooms=int(item.get("reserved_rooms", 0)),
                    )
                except (KeyError, TypeError, ValueError):
                    print("[ERROR] Invalid hotel record in file. Skipping corrupted record.")
                    return None
        return None

    @staticmethod
    def list_all(json_path: Path) -> List[Hotel]:
        """List all hotels."""
        result: List[Hotel] = []
        for item in Hotel._load_raw(json_path):
            try:
                result.append(
                    Hotel(
                        hotel_id=str(item["hotel_id"]),
                        name=str(item["name"]),
                        location=str(item["location"]),
                        total_rooms=int(item["total_rooms"]),
                        reserved_rooms=int(item.get("reserved_rooms", 0)),
                    )
                )
            except (KeyError, TypeError, ValueError):
                print("[ERROR] Invalid hotel record in file. Skipping corrupted record.")
        return result

    @staticmethod
    def update(
        json_path: Path,
        hotel_id: str,
        name: str,
        location: str,
        total_rooms: int,
    ) -> Hotel:
        """Modify hotel info."""
        if not name.strip():
            raise ValueError("name cannot be empty")
        if not location.strip():
            raise ValueError("location cannot be empty")
        if total_rooms <= 0:
            raise ValueError("total_rooms must be > 0")

        data = Hotel._load_raw(json_path)
        updated: Optional[Hotel] = None

        for idx, item in enumerate(data):
            if str(item.get("hotel_id")) == hotel_id:
                reserved_rooms = int(item.get("reserved_rooms", 0))
                if reserved_rooms > total_rooms:
                    raise ValueError("total_rooms cannot be less than reserved_rooms")

                updated = Hotel(
                    hotel_id=hotel_id,
                    name=name.strip(),
                    location=location.strip(),
                    total_rooms=int(total_rooms),
                    reserved_rooms=reserved_rooms,
                )

                data[idx] = {
                    "hotel_id": updated.hotel_id,
                    "name": updated.name,
                    "location": updated.location,
                    "total_rooms": updated.total_rooms,
                    "reserved_rooms": updated.reserved_rooms,
                }
                break

        if updated is None:
            raise ValueError("hotel not found")

        Hotel._save_raw(json_path, data)
        return updated

    @staticmethod
    def reserve_room(json_path: Path, hotel_id: str) -> Hotel:
        """Reserve one room in a hotel."""
        data = Hotel._load_raw(json_path)

        for idx, item in enumerate(data):
            if str(item.get("hotel_id")) == hotel_id:
                total_rooms = int(item["total_rooms"])
                reserved_rooms = int(item.get("reserved_rooms", 0))

                if reserved_rooms >= total_rooms:
                    raise ValueError("no rooms available")

                reserved_rooms += 1
                item["reserved_rooms"] = reserved_rooms
                data[idx] = item

                Hotel._save_raw(json_path, data)
                return Hotel.get(json_path, hotel_id)

        raise ValueError("hotel not found")

    @staticmethod
    def cancel_room_reservation(json_path: Path, hotel_id: str) -> Hotel:
        """Cancel one reserved room in a hotel."""
        data = Hotel._load_raw(json_path)

        for idx, item in enumerate(data):
            if str(item.get("hotel_id")) == hotel_id:
                reserved_rooms = int(item.get("reserved_rooms", 0))
                if reserved_rooms <= 0:
                    raise ValueError("no reservations to cancel")

                reserved_rooms -= 1
                item["reserved_rooms"] = reserved_rooms
                data[idx] = item

                Hotel._save_raw(json_path, data)
                return Hotel.get(json_path, hotel_id)

        raise ValueError("hotel not found")
