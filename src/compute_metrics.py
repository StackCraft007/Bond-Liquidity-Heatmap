"""Compute depth score & spread metrics using improved algorithm for better heatmap distribution."""
import pandas as pd, sqlite3, numpy as np, pathlib
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ROOT = pathlib.Path(__file__).resolve().parent.parent
db_path = ROOT / "heatmap.db"
conn = sqlite3.connect(db_path)

logger.info(f"Loading trades from database: {db_path}")
trades = pd.read_sql("SELECT * FROM raw_trade_events ORDER BY trade_ts", conn,
                    parse_dates=["trade_ts"])

logger.info(f"Loaded {len(trades)} trades for {trades['isin'].nunique()} ISINs")
logger.info(f"Date range: {trades['trade_ts'].min()} to {trades['trade_ts'].max()}")
logger.info(f"Rating distribution: {trades['rating'].value_counts().to_dict()}")

def compute_depth_score(group):
    """Compute depth score with improved algorithm for better distribution"""
    isin = group['isin'].iloc[0]
    logger.info(f"Processing ISIN {isin} with {len(group)} trades")
    
    group = group.sort_values('trade_ts')
    
    # Calculate time since last trade (in minutes)
    group['time_since_last'] = group['trade_ts'].diff().dt.total_seconds() / 60
    
    # Calculate spread (price difference in basis points)
    group['spread_bps'] = group['price'].diff().abs() * 10000  # Convert to basis points
    
    # Calculate volume-weighted metrics
    group['volume_weighted_price'] = (group['price'] * group['qty_cr']).rolling(5, min_periods=1).sum() / group['qty_cr'].rolling(5, min_periods=1).sum()
    
    # Calculate depth score with better formula
    # Use rolling averages to smooth the data
    rolling_volume = group['qty_cr'].rolling(10, min_periods=5).sum()
    rolling_spread = group['spread_bps'].rolling(10, min_periods=5).mean()
    rolling_time = group['time_since_last'].rolling(10, min_periods=5).mean()
    
    # Depth score = (Volume / Time) / (Spread + 1)
    # This creates better distribution
    min_spread = 0.5  # Minimum 0.5 bps spread
    min_time = 0.5    # Minimum 0.5 minutes
    
    group['depth_score'] = (rolling_volume / (rolling_time + min_time)) / (rolling_spread + min_spread)
    
    # Log some statistics for debugging
    logger.info(f"  {isin} - Volume range: {group['qty_cr'].min()/1e6:.1f}M to {group['qty_cr'].max()/1e6:.1f}M")
    logger.info(f"  {isin} - Spread range: {group['spread_bps'].min():.2f} to {group['spread_bps'].max():.2f} bps")
    logger.info(f"  {isin} - Time range: {group['time_since_last'].min():.2f} to {group['time_since_last'].max():.2f} minutes")
    logger.info(f"  {isin} - Raw depth range: {group['depth_score'].min():.2f} to {group['depth_score'].max():.2f}")
    
    # Normalize depth score to 0-100 range for better visualization
    if group['depth_score'].max() > 0:
        group['depth_score'] = (group['depth_score'] / group['depth_score'].max()) * 100
        logger.info(f"  {isin} - Normalized depth range: {group['depth_score'].min():.2f} to {group['depth_score'].max():.2f}")
    
    # Calculate additional metrics
    group['vwap'] = (group['price'] * group['qty_cr']).rolling(10, min_periods=1).sum() / group['qty_cr'].rolling(10, min_periods=1).sum()
    group['volume_15min'] = group['qty_cr'].rolling(window=15, min_periods=1).sum()
    
    return pd.DataFrame({
        'isin': group['isin'].iloc[0],
        'trade_ts': group['trade_ts'],
        'depth_score': group['depth_score'],
        'spread': group['spread_bps'],
        'time_since_last': group['time_since_last'],
        'vwap': group['vwap'],
        'volume_15min': group['volume_15min'],
        'price': group['price'],
        'qty_cr': group['qty_cr']
    })

# Process each ISIN separately
all_metrics = []
valid_isins = 0
total_isins = len(trades['isin'].unique())

logger.info(f"Processing {total_isins} ISINs for depth calculation")

for isin in trades['isin'].unique():
    isin_trades = trades[trades['isin'] == isin]
    if len(isin_trades) > 5:  # Need at least 5 trades for meaningful calculations
        try:
            metrics = compute_depth_score(isin_trades)
            all_metrics.append(metrics)
            valid_isins += 1
        except Exception as e:
            logger.error(f"Error processing ISIN {isin}: {e}")
    else:
        logger.warning(f"ISIN {isin} has only {len(isin_trades)} trades, skipping")

logger.info(f"Successfully processed {valid_isins} out of {total_isins} ISINs")

if all_metrics:
    metrics_df = pd.concat(all_metrics, ignore_index=True)
    metrics_df = metrics_df.dropna()
    
    logger.info(f"Final metrics dataframe: {len(metrics_df)} rows")
    logger.info(f"Depth score statistics:")
    logger.info(f"  - Min: {metrics_df['depth_score'].min():.2f}")
    logger.info(f"  - Max: {metrics_df['depth_score'].max():.2f}")
    logger.info(f"  - Mean: {metrics_df['depth_score'].mean():.2f}")
    logger.info(f"  - Median: {metrics_df['depth_score'].median():.2f}")
    
    # Store in database
    metrics_df.to_sql("trade_metrics", conn, if_exists="replace", index=False)
    conn.commit()
    
    print(f"Computed depth scores for {metrics_df['isin'].nunique()} ISINs ({len(metrics_df)} rows).")
    print(f"Depth score range: {metrics_df['depth_score'].min():.2f} to {metrics_df['depth_score'].max():.2f}")
    print(f"Spread range: {metrics_df['spread'].min():.2f} to {metrics_df['spread'].max():.2f} bps")
    print(f"Time range: {metrics_df['time_since_last'].min():.2f} to {metrics_df['time_since_last'].max():.2f} minutes")
    
    # Show distribution statistics
    print(f"\nDepth score distribution:")
    print(f"  - Mean: {metrics_df['depth_score'].mean():.2f}")
    print(f"  - Median: {metrics_df['depth_score'].median():.2f}")
    print(f"  - Std Dev: {metrics_df['depth_score'].std():.2f}")
    print(f"  - 25th percentile: {metrics_df['depth_score'].quantile(0.25):.2f}")
    print(f"  - 75th percentile: {metrics_df['depth_score'].quantile(0.75):.2f}")
    
    # Additional debugging info
    print(f"\nDetailed statistics:")
    print(f"  - Total ISINs processed: {valid_isins}/{total_isins}")
    print(f"  - Non-null depth scores: {metrics_df['depth_score'].notna().sum()}")
    print(f"  - Zero depth scores: {(metrics_df['depth_score'] == 0).sum()}")
    print(f"  - Very low depth scores (<1): {(metrics_df['depth_score'] < 1).sum()}")
else:
    logger.error("No valid metrics computed - need at least 5 trades per ISIN.")
    print("No valid metrics computed - need at least 5 trades per ISIN.")

conn.close()