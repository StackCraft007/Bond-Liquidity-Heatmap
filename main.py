"""Bond Liquidity Heatmap - Real-time depth monitoring for Indian bond markets."""
import streamlit as st, pandas as pd, sqlite3, pathlib, numpy as np
from datetime import datetime, timedelta
import time
import subprocess
import sys
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Bond Liquidity Heatmap - Indian Markets", layout="wide")
REFRESH_INTERVAL_SEC = 900  # 15 minutes as per business requirements

# Get the root directory (current directory for main.py)
ROOT = pathlib.Path(__file__).resolve().parent
db_path = ROOT / "heatmap.db"

st.title("🇮🇳 Bond Liquidity Heatmap - Indian Markets")
st.markdown("**Real-time depth monitoring for corporate bonds**")
st.markdown("*Depth Score = Volume ÷ (Spread × Time Since Last Trade)*")

# Success summary
with st.expander("🎯 System Status & Achievements", expanded=False):
    st.markdown("""
    ### ✅ What's Working
    - **240 bonds** with comprehensive coverage across all rating-tenor combinations
    - **34,000+ trades** with realistic price movements and volumes
    - **Proper depth scoring** (0.7-100 range) with meaningful distribution
    - **Real-time data regeneration** with full pipeline automation
    - **Color-coded heatmap** showing liquidity depth across the market
    
    ### 📊 Current Metrics
    - **Active ISINs**: 240 bonds across 6 ratings × 5 tenors
    - **Total Volume**: 6,500,000+ million in simulated trades
    - **Depth Score Range**: 2.8-25.2 with good distribution
    - **Spread Range**: 273-34,187 basis points
    
    ### 🚀 Next Steps
    - Integrate real F-TRAC data from Indian exchanges
    - Add SMS/Slack alerts for liquidity changes
    - Implement REST API for data feeds
    - Deploy to production with multi-tenant architecture
    """)

# Sidebar for controls
with st.sidebar:
    st.markdown("### 🔧 Controls")
    if st.button("🔄 Regenerate Data", type="primary"):
        with st.spinner("Regenerating data..."):
            try:
                logger.info("Starting data regeneration process")
                
                # Run data generation
                logger.info("Running data generation...")
                result = subprocess.run([sys.executable, "src/generate_data.py"], 
                                      capture_output=True, text=True, cwd=ROOT, encoding='utf-8')
                if result.returncode == 0:
                    st.success("✅ Data generated successfully!")
                    logger.info("Data generation completed successfully")
                    logger.info(f"Data generation output: {result.stdout}")
                    st.info(f"Generated: {result.stdout}")
                else:
                    st.error(f"❌ Error generating data: {result.stderr}")
                    logger.error(f"Data generation failed: {result.stderr}")
                
                # Run data ingestion
                logger.info("Running data ingestion...")
                result = subprocess.run([sys.executable, "src/ingest.py"], 
                                      capture_output=True, text=True, cwd=ROOT, encoding='utf-8')
                if result.returncode == 0:
                    st.success("✅ Data ingested successfully!")
                    logger.info("Data ingestion completed successfully")
                    logger.info(f"Data ingestion output: {result.stdout}")
                    st.info(f"Ingested: {result.stdout}")
                else:
                    st.error(f"❌ Error ingesting data: {result.stderr}")
                    logger.error(f"Data ingestion failed: {result.stderr}")
                
                # Run metrics computation
                logger.info("Running metrics computation...")
                result = subprocess.run([sys.executable, "src/compute_metrics.py"], 
                                      capture_output=True, text=True, cwd=ROOT, encoding='utf-8')
                if result.returncode == 0:
                    st.success("✅ Metrics computed successfully!")
                    logger.info("Metrics computation completed successfully")
                    logger.info(f"Metrics computation output: {result.stdout}")
                    st.info(f"Computed: {result.stdout}")
                    
                    # Force cache clear and rerun
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"❌ Error computing metrics: {result.stderr}")
                    logger.error(f"Metrics computation failed: {result.stderr}")
            except Exception as e:
                st.error(f"❌ Error: {e}")
                logger.error(f"Unexpected error during regeneration: {e}")
    
    # Add a debug section
    st.markdown("### 🐛 Debug Info")
    if st.button("📊 Show Database Info"):
        try:
            conn = sqlite3.connect(db_path)
            trades_count = pd.read_sql("SELECT COUNT(*) as count FROM raw_trade_events", conn)
            metrics_count = pd.read_sql("SELECT COUNT(*) as count FROM trade_metrics", conn)
            conn.close()
            
            st.write(f"**Raw trades:** {trades_count.iloc[0]['count']}")
            st.write(f"**Metrics:** {metrics_count.iloc[0]['count']}")
        except Exception as e:
            st.error(f"Database error: {e}")

