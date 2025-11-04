"""Script to create sample parquet data for testing."""

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# Sample TWAP data
sample_data = [
    {
        "twap_id": "123456",
        "state_user": "0xabc123def456",
        "state_timestamp": datetime(2025, 11, 3, 12, 0, 0, tzinfo=timezone.utc),
        "state_coin": "SOL",
        "state_side": "B",
        "state_sz": 100.0,
        "state_executedSz": 10.5,
        "state_executedNtl": 950.25,
        "status": "activated",
        "state_minutes": 30,
    },
    {
        "twap_id": "123456",
        "state_user": "0xabc123def456",
        "state_timestamp": datetime(2025, 11, 3, 12, 15, 0, tzinfo=timezone.utc),
        "state_coin": "SOL",
        "state_side": "B",
        "state_sz": 100.0,
        "state_executedSz": 25.8,
        "state_executedNtl": 2332.20,
        "status": "executing",
        "state_minutes": 30,
    },
    {
        "twap_id": "123456",
        "state_user": "0xabc123def456",
        "state_timestamp": datetime(2025, 11, 3, 12, 30, 0, tzinfo=timezone.utc),
        "state_coin": "SOL",
        "state_side": "B",
        "state_sz": 100.0,
        "state_executedSz": 100.0,
        "state_executedNtl": 9050.00,
        "status": "completed",
        "state_minutes": 30,
    },
    {
        "twap_id": "789012",
        "state_user": "0xabc123def456",
        "state_timestamp": datetime(2025, 11, 3, 14, 0, 0, tzinfo=timezone.utc),
        "state_coin": "ETH",
        "state_side": "A",
        "state_sz": 5.0,
        "state_executedSz": 2.5,
        "state_executedNtl": 8500.00,
        "status": "executing",
        "state_minutes": 60,
    },
    {
        "twap_id": "345678",
        "state_user": "0xdef456ghi789",
        "state_timestamp": datetime(2025, 11, 2, 10, 0, 0, tzinfo=timezone.utc),
        "state_coin": "BTC",
        "state_side": "B",
        "state_sz": 0.5,
        "state_executedSz": 0.5,
        "state_executedNtl": 43000.00,
        "status": "completed",
        "state_minutes": 120,
    },
]


def create_sample_parquet():
    """Create sample parquet file for testing."""
    # Create DataFrame
    df = pd.DataFrame(sample_data)
    
    # Ensure output directory exists
    output_dir = Path(__file__).parent / "data"
    output_dir.mkdir(exist_ok=True)
    
    # Save as parquet
    output_path = output_dir / "sample_twap.parquet"
    df.to_parquet(output_path, index=False)
    
    print(f"Created sample parquet file: {output_path}")
    print(f"Rows: {len(df)}")
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nSample data:")
    print(df.head())


if __name__ == "__main__":
    create_sample_parquet()
