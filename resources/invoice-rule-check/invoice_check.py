"""Check that invoice lines add up to the order total. Standard library only.

CSV format (header required):
    kind,description,amount
    invoice_line,Item A,54.00
    invoice_line,Item B,29.00
    order_total,Order,83.00

Every amount is rounded to cents (half up) with Decimal before it is summed.
Exit codes: 0 PASS, 1 MISMATCH, 2 bad input.
"""
import csv
import sys
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path

CENT = Decimal("0.01")
REQUIRED = ("kind", "amount")


class InputError(Exception):
    """The file cannot be checked (empty, missing columns, bad amount)."""


@dataclass
class Result:
    lines_total: Decimal
    order_total: Decimal

    @property
    def difference(self):
        return self.lines_total - self.order_total

    @property
    def passed(self):
        return self.difference == Decimal("0.00")


def to_cents(text, row_number):
    try:
        value = Decimal(text.strip())
    except (InvalidOperation, AttributeError):
        raise InputError(f"row {row_number}: amount {text!r} is not a number")
    if not value.is_finite():
        raise InputError(f"row {row_number}: amount {text!r} is not a finite number")
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def read_rows(path):
    """Return the header and the rows. Any unreadable file becomes an InputError."""
    try:
        # utf-8-sig drops the byte order mark that Excel's "CSV UTF-8" adds.
        with open(path, newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            fieldnames = reader.fieldnames
            return fieldnames, list(reader)
    except UnicodeDecodeError:
        raise InputError("file is not valid UTF-8 text; save it as CSV UTF-8 and try again")
    except csv.Error as error:
        raise InputError(f"file is not a readable CSV: {error}")


def check_file(path):
    fieldnames, rows = read_rows(path)
    if not fieldnames:
        raise InputError("file is empty")
    missing = [c for c in REQUIRED if c not in fieldnames]
    if missing:
        raise InputError("missing column(s): " + ", ".join(missing))
    lines = []
    totals = []
    for number, row in enumerate(rows, start=2):
        kind = (row.get("kind") or "").strip()
        amount = row.get("amount") or ""
        if kind == "invoice_line":
            lines.append(to_cents(amount, number))
        elif kind == "order_total":
            totals.append(to_cents(amount, number))
        elif kind:
            raise InputError(f"row {number}: unknown kind {kind!r}")
        elif amount.strip():
            raise InputError(f"row {number}: has an amount but no kind (use invoice_line or order_total)")
    if not lines:
        raise InputError("no invoice_line rows found")
    if len(totals) != 1:
        raise InputError(f"expected exactly one order_total row, found {len(totals)}")
    return Result(lines_total=sum(lines, Decimal("0.00")), order_total=totals[0])


def format_result(result):
    if result.passed:
        return f"PASS: lines add up to {result.lines_total}, order total {result.order_total}"
    return (
        f"MISMATCH: lines add up to {result.lines_total}, order total {result.order_total}, "
        f"difference {result.difference}"
    )


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: python invoice_check.py <invoice.csv>", file=sys.stderr)
        return 2
    try:
        result = check_file(Path(args[0]))
    except (InputError, OSError) as error:
        print(f"INPUT ERROR: {error}", file=sys.stderr)
        return 2
    print(format_result(result))
    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
