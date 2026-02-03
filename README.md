# portfolio
showcase for projects &amp; assorted small ideas

## Dashboard setup (pip/venv)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Required dependencies
At minimum, install:
- streamlit
- plotly
- yfinance
- pandas

## Launch
```bash
streamlit run dashboard/app.py
```

## API limits and refresh guidance
- Data providers like Yahoo Finance can throttle or rate-limit requests; excessive refreshes may lead to temporary blocks.
- Suggested refresh frequency: every 5–15 minutes for interactive use, and less often for unattended dashboards.
