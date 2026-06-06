# CycleAnalysis / Quant Sniper

A browser-based stock charting and analysis tool built on **cycle harmonic fitting**, **TD Sequential**, **Squeeze Momentum**, **SuperTrend**, and **Chaikin Money Flow (CMF)**, powered by Streamlit.

The original desktop app lives at `../nya_V6.py` (Tkinter GUI). This folder is the **web deployment** version; the quant engine logic matches the desktop release.

> Chinese documentation: [README.md](README.md)

---

## File Overview

| File | Purpose |
|------|---------|
| **`streamlit_app.py`** | **Application entry point.** Set this as the Main file path on Streamlit Community Cloud. Provides the sidebar UI, runs the analysis pipeline, renders Plotly charts, engine logs, and an HTML download button. |
| **`quant_engine.py`** | **Quant engine** (extracted from `nya_V6.py`, no GUI dependencies). Handles data download, cycle detection (DFE), lookback selection, indicator math, trade-state analysis, and Plotly chart building. Core logic for both local and cloud runs. |
| **`nya_V6_backup.py`** | **Full backup of the original app.** A copy of `TD9ETC/nya_V6.py` for reference or rollback; not used when running the web app. |
| **`requirements.txt`** | **Python dependencies.** Used by Streamlit Cloud to install `streamlit`, `yfinance`, `plotly`, `scipy`, and related packages. |
| **`.python-version`** | **Python version pin.** Locks the runtime to Python 3.12 to avoid compatibility issues with newer cloud defaults. |
| **`.gitignore`** | **Git ignore rules.** Excludes `.venv/`, `tmp/`, `__pycache__/`, and other local artifacts from the repository. |
| **`README.md`** | Chinese documentation. |
| **`README_EN.md`** | This English documentation. |

### Runtime directories (ignored by `.gitignore`)

| Path | Purpose |
|------|---------|
| `tmp/yf_cache/` | yfinance timezone cache to reduce repeat requests |
| `tmp/quant_sniper_v8.html` | Default HTML output path from the engine (the web app mainly embeds charts in-page; HTML download is optional) |

---

## Features

- **Cycle** — Dynamic Frequency Extraction (DFE) or manual periods, harmonic fit, and forward projection
- **SuperTrend** — Bull/bear trend bands on the main chart
- **TD Sequential** — TD9 Setup and TD13/15 Countdown markers
- **Squeeze Momentum** — LazyBear-style momentum sub-chart
- **CMF** — Chaikin Money Flow sub-chart
- **Trade guidance** — Combined read on trend, TD, SQZ, and CMF

---

## Run Locally

```powershell
cd path\to\TD
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Open **http://localhost:8501** in your browser, configure parameters in the sidebar, then click **▶ Run & Analyze**.

The first run with auto lookback may take **30–90 seconds**.

---

## Deploy to Streamlit Community Cloud

1. Push this directory to a GitHub repository (e.g. `Deemolotus/CycleAnalysis`)
2. Go to [share.streamlit.io](https://share.streamlit.io) → **Create app** → **From existing repo**
3. Set:
   - **Repository** — your repo
   - **Branch** — `main`
   - **Main file path** — `streamlit_app.py`
4. Click **Deploy** and wait for dependencies to install

No Secrets are required (public market data via yfinance only).

---

## Desktop vs Web

| Edition | Files | UI |
|---------|-------|-----|
| Desktop | `TD9ETC/nya_V6.py` | Tkinter window, runs locally |
| Web | `streamlit_app.py` + `quant_engine.py` | Browser, deployable on Streamlit Cloud |

When updating engine logic, prefer editing `quant_engine.py`. The desktop and web editions are maintained separately for now.

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file in the repository root.

```
MIT License

Copyright (c) 2026 Deemolotus (Zhiwen Tan)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
