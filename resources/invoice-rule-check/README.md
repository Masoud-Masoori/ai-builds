# Invoice rule check: use a rule, not AI

For the video: "Use a rule, not AI".

## What it is

A short Python script that adds up the line items on an invoice and compares the result to the order total. It prints `PASS` or `MISMATCH` and the difference.

The idea from the video: where a rule works, use the rule. Adding up lines and comparing them to a total is a pattern, so no AI is needed for that check. Where there is no pattern (for example a free text email from a customer), the rule stops and flags it, and that one goes to a model or a person. A model can be wrong, so a person checks the result. AI can still help you write the rule, as in the prompt below.

Files in this folder:

- `invoice_check.py`: the rule. Python standard library only, nothing to install.
- `sample_invoice.csv`: a fictional sample. Two lines, 54.00 and 29.00, and an order total of 83.00. It is sample data, not a client.
- `test_invoice_check.py`: tests (a match, a mismatch, rounding to cents, an empty file and other bad input).

What the rule does: it reads amounts with Decimal instead of floats (so 0.10 plus 0.20 is exactly 0.30), rounds every amount to cents (half up), sums the invoice lines and compares the sum to the order total.

What it does not do: it proves the lines add up to the total. It does not prove the invoice is correct, the prices are right or the goods arrived.

## How to use it

You need Python 3 and nothing else. From this folder:

```
python invoice_check.py sample_invoice.csv
```

Expected output for the sample:

```
PASS: lines add up to 83.00, order total 83.00
```

Exit code 0 means PASS, 1 means MISMATCH (the output shows the difference, lines minus order total), 2 means the file could not be checked (empty, missing columns, a value that is not a number, no order total).

CSV format, with a header row:

```
kind,description,amount
invoice_line,Sample item A (fictional),54.00
invoice_line,Sample item B (fictional),29.00
order_total,Sample order (fictional),83.00
```

Use `invoice_line` for every line and exactly one `order_total` row. Amounts are plain numbers: no currency symbols and no thousands separators.

To run the tests (needs pytest): `python -m pytest -q`.

### Paste this into Claude

Copy everything in the box below into Claude. It will adapt the rule to your own invoice export. Use a copy of your file, or a few redacted rows.

```text
I want a small rule that checks whether the line items of my invoices add up to the order total. Here is a reference script and test idea: it uses only the Python standard library, reads amounts with decimal.Decimal (never float), rounds every amount to cents with ROUND_HALF_UP, sums the invoice lines, compares the sum to the order total, prints PASS or MISMATCH with the difference, and exits 0 for PASS, 1 for MISMATCH and 2 for bad input (empty file, missing column, a value that is not a number).

My invoice export is a file I will show you (a CSV, or a few redacted rows). Please:
1. Ask me which column holds each line amount and where the order total is.
2. Explain each step in plain words before you do it.
3. Ask before creating any file, and tell me where it will go.
4. Write the script and tests first: a matching invoice, a mismatching invoice, a rounding case and an empty file. Run them and show me the real output.
5. Tell me what the rule proves and what it does not prove.

Never ask me for passwords, tokens or API keys. Do not change my original file. Do not install anything without asking me first.
```

## Sources

- No external sources. The code and the sample data are original and fictional.
- The idea (use a rule where you can, use AI where you must) is from the video "Use a rule, not AI" by Masoud Masoori. Its sample invoice (54.00 plus 29.00 equals 83.00) is sample data, not a client.
