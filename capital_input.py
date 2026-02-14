from __future__ import annotations

from typing import Final


def parse_initial_cash(raw: str) -> float:
    """
    Parse a raw string into a positive float representing initial capital.

    Design:
    - Keep this function pure (no input/print) so it can be unit-tested easily.
    - Accept human-friendly formats like "100,000" by stripping whitespace
      and removing commas before conversion.
    - Enforce that the resulting value must be strictly greater than zero,
      which is suitable for most investment onboarding flows.
    """
    if raw is None:
        raise ValueError("Initial capital input must not be None.")

    # Normalize common formatting: strip spaces and thousands separators.
    normalized = raw.strip().replace(",", "")

    if not normalized:
        raise ValueError("Initial capital must not be empty.")

    try:
        value = float(normalized)
    except ValueError as exc:
        raise ValueError("Initial capital must be a valid number.") from exc

    if value <= 0:
        raise ValueError("Initial capital must be greater than zero.")

    return value


def run_capital_input_cli() -> float:
    """
    CLI wrapper for collecting initial investment capital from the user.

    Design:
    - Responsibility of this function is limited to:
        * prompting the user via input()
        * delegating parsing/validation to parse_initial_cash()
        * looping until a valid value is obtained
      This keeps main.py free from validation details and keeps
      parse_initial_cash() reusable and testable in isolation.
    """
    while True:
        raw = input("กรุณากรอกเงินลงทุนเริ่มต้น: ")
        try:
            return parse_initial_cash(raw)
        except ValueError as exc:
            print(f"ข้อมูลไม่ถูกต้อง: {exc}")
            print("กรุณาลองใหม่อีกครั้ง.\n")