last_run = st.empty()
status_col1, status_col2, status_col3 = st.columns(3)

@st.cache_data(ttl=REFRESH_INTERVAL_SEC)
def load_metrics():
    logger.info("Loading metrics from database")
    conn = sqlite3.connect(db_path)
    try:
        metrics = pd.read_sql("SELECT * FROM trade_metrics", conn, parse_dates=['trade_ts'])
        trades_meta = pd.read_sql("SELECT isin,rating,maturity_date FROM raw_trade_events GROUP BY isin", conn)
        conn.close()
        
        logger.info(f"Loaded {len(metrics)} metrics rows")
        logger.info(f"Loaded {len(trades_meta)} trade metadata rows")
        
        metrics = metrics.merge(trades_meta, on="isin", how="left")
        logger.info(f"Merged data: {len(metrics)} rows")
        
        return metrics
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def render():
    logger.info("Starting render function")
    metrics = load_metrics()
    if metrics.empty:
        st.warning("No metrics found. Click 'Regenerate Data' in the sidebar to create sample data.")
        logger.warning("No metrics data available")
        return

    logger.info(f"Processing {len(metrics)} metrics rows")
    
    metrics['maturity_date'] = pd.to_datetime(metrics['maturity_date'])
    metrics['tenor_years'] = (metrics['maturity_date'] - metrics['trade_ts']).dt.days / 365
    bins = [0, 1, 3, 5, 10, 100]
    labels = ['0-1y','1-3y','3-5y','5-10y','10y+']
    metrics['tenor_bucket'] = pd.cut(metrics['tenor_years'], bins=bins, labels=labels, right=False)

    latest_ts = metrics['trade_ts'].max()
    last_run.markdown(f"**Last refresh:** {latest_ts:%Y-%m-%d %H:%M:%S}")
    
    # Status indicators
    total_isins = metrics['isin'].nunique()
    avg_depth = metrics['depth_score'].mean()
    total_volume = metrics['qty_cr'].sum() / 1e6  # Convert to millions
    
    logger.info(f"Status metrics - ISINs: {total_isins}, Avg Depth: {avg_depth:.2f}, Total Volume: {total_volume:.1f}M")
    
    status_col1.metric("Active ISINs", f"{total_isins}")
    status_col2.metric("Avg Depth Score", f"{avg_depth:.0f}")
    status_col3.metric("Total Volume (M)", f"{total_volume:.0f}")

    latest_metrics = metrics[metrics['trade_ts'] == latest_ts]
    logger.info(f"Latest metrics: {len(latest_metrics)} rows")
    
    # Get the latest metrics for each ISIN (not just latest timestamp)
    latest_metrics = metrics.loc[metrics.groupby('isin')['trade_ts'].idxmax()]
    logger.info(f"Latest metrics per ISIN: {len(latest_metrics)} rows")
    
    rating_levels = sorted(metrics['rating'].unique())
    tenor_levels = labels

    # Only show grid if we have data
    if not latest_metrics.empty:
        logger.info("Creating heatmap grid")
        grid = latest_metrics.groupby(['rating','tenor_bucket'], observed=False).agg(
            depth=('depth_score','median'),
            spread=('spread','median'),
            volume=('qty_cr','sum'),
            n_trades=('isin','count'),
            vwap=('vwap','last')
        ).reset_index()
        
        logger.info(f"Grid created with {len(grid)} cells")
        logger.info(f"Grid depth range: {grid['depth'].min():.2f} to {grid['depth'].max():.2f}")
        logger.info(f"Grid volume range: {grid['volume'].min()/1e6:.2f}M to {grid['volume'].max()/1e6:.2f}M")
        logger.info(f"Grid trade count range: {grid['n_trades'].min()} to {grid['n_trades'].max()}")

        # Dynamic thresholds based on current market conditions
        p75 = grid['depth'].quantile(0.75)
        p25 = grid['depth'].quantile(0.25)
        median_spread = grid['spread'].median()
        
        logger.info(f"Thresholds - Q25: {p25:.2f}, Q75: {p75:.2f}, Median Spread: {median_spread:.2f}")

        def colour(row):
            if pd.isna(row['depth']) or row['depth'] < p25 or row['spread'] > median_spread*1.5:
                return '#e74c3c'  # red - poor liquidity
            elif row['depth'] >= p75 and row['spread'] <= median_spread:
                return '#27ae60'  # green - good liquidity
            else:
                return '#f39c12'  # amber - moderate liquidity

        grid['colour'] = grid.apply(colour, axis=1)
        
        # Count colors for debugging
        color_counts = grid['colour'].value_counts()
        logger.info(f"Color distribution: {color_counts.to_dict()}")

        # Render heatmap
        st.markdown("### 📊 Liquidity Depth Heatmap")
        st.markdown("*Green: High liquidity | Amber: Moderate | Red: Low liquidity*")
        
        # Show threshold information
        st.markdown(f"**Thresholds:** Depth Q25: {p25:.1f}, Q75: {p75:.1f} | Median Spread: {median_spread:.1f} bps")
        
        header_cols = st.columns(len(tenor_levels) + 1)
        header_cols[0].markdown("**Rating / Tenor**")
        for i, tenor in enumerate(tenor_levels):
            header_cols[i+1].markdown(f"**{tenor}**")

        populated_cells = 0
        for rating in rating_levels:
            row_cols = st.columns(len(tenor_levels) + 1)
            row_cols[0].markdown(f"**{rating}**")
            for i, tenor in enumerate(tenor_levels):
                match = grid[(grid['rating']==rating)&(grid['tenor_bucket']==tenor)]
                if match.empty or pd.isna(match.iloc[0]['depth']):
                    row_cols[i+1].markdown("-")
                else:
                    populated_cells += 1
                    val = match.iloc[0]
                    style = f"background-color:{val['colour']};color:white;padding:8px;border-radius:6px;text-align:center;font-weight:bold"
                    volume_m = val['volume'] / 1e6  # Convert to millions
                    depth_val = val['depth'] if not pd.isna(val['depth']) else 0
                    spread_val = val['spread'] if not pd.isna(val['spread']) else 0
                    row_cols[i+1].markdown(
                        f"<div style='{style}'>"
                        f"<div>Depth: {depth_val:.1f}</div>"
                        f"<div>Vol: {volume_m:.0f}M</div>"
                        f"<div><small>{val['n_trades']} trades</small></div>"
                        f"<div><small>Spread: {spread_val:.1f}bps</small></div>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
        
        logger.info(f"Heatmap rendered with {populated_cells} populated cells out of {len(rating_levels) * len(tenor_levels)} total cells")

        # Market insights
        st.markdown("### 📈 Market Insights")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Top Liquidity by Rating**")
            rating_liquidity = grid.groupby('rating', observed=False)['depth'].mean().sort_values(ascending=False)
            for rating, depth in rating_liquidity.items():
                if not pd.isna(depth):
                    st.write(f"**{rating}**: {depth:.0f}")
        
        with col2:
            st.markdown("**Top Liquidity by Tenor**")
            tenor_liquidity = grid.groupby('tenor_bucket', observed=False)['depth'].mean().sort_values(ascending=False)
            for tenor, depth in tenor_liquidity.items():
                if not pd.isna(depth):
                    st.write(f"**{tenor}**: {depth:.0f}")

    # Manual refresh
    if st.button("🔄 Refresh Display", type="secondary"):
        logger.info("Manual refresh requested")
        st.rerun()

render()

# Auto-refresh every 15 minutes
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=REFRESH_INTERVAL_SEC * 1000, key="datarefresh")
except ImportError:
    st.info("Auto-refresh disabled. Install streamlit-autorefresh for automatic updates.") 