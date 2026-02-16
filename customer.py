"""
customer.py

Implements:
- Customer class
- JSON persistence (create, delete, display, modify)
- Auto-ID generation: CUST-0001, CUST-0002

Req 5: If JSON file is corrupted/invalid, print error and continue.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class Customer:
    """Represents a customer."""

    customer_id: str
    name: str
    email: str

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
        """Generate next customer ID."""
        max_num = 0
        for item in existing:
            cid = str(item.get("customer_id", ""))
            if cid.startswith("CUST-"):
                try:
                    num = int(cid.split("-")[1])
                    max_num = max(max_num, num)
                except (IndexError, ValueError):
                    continue
        return f"CUST-{max_num + 1:04d}"

    @staticmethod
    def create(json_path: Path, name: str, email: str) -> Customer:
        """Create a customer and persist it."""
        if not name.strip():
            raise ValueError("name cannot be empty")
        if not email.strip() or "@" not in email:
            raise ValueError("email is invalid")

        data = Customer._load_raw(json_path)
        customer_id = Customer._next_id(data)

        customer = Customer(customer_id=customer_id, name=name.strip(), email=email)
        data.append(
            {"customer_id": customer.customer_id, "name": customer.name, "email": customer.email}
        )
        Customer._save_raw(json_path, data)
        return customer

    @staticmethod
    def delete(json_path: Path, customer_id: str) -> None:
        """Delete a customer by ID."""
        data = Customer._load_raw(json_path)
        new_data = [x for x in data if str(x.get("customer_id")) != customer_id]
        if len(new_data) == len(data):
            raise ValueError("customer not found")
        Customer._save_raw(json_path, new_data)

    @staticmethod
    def get(json_path: Path, customer_id: str) -> Optional[Customer]:
        """Get a customer by ID."""
        for item in Customer._load_raw(json_path):
            if str(item.get("customer_id")) == customer_id:
                try:
                    return Customer(
                        customer_id=str(item["customer_id"]),
                        name=str(item["name"]),
                        email=str(item["email"]),
                    )
                except (KeyError, TypeError):
                    print(
                        "[ERROR] Invalid customer record in file. "
                        "Skipping corrupted record."
                    )
                    return None
        return None

    @staticmethod
    def list_all(json_path: Path) -> List[Customer]:
        """List all customers."""
        result: List[Customer] = []
        for item in Customer._load_raw(json_path):
            try:
                result.append(
                    Customer(
                        customer_id=str(item["customer_id"]),
                        name=str(item["name"]),
                        email=str(item["email"]),
                    )
                )
            except (KeyError, TypeError):
                print(
                    "[ERROR] Invalid customer record in file. "
                    "Skipping corrupted record."
                )
        return result

    @staticmethod
    def update(json_path: Path, customer_id: str, name: str, email: str) -> Customer:
        """Modify customer info."""
        if not name.strip():
            raise ValueError("name cannot be empty")
        if not email.strip() or "@" not in email:
            raise ValueError("email is invalid")

        data = Customer._load_raw(json_path)
        updated: Optional[Customer] = None

        for idx, item in enumerate(data):
            if str(item.get("customer_id")) == customer_id:
                updated = Customer(customer_id=customer_id, name=name.strip(), email=email)
                data[idx] = {
                    "customer_id": updated.customer_id,
                    "name": updated.name,
                    "email": updated.email,
                }
                break

        if updated is None:
            raise ValueError("customer not found")

        Customer._save_raw(json_path, data)
        return updated
