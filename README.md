# Earnings Report Alert System

How do S&P 500 stocks move after a company beats or misses its earnings estimate? This project backtests **11,766 earnings reports across 500 S&P 500 companies**, then uses those results to flag recently released earnings reports with a historical signal, shown in a Streamlit dashboard.

> ⚠️ **Not investment advice.** This is an educational data project. See [Limitations](#limitations).

## What it does

1. **Collects earnings history** (EPS estimate, reported EPS, surprise %) for every current S&P 500 company using `yfinance`.
2. **Backtests the price reaction** 1, 3 and 5 trading days after each report, using the correct base price for the announcement time (see [Method](#method)).
3. **Compares beats vs. misses** and computes historical success rates.
4. **Alerts on fresh reports** released in the last 3 days and labels each one `BUY`, `SELL`, `HOLD` or `NO ESTIMATE` based on the backtest.
5. **Dashboard** (Streamlit) showing historical stats, the latest alerts, best/worst reacting companies and the full backtest log.

## Results

Backtest run on 27 October 2026 (11,766 released reports):

| | Beat (surprise > 0) | Miss (surprise ≤ 0) |
|---|---|---|
| Reports | 9,464 | 2,283 |
| **1 day:** mean change / share that rose | +0.83% / 54.92% | −2.18% / 34.82% |
| **3 days:** mean change / share that rose | +1.18% / 55.92% | −2.01% / 38.04% |
| **5 days:** mean change / share that rose | +1.41% / 57.04% | −1.77% / 40.57% |

Report counts per row vary slightly because the most recent reports do not yet have 3 or 5 trading days of data.

**Key findings**

- Misses are punished harder than beats are rewarded: the average 1-day drop after a miss (−2.18%) is more than double the average gain after a beat (+0.83%).
- The direction of the surprise matters, but the size does not seem to: the correlation between surprise size and price change is close to zero (0.034 after 1 and 3 days, 0.028 after 5 days).

### The advice rule

| Condition | Signal |
|---|---|
| Beat, and historically ≥ 55% of beats rose within 5 days | `BUY` |
| Miss, and historically ≤ 45% of misses rose within 5 days | `SELL` |
| Anything else | `HOLD` |
| No analyst EPS estimate (surprise cannot be calculated) | `NO ESTIMATE` |

With the current numbers (57.04% and 40.57%), every beat gets `BUY` and every miss gets `SELL`. The signal uses only the direction of the surprise, not its size.

## Method

Earnings timestamps are converted to New York time, and the base price depends on when the report was released:

| Announcement | Base price | Day 1 |
|---|---|---|
| Before 16:00 (pre-market or during session) | Previous trading day's close | Announcement day |
| 16:00 or later (after close) | Announcement day's close | Next trading day |

In this run, 6,712 reports were released before the close and 5,054 after. Only one report had an unknown time (00:00) and is treated as before the close.

> **Why this matters:** an earlier version used the announcement day's close as the base price for every report. For pre-market reports this skipped the biggest reaction day. Fixing it more than doubled the measured 1-day gap between beats and misses (from about 1.2 to about 3.0 percentage points).

## Limitations

- **Raw returns, not abnormal returns.** Price changes are not adjusted for overall market movement, so part of the average gain after a beat may simply reflect a rising market.
- **Survivorship bias.** The company list is today's S&P 500 constituents, applied to past data. Companies that left the index are missing.
- **No trading costs.** Spreads, commissions and slippage are ignored.
- **Data source.** All data comes from Yahoo Finance via `yfinance`, an unofficial API. Data can contain errors and requests can be rate-limited.
- **Simple signal.** The advice rule is a historical average applied to every company, ignoring company-specific behaviour and surprise size.

## Project structure

```
earnings-report-alert/
├── earnings_analysis.ipynb   # data collection, backtest, alert and advice
├── earnings_app.py           # Streamlit dashboard
├── requirements.txt
└── README.md
```

Running the notebook creates a `data/` folder next to it, which the dashboard reads:

```
data/
├── earnings_raw.csv           # raw earnings history collected in step 1
├── full_backtest.csv          # every backtested report with 1/3/5-day reactions
├── fresh_earnings.csv         # reports from the last 3 days, with their signal
├── company_performance.csv    # average 5-day reaction per company
└── summary_stats.json         # beat/miss stats shown on the dashboard
```

## Data

All market data (earnings dates, EPS estimates, reported EPS and prices) comes from Yahoo Finance through the unofficial [`yfinance`](https://github.com/ranaroussi/yfinance) library, and the S&P 500 company list comes from Wikipedia.

**The data files are not included in this repository**, because Yahoo Finance's terms restrict redistributing its data. Run the notebook to generate them yourself. The project is intended for educational and research use only.

## How to run

### On Kaggle

1. Upload `earnings_analysis.ipynb` and turn **Internet** on in the session options.
2. Run all cells (about 30 minutes in total, mostly waiting on `yfinance`).
3. The notebook writes the data files to `data/`.
4. To test the dashboard in the last cell, first download the app script into the notebook:
   ```
   !wget -q https://raw.githubusercontent.com/faten20/earnings-report-alert/main/earnings_app.py -O earnings_app.py
   ```

### Locally

```bash
pip install -r requirements.txt
jupyter notebook earnings_analysis.ipynb   # run all cells to create data/
streamlit run earnings_app.py
```

The dashboard needs the `data/` folder, so run the notebook at least once before starting it.

## Author

**Dr. Faten Alzazah** · PhD in Computer Science (Middlesex University London) · Research in financial sentiment analysis and stock market prediction
