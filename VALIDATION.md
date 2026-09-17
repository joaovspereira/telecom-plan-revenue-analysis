# Publication validation — 2026-09-17

## Provenance and scope

Original source: `Sprint 4 - Análise e Estatística de Dados.ipynb`. SHA-256: `68d1305090d34c44dc4e8f5890150530ad1a25c72c04deb4f64e7c3ba811ff9f`.

This is a substantive revision of the implementation, not a relabeling of old outputs. No original-data training or analysis run is claimed. No empirical business result from the original notebook is presented as a result of this corrected code.

## Corrections

- Removed the erroneous addition of excess GB to an already monetized bill.
- Filled all missing usage components with zero after aggregation.
- Used year-month keys, preventing January values from different years being merged.
- Included zero-usage subscription months under an explicit full-fee/no-proration policy.
- Changed inference from repeated user-month rows to user-level average invoices.

## Executed checks

- `python -m unittest discover -s tests -v`: **5 tests passed**.
- Python modules parsed and imported successfully in the verification environment.
- All notebook code cells ran sequentially in an isolated Python process with their default synthetic example and explicit original-data skip; captured output is included. The environment blocked the socket-based Jupyter kernel, so this is a Python execution check rather than a Jupyter-kernel run. No notebook magics or widget execution are used.
- `reports/synthetic_demo.json` contains the generated example results, labeled as synthetic.

## Verification environment

Python 3.12. Direct library versions observed during checks:

- pandas 2.2.3
- numpy 2.3.5
- scipy 1.17.0

## Remaining empirical work

Recompute the real dataset, check sensitivity to subscription-month rules, inspect outliers and add customer-level bootstrap intervals.

Plan assignment is observational and constant per user in this source. Registration and churn months incur the full fee; there is no proration, tax, refund or plan-change model. Customer-weighted mean invoices differ from month-weighted revenue. Welch inference assumes independent customers and does not establish a causal plan effect.
