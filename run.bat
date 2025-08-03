@echo off
REM === Bond Liquidity Heatmap prototype ===
REM Creates a virtual environment, installs deps, generates fake data,
REM loads it into a local SQLite DB, computes metrics and launches the heatmap UI.

echo Setting up Python virtual environment...
python -m venv .venv
call .venv\Scripts\activate

echo Installing Python packages...
pip install --upgrade pip
pip install -r requirements.txt

echo Generating simulated trade data...
python src\generate_data.py

echo Ingesting data into SQLite...
python src\ingest.py

echo Computing liquidity metrics...
python src\compute_metrics.py

echo Launching Streamlit heatmap (will open in your browser)...
start "" streamlit run src\ui.py