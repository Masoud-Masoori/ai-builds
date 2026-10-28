# Docling: turn an invoice PDF into data on your laptop

For the video: "This free GitHub repo turns an invoice PDF into a clean table".

## What it is

Docling is an open source Python project that converts documents such as PDFs into Markdown and JSON. Repository: https://github.com/docling-project/docling . It is MIT licensed (stated in the repository README).

What it is good for: on the maintainer's one test, it can replace paid parsing for many documents. A clean digital invoice PDF and a 110 dpi scan both came back exact (5 of 5 line items, subtotal, tax and total all matching). It runs on your own computer, so there is no per page fee. That is one test on one fictional English invoice, not a benchmark.

Version checked: the latest release on 2026-10-28 was v2.144.0 (published that day). The test below used v2.142.1. Releases move fast, so check the repository for the current version.

Not affiliated with the Docling project. Prepared by MAS-AI Technologies.

## How to use it

Requirements: Python 3.10 or higher. Works on macOS, Linux and Windows (x86_64 and arm64). On an Intel Mac the install page says to use Python 3.12 or lower.

What to expect (from the maintainer's run on Windows 11, Python 3.11.9, CPU only): installing took about 10 minutes (579 seconds), the virtual environment used about 1.5 GB, and the first conversion downloaded about 530 MB of models. Plan for about 2 GB of free disk. A warm conversion of the digital PDF took about 19 seconds; the 110 dpi scan took about 38 seconds.

Install (official command):

```
pip install docling
```

To get the version that was tested, use `pip install docling==2.142.1` instead. Use a virtual environment so it stays out of your other projects.

Convert a file from the command line:

```
docling invoice.pdf --to md --to json --output out
```

The official CLI example is `docling <url-or-path>`. The `--to` and `--output` options above come from the maintainer's own test run; check `docling --help` if they differ on your version.

Minimal official Python example (structure as on the quickstart page; if it differs from the live docs, trust the docs):

```python
from docling.document_converter import DocumentConverter

source = "invoice.pdf"  # file path or URL
converter = DocumentConverter()
result = converter.convert(source)
print(result.document.export_to_markdown())
```

Always check the output. Save this as `check.py` and run `python check.py out/invoice.md`:

```python
import pathlib
import sys

text = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
rows = [line for line in text.splitlines() if line.strip().startswith("|")]
if len(rows) < 3:  # header, separator, at least one data row
    sys.exit("EMPTY: no table in the output, do not trust this file")
print(f"OK: {len(rows)} table rows found")
```

Then add up the line items yourself and compare them to the total. A small script for exactly that is in [invoice-rule-check](../invoice-rule-check/README.md).

### Paste this into Claude

Copy everything in the box below and paste it into Claude (Claude Code, or any chat where Claude can run commands on your computer). Replace the file name.

```text
I want to convert one PDF to Markdown and JSON on my own computer with the open source tool Docling (https://github.com/docling-project/docling). The file is called invoice.pdf and it is my own document.

Please do this step by step and explain each step in plain words before you do it:
1. Check that Python 3.10 or higher is installed. If it is not, stop and tell me; do not install Python without asking me.
2. Tell me what the install needs (about 2 GB of free disk, roughly 10 minutes, and about 530 MB of models downloaded on the first conversion), then ask me before creating a virtual environment and running pip install docling. Offer me docling==2.142.1 (the version that was tested) or the newest release, and let me choose.
3. Run: docling invoice.pdf --to md --to json --output out
4. Do not trust exit code zero. Open out/invoice.md and look for table rows (lines starting with a pipe character). If there are fewer than three (a header, a separator and at least one data row), tell me the output is EMPTY and must not be trusted. A blurry, tilted low resolution scan can fail silently.
5. Tell me what was produced, what you checked, and what you did not check.

Never ask me for passwords, tokens or API keys. Do not upload my file anywhere. Ask before installing or downloading anything.
```

## Limits

- The maintainer's test: one fictional English invoice. A blurry, tilted scan at 55 dpi came back with no text and no table rows, with exit code zero and no error. That is a silent failure, which is why the check above matters.
- Not tested: multi page contracts, handwriting, non English documents, rotated tables, GPU.
- Test machine: Windows 11, Python 3.11.9, CPU only. Your times will differ.
- The test used version 2.142.1. Newer versions exist and were not re-tested.
- Check your own numbers: add up the lines and compare them to the total before you trust any converted invoice.

## Sources

- Docling repository and README (license, Python 3.10 or higher, `pip install docling`): https://github.com/docling-project/docling , retrieved 2026-10-28.
- Latest release v2.144.0: https://github.com/docling-project/docling/releases/latest and https://pypi.org/pypi/docling/2.144.0/json , retrieved 2026-10-28.
- Install page (platforms, Intel Mac note): https://docling-project.github.io/docling/getting_started/installation/ , retrieved 2026-10-28.
- Quickstart (Python example, CLI example): https://docling-project.github.io/docling/getting_started/quickstart/ , retrieved 2026-10-28.
- Install time, disk use, model download, timings, accuracy and the 55 dpi failure: the maintainer's own test run on 2026-10-28 with docling 2.142.1. There is no public link for it.
