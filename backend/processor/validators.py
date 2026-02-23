# validators.py
from collections.abc import Sequence
from typing import Any, Mapping

from emval import EmailValidator

emval = EmailValidator(
    allow_smtputf8=False,
    allow_empty_local=True,
    allow_quoted_local=True,
    allow_domain_literal=True,
    deliverable_address=False,
    allowed_special_domains=["test", "invalid"],
)


def validate_id(value: str | None) -> int:
    if value is None:
        raise ValueError("Invalid id")
    try:
        id_ = int(value)
    except (TypeError, ValueError):
        raise ValueError("Invalid id")
    if id_ <= 0:
        raise ValueError("Id must be positive")

    return id_


def validate_name(value: str | None) -> str:
    if value is None:
        raise ValueError("Name is required")
    name = (value or "").strip()
    if not name:
        raise ValueError("Name is required")
    return name


def validate_email(value: str | None) -> str:
    if value is None:
        raise ValueError("Invalid email address")
    if not value or not isinstance(value, str):
        raise ValueError("Invalid email address")

    if not emval.validate_email(value):
        raise ValueError("Invalid email address")

    return value.strip()


def validate_amount(value: str | None) -> float:
    if value is None:
        raise ValueError("Missing amount")
    try:
        amount = float(value)
    except (TypeError, ValueError):
        raise ValueError("Invalid amount")

    if amount < 0:
        raise ValueError("Amount must be non-negative")

    return amount


class CSVRowValidator:
    @classmethod
    def validate_row(cls, row: Mapping[str, str]) -> dict[str, Any]:
        return {
            "id": validate_id(row.get("id")),
            "name": validate_name(row.get("name")),
            "email": validate_email(row.get("email")),
            "amount": validate_amount(row.get("amount")),
        }


class CSVHeaderValidator:
    EXPECTED_COLUMNS = {"id", "name", "email", "amount"}

    @classmethod
    def validate_header(cls, fieldnames: Sequence[str] | None) -> None:
        if not fieldnames:
            raise ValueError("Missing header")

        missing = cls.EXPECTED_COLUMNS - set(fieldnames)
        if missing:
            raise ValueError(f"Missing columns: {missing}")
