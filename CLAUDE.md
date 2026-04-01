# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the primary Streamlit app (port 8501)
streamlit run streamlit_app.py

# Run the legacy Flask app (port 5000)
python app.py

# Run unit/feature tests (no server required)
python test_features.py

# Run integration tests (requires Flask server running on localhost:5000)
python test_integration.py
```

## Architecture

This is a FIRE (Financial Independence, Retire Early) calculator with two separate frontends sharing one calculation engine.

**`fire_calculator.py`** — The core engine. Everything is in the `FIRECalculator` class:
- Constructor takes all financial inputs (ages, portfolio values, rates, FIRE type, windfalls, large expenses)
- `generate_yearly_projections()` is the central method — drives FIRE achievement detection, accumulation vs. retirement phase switching, inflation adjustments, Social Security, windfalls, and large expense funding strategies
- `calculate_scenarios()` spins up additional `FIRECalculator` instances for conservative/optimistic/higher-contribution comparisons
- `run_monte_carlo_simulation()` uses NumPy for probabilistic projections

**`streamlit_app.py`** — Primary UI. All user inputs are collected via Streamlit sidebar widgets; results (charts, tables, scenario comparisons) are rendered in the main panel using Plotly. This is the deployed version (devcontainer auto-starts it).

**`app.py` + `templates/index.html` + `static/calculator.js`** — Legacy Flask UI. Exposes a `/calculate` POST endpoint that accepts JSON, instantiates `FIRECalculator`, and returns projection data. `test_integration.py` tests against this endpoint.

**`google-apps-script.js`** — Google Apps Script deployed as a webhook to handle feedback form submissions from the Streamlit app.

## Key Domain Notes

- FIRE types (`lean`, `barista`, `regular`, `fat`, `coast`) apply spending multipliers to the target portfolio calculation
- Large expenses support three funding strategies: `reduce_contributions`, `portfolio_withdrawal`, and `mixed_approach`; they can be single-year or multi-year
- The inflation-adjusted target portfolio grows each year — FIRE is checked against this moving target, not a fixed value
- Contributions stop once FIRE is achieved OR `desired_retirement_age` is reached, whichever comes first
- `requirements.txt` has a typo: `requestsflask` should be two separate packages (`requests` and `flask`)
