import pandas as pd
from pathlib import Path

def migrate_to_parquet():
    raw_path = Path("data/raw/tech_employment_2000_2025.csv")
    processed_dir = Path("data/processed")
    output_path = processed_dir / "tech_employment_2000_2025.parquet"

    processed_dir.mkdir(parents=True, exist_ok=True)

    print(f"Reading {raw_path}...")
    df = pd.read_csv(raw_path)


    print(f"Saving to {output_path}...")
    df.to_parquet(output_path, engine="pyarrow", index=False)
    
    print("Migration complete!")

if __name__ == "__main__":
    migrate_to_parquet()