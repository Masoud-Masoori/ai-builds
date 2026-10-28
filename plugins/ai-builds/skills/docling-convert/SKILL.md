---
name: docling-convert
description: Convert a PDF to Markdown and JSON on the user's own machine with the open source Docling tool. Asks before any install and checks the output for silent failures.
---

# Convert a PDF with Docling

Docling is an MIT licensed open source Python project (github.com/docling-project/docling). This skill walks through converting one PDF on the user's own computer. Explain each step in plain words before you do it.

Rules for this skill:

- Never ask for, read or store passwords, tokens or API keys. Nothing here needs them.
- Never install anything, create a folder or download anything without asking first and saying what and how big.
- Work only on the file the user names. Do not upload it anywhere.

## Steps

1. Ask which PDF to convert and where the output should go. Confirm it is the user's own document.
2. Check the Python version with `python --version` (or `python3 --version`). Docling needs Python 3.10 or higher. On an Intel Mac the install page says Python 3.12 or lower. If Python is too old, stop and tell the user; do not install Python for them without asking.
3. Ask permission to create a virtual environment in a folder the user picks, then install Docling into it. Say what to expect before asking: the maintainer's test run on Windows with CPU only took about 10 minutes to install, used about 1.5 GB for the virtual environment, and the first conversion downloaded about 530 MB of models, so plan for about 2 GB of free disk. Offer two versions: `docling==2.142.1` (the version that was tested) or the newest release (`pip install docling`). Let the user choose.
4. Run the conversion: `docling invoice.pdf --to md --to json --output out` (replace `invoice.pdf` with the real file name). The first run is slow because of the model download. Say so while it runs.
5. Check the result. Do not trust exit code zero. Open the Markdown file in `out` and look for table rows (lines starting with `|`). If there are fewer than three such lines (a header, a separator and at least one data row) for a document that should contain a table, say clearly: the output is EMPTY and must not be trusted. In the maintainer's test, a blurry, tilted low resolution scan (55 dpi) came back with no text and no table rows and exit code zero, while a clean PDF and a 110 dpi scan converted exactly.
6. Report what was produced and where, what was checked, and what was not checked. Remind the user that adding up the numbers and comparing them to the stated total is the safest check for invoices (see the invoice-rule-check skill).

If the user wants the reasoning, the full page with sources is in the resources folder of the repository this plugin came from (resources/docling).
