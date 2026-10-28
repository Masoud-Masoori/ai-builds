import subprocess
import sys
from decimal import Decimal
from pathlib import Path

import pytest

import invoice_check as ic

HERE = Path(__file__).resolve().parent


def write(tmp_path, text):
    p = tmp_path / "inv.csv"
    p.write_text(text, encoding="utf-8")
    return p


def test_match_passes(tmp_path):
    p = write(tmp_path, "kind,description,amount\ninvoice_line,A,54.00\ninvoice_line,B,29.00\norder_total,Order,83.00\n")
    r = ic.check_file(p)
    assert r.passed
    assert r.lines_total == Decimal("83.00")
    assert r.difference == Decimal("0.00")
    assert ic.format_result(r).startswith("PASS")


def test_mismatch_reports_difference(tmp_path):
    p = write(tmp_path, "kind,description,amount\ninvoice_line,A,54.00\ninvoice_line,B,29.00\norder_total,Order,85.50\n")
    r = ic.check_file(p)
    assert not r.passed
    assert r.difference == Decimal("-2.50")
    out = ic.format_result(r)
    assert out.startswith("MISMATCH")
    assert "-2.50" in out


def test_decimal_avoids_float_error(tmp_path):
    # 0.10 + 0.20 is 0.30000000000000004 in floats; Decimal gets it exact.
    p = write(tmp_path, "kind,description,amount\ninvoice_line,A,0.10\ninvoice_line,B,0.20\norder_total,Order,0.30\n")
    assert ic.check_file(p).passed


def test_rounds_to_cents_half_up(tmp_path):
    # 10.005 rounds to 10.01 (half up), so two lines make 20.02.
    p = write(tmp_path, "kind,description,amount\ninvoice_line,A,10.005\ninvoice_line,B,10.005\norder_total,Order,20.02\n")
    r = ic.check_file(p)
    assert r.lines_total == Decimal("20.02")
    assert r.passed


def test_empty_file_is_input_error(tmp_path):
    p = write(tmp_path, "")
    with pytest.raises(ic.InputError):
        ic.check_file(p)


def test_header_only_is_input_error(tmp_path):
    p = write(tmp_path, "kind,description,amount\n")
    with pytest.raises(ic.InputError):
        ic.check_file(p)


def test_missing_order_total_is_input_error(tmp_path):
    p = write(tmp_path, "kind,description,amount\ninvoice_line,A,1.00\n")
    with pytest.raises(ic.InputError):
        ic.check_file(p)


def test_no_lines_is_input_error(tmp_path):
    p = write(tmp_path, "kind,description,amount\norder_total,Order,1.00\n")
    with pytest.raises(ic.InputError):
        ic.check_file(p)


def test_bad_amount_is_input_error(tmp_path):
    p = write(tmp_path, "kind,description,amount\ninvoice_line,A,abc\norder_total,Order,1.00\n")
    with pytest.raises(ic.InputError):
        ic.check_file(p)


def test_sample_file_passes_via_cli():
    out = subprocess.run(
        [sys.executable, str(HERE / "invoice_check.py"), str(HERE / "sample_invoice.csv")],
        capture_output=True,
        text=True,
    )
    assert out.returncode == 0
    assert out.stdout.startswith("PASS")
    assert "83.00" in out.stdout


def test_cli_exit_codes(tmp_path):
    bad = write(tmp_path, "kind,description,amount\ninvoice_line,A,1.00\norder_total,Order,2.00\n")
    r = subprocess.run([sys.executable, str(HERE / "invoice_check.py"), str(bad)], capture_output=True, text=True)
    assert r.returncode == 1
    assert r.stdout.startswith("MISMATCH")
    empty = write(tmp_path, "")
    r = subprocess.run([sys.executable, str(HERE / "invoice_check.py"), str(empty)], capture_output=True, text=True)
    assert r.returncode == 2


HEADER = "kind,description,amount\n"


def run_cli(path):
    return subprocess.run([sys.executable, str(HERE / "invoice_check.py"), str(path)], capture_output=True, text=True)


def test_cp1252_file_is_input_error(tmp_path):
    # A spreadsheet "CSV" saved in the Windows code page: e-acute is the single byte 0xE9, not valid UTF-8.
    p = tmp_path / "inv.csv"
    p.write_bytes((HEADER + "invoice_line,Caf\u00e9,1.00\norder_total,Order,1.00\n").encode("cp1252"))
    with pytest.raises(ic.InputError, match="UTF-8"):
        ic.check_file(p)
    r = run_cli(p)
    assert r.returncode == 2
    assert "UTF-8" in r.stderr
    assert "Traceback" not in r.stderr


def test_utf8_bom_file_passes(tmp_path):
    # Excel's "CSV UTF-8" writes a byte order mark; it must not hide the first column name.
    p = tmp_path / "inv.csv"
    p.write_bytes(b"\xef\xbb\xbf" + (HEADER + "invoice_line,A,1.00\norder_total,Order,1.00\n").encode("utf-8"))
    assert ic.check_file(p).passed
    r = run_cli(p)
    assert r.returncode == 0
    assert r.stdout.startswith("PASS")


def test_blank_kind_with_amount_is_input_error(tmp_path):
    # A row that carries money but no kind must not be skipped silently.
    p = write(tmp_path, HEADER + "invoice_line,A,1.00\n,Forgotten line,5.00\norder_total,Order,1.00\n")
    with pytest.raises(ic.InputError, match="row 3"):
        ic.check_file(p)
    assert run_cli(p).returncode == 2


def test_blank_kind_without_amount_is_ignored(tmp_path):
    p = write(tmp_path, HEADER + "invoice_line,A,1.00\n,,\norder_total,Order,1.00\n")
    assert ic.check_file(p).passed


def test_malformed_csv_is_input_error(tmp_path):
    # A field longer than the csv module's limit raises csv.Error.
    p = write(tmp_path, HEADER + "invoice_line," + "x" * 200000 + ",1.00\norder_total,Order,1.00\n")
    with pytest.raises(ic.InputError, match="CSV"):
        ic.check_file(p)
    r = run_cli(p)
    assert r.returncode == 2
    assert "Traceback" not in r.stderr
