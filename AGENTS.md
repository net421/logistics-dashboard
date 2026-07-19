# Repository working agreement

## Scope

This repository is a compact portfolio demonstration for junior supply-chain and
data-analyst roles. Prefer small, testable improvements over adding platforms or
architectural layers.

## Evidence and claims

- Always describe the bundled data as synthetic and deterministic.
- Never claim real-time operation, production use, SAP integration, customer
  impact, or professional platform experience without external evidence.
- KPI names, units, formulas, denominators, and limitations must remain visible
  in the application or README.
- All supplier, route, and monthly views must derive from the same filtered order
  rows. Do not generate finished KPI percentages directly.

## Engineering expectations

- Keep business logic in `src/`; keep `dashboard.py` focused on presentation.
- Add or update unit tests whenever a formula or data contract changes.
- Run `python -m ruff check .` and `python -m pytest -q` before handoff.
- Do not commit virtual environments, caches, credentials, generated logs, or
  user/company data.
- Do not create artificial commit activity. Commits should correspond to a real
  repair, tested behavior change, or documentation improvement.
