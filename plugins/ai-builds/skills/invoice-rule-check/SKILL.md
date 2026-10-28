---
name: invoice-rule-check
description: Build a small rule that adds up invoice line items and compares them to the order total, using only the Python standard library. No AI needed for the check itself.
---

# Invoice rule check

A rule is better than a model wherever a pattern exists. Adding up invoice lines and comparing the result to the order total is such a case. Use this skill to write that rule for the user's own invoice export. Explain each step in plain words.

Rules for this skill:

- Never ask for, read or store passwords, tokens or API keys. Nothing here needs them.
- Ask before creating any file, and say where it goes.
- Work on a copy or a redacted sample first. Never change the user's original data.
- The script uses only the Python standard library, so there is nothing to install. If the user asks for a package, ask first.

## Steps

1. Ask for the invoice export (CSV is simplest) or a few fictional or redacted rows. Ask which column holds each line amount and where the order total lives.
2. Write a short Python script in a folder the user picks (ask first). It must:
   - read amounts with `decimal.Decimal`, never `float`, so 0.10 plus 0.20 equals 0.30 exactly;
   - round every amount to cents (`ROUND_HALF_UP`) before adding;
   - sum the invoice lines and compare the sum to the order total;
   - print `PASS` or `MISMATCH` plus the difference, and exit 0 for PASS, 1 for MISMATCH, 2 for bad input (empty file, missing column, a value that is not a number);
   - never guess: if the input cannot be read, say so instead of passing.
3. Add tests before trusting it: a matching invoice, a mismatching invoice, a rounding case, and an empty file.
4. Run the tests and the script on the sample and show the real output.
5. Explain the limit: the rule proves the lines add up to the total. It does not prove the invoice is correct, the prices are right or the goods arrived. Anything that does not fit the rule (a free text email, a missing column) should go to a person, or to a model with a person checking the result.
6. Mention that a reference version with tests lives in the resources folder of the repository this plugin came from (resources/invoice-rule-check).
