![Telecom Plan Revenue Analysis](assets/banner.svg)

**English** · [Português](README.pt-BR.md) · [Portfolio](https://github.com/joaovspereira)

# Telecom Plan Revenue Analysis

**Decision question:** How do monthly invoices differ across plans after applying billing rules consistently?

## Published scope

A corrected billing and statistical-analysis implementation rebuilt from the original telecom notebook. The old revenue totals and p-values are intentionally excluded because the original formula charged raw excess GB a second time as dollars.

## What this project demonstrates

- Round each call upward to whole minutes and monthly total MB upward to GB.
- Construct the full subscription-month grid, including months with no activity.
- Compute a fee plus minute, message and data overage charges, all expressed in USD.
- Compare one average monthly invoice per user with a two-sided Welch test; return group sizes, mean difference, statistic and p-value.

## Verified example

In the synthetic fixture, calls of 0.1 and 1.1 minutes become **3 billed minutes**; 600 + 425 MB become **2 billed GB**. Under its invented plan, the invoice is **US$30.09**. A subscribed user with no usage pays **US$20.00**. These are rule checks, not company revenue.

## Improvements over the original project

- Removed the erroneous addition of excess GB to an already monetized bill.
- Filled all missing usage components with zero after aggregation.
- Used year-month keys, preventing January values from different years being merged.
- Included zero-usage subscription months under an explicit full-fee/no-proration policy.
- Changed inference from repeated user-month rows to user-level average invoices.

## Tools

Python · pandas · NumPy · SciPy · billing rules · cohort comparison · Welch t-test

## Run locally

Use Python 3.12. From this repository's root:

```bash
python -m venv .venv
# Activate: source .venv/bin/activate (macOS/Linux)
# Activate: .venv\Scripts\Activate.ps1 (Windows PowerShell)
python -m pip install -r requirements.txt
python billing.py
python -m unittest discover -s tests -v
python -m notebook notebooks/analysis.ipynb
```

Run all included checks with `python -m unittest discover -s tests -v`.

[Notebook](notebooks/analysis.ipynb) · [Implementation](billing.py) · [Synthetic output](reports/synthetic_demo.json) · [Data requirements](data/README.md) · [Validation record](VALIDATION.md)

## Interpretation and limitations

Plan assignment is observational and constant per user in this source. Registration and churn months incur the full fee; there is no proration, tax, refund or plan-change model. Customer-weighted mean invoices differ from month-weighted revenue. Welch inference assumes independent customers and does not establish a causal plan effect.

## Learning and next improvement

The public revision makes assumptions, units, denominators and validation boundaries explicit, so another analyst can inspect how results would be produced.

Recompute the real dataset, check sensitivity to subscription-month rules, inspect outliers and add customer-level bootstrap intervals.

Educational portfolio project derived from work in the TripleTen Data Science Bootcamp, revised for public use in September 2026. Dataset files are not redistributed. Direct dependency versions are documented from the verification environment; a complete historical environment lock is not available.

[João Vitor Pereira](https://github.com/joaovspereira) · [Contact](mailto:joaovitorsouza20pereira@gmail.com)
