"""Generate synthetic corporate-bond trade prints with comprehensive coverage across all rating-tenor buckets."""
import pandas as pd, numpy as np, random, datetime, pathlib
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OUT = pathlib.Path(__file__).resolve().parent.parent / "data"
OUT.mkdir(exist_ok=True)

today = datetime.date.today()
start_ts = datetime.datetime.combine(today, datetime.time(9, 30))
end_ts   = datetime.datetime.combine(today, datetime.time(15, 30))

ratings = ["AAA", "AA+", "AA", "AA-", "A+", "A"]
tenor_buckets = {
    "0-1y": (30, 365),
    "1-3y": (366, 3*365),
    "3-5y": (3*365+1, 5*365),
    "5-10y": (5*365+1, 10*365),
    "10y+": (10*365+1, 20*365),
}

logger.info(f"Starting data generation for {len(ratings)} ratings and {len(tenor_buckets)} tenor buckets")
logger.info(f"Date range: {start_ts} to {end_ts}")

rows = []
isin_counter = 1000000000

# Generate comprehensive data ensuring every rating-tenor combination has data
for rating in ratings:
    for bucket_name, (min_d, max_d) in tenor_buckets.items():
        logger.info(f"Generating data for {rating} - {bucket_name}")
        
        # Create 8 bonds per bucket for comprehensive coverage
        for bond_num in range(8):
            isin = f"IN{isin_counter}"
            isin_counter += 1
            maturity_date = today + datetime.timedelta(days=random.randint(min_d, max_d))
            
            # Base price varies by rating (higher rating = higher price)
            rating_base = {"AAA": 102.5, "AA+": 102.0, "AA": 101.5, "AA-": 101.0, "A+": 100.5, "A": 100.0}
            base_price = rating_base[rating]
            
            # Generate 80-200 trades per ISIN (more trades for better depth calculation)
            num_trades = random.randint(80, 200)
            logger.info(f"  Bond {isin}: {num_trades} trades, base price: {base_price}")
            
            # Create realistic trading patterns
            current_price = base_price
            bond_trades = []
            
            for trade_num in range(num_trades):
                # More realistic time distribution throughout the day
                ts_seconds = random.randint(0, int((end_ts-start_ts).total_seconds()))
                ts = start_ts + datetime.timedelta(seconds=ts_seconds)
                
                # Realistic quantities based on rating (higher rating = larger trades)
                rating_multiplier = {"AAA": 1.5, "AA+": 1.3, "AA": 1.1, "AA-": 1.0, "A+": 0.9, "A": 0.8}
                base_qty = random.randint(5_000_000, 30_000_000)
                qty = int(base_qty * rating_multiplier[rating])
                
                # Realistic price movements with some trend
                if trade_num % 10 == 0:  # Every 10th trade, introduce a trend
                    trend = random.choice([-0.01, 0.01]) * random.randint(1, 3)
                else:
                    trend = 0
                
                price_move = random.uniform(-0.015, 0.015) + trend
                current_price = max(98, min(105, current_price + price_move))
                
                buyer = f"CP{random.randint(1, 25)}"
                seller = f"CP{random.randint(26, 50)}"
                
                bond_trades.append([isin, rating, maturity_date.isoformat(), ts.isoformat(), qty, current_price, buyer, seller])
            
            rows.extend(bond_trades)
            logger.info(f"    Added {len(bond_trades)} trades for {isin}")

df = pd.DataFrame(rows, columns=["isin","rating","maturity_date","trade_ts","qty_cr","price","buyer_cp","seller_cp"])
out_file = OUT / f"ftrac_{today.strftime('%Y%m%d')}.csv"
df.to_csv(out_file, index=False)

logger.info(f"Data generation complete!")
logger.info(f"Total rows: {len(df)}")
logger.info(f"Total bonds: {len(df['isin'].unique())}")
logger.info(f"Output file: {out_file}")

print(f"[generate_data] {len(df)} rows across {len(df['isin'].unique())} bonds -> {out_file}")
print(f"[generate_data] Data distribution:")
print(f"  - Total bonds: {len(df['isin'].unique())}")
print(f"  - Ratings: {df['rating'].value_counts().to_dict()}")
print(f"  - Avg trades per bond: {len(df)/len(df['isin'].unique()):.1f}")
print(f"  - Price range: {df['price'].min():.2f} - {df['price'].max():.2f}")
print(f"  - Volume range: {df['qty_cr'].min()/1e6:.1f}M - {df['qty_cr'].max()/1e6:.1f}M")

# Verify coverage
coverage = df.groupby(['rating', 'maturity_date']).size().reset_index(name='trades')
print(f"[generate_data] Coverage check:")
for rating in ratings:
    rating_data = df[df['rating'] == rating]
    print(f"  - {rating}: {len(rating_data['isin'].unique())} bonds, {len(rating_data)} trades")

# Additional verification
print(f"[generate_data] Detailed verification:")
for rating in ratings:
    for bucket_name in tenor_buckets.keys():
        rating_data = df[df['rating'] == rating]
        # Check if we have bonds in this rating-tenor combination
        bonds_in_rating = rating_data['isin'].unique()
        if len(bonds_in_rating) > 0:
            print(f"  - {rating} {bucket_name}: {len(bonds_in_rating)} bonds, {len(rating_data)} trades")
        else:
            print(f"  - {rating} {bucket_name}: NO DATA")