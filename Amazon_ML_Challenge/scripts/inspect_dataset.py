import sys
import json
import time
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import ARTIFACTS_DIR, DATA_ROOT, TRAIN_FILES, TEST_FILES

def compute_file_summary(file_name: str, file_path: Path):
    print(f"Inspecting {file_name}...")
    t0 = time.time()
    
    # Read sample to get columns, data types and sample records
    sample_df = pd.read_csv(file_path, sep='\t', nrows=5, low_memory=False)
    columns = list(sample_df.columns)
    sample_records = sample_df.fillna('').to_dict(orient='records')
    
    # Read chunks to get total rows, missing counts, and country counts
    total_rows = 0
    missing = {col: 0 for col in columns}
    country_counts = {}
    has_country = 'country' in columns
    
    # Read first 100k rows in detail for rapid accurate missingness and distributions
    # and count total lines quickly
    with open(file_path, 'rb') as fp:
        total_rows = sum(1 for _ in fp) - 1
        
    # Analyze first 100k chunk for missingness and country distribution
    chunk_sample = pd.read_csv(file_path, sep='\t', nrows=100000, low_memory=False)
    for col in columns:
        missing[col] = int(chunk_sample[col].isna().sum() * (total_rows / len(chunk_sample)))
        
    if has_country:
        for k, v in chunk_sample['country'].fillna('Unknown').value_counts().items():
            country_counts[str(k)] = int(v)
            
    summary = {
        'name': file_name,
        'size_mb': round(file_path.stat().st_size / (1024 * 1024), 2),
        'rows': total_rows,
        'columns': columns,
        'missing': missing,
        'sample_rows': sample_records,
        'unique_country_counts': country_counts,
        'inspection_time_s': round(time.time() - t0, 2),
    }
    return summary

def generate_all_summaries():
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    all_files = {
        'train_source1.tsv': TRAIN_FILES['source1'],
        'train_source2.tsv': TRAIN_FILES['source2'],
        'train_source3.tsv': TRAIN_FILES['source3'],
        'train_ground_truth.tsv': TRAIN_FILES['ground_truth'],
        'test_source1.tsv': TEST_FILES['source1'],
        'test_source2.tsv': TEST_FILES['source2'],
        'test_source3.tsv': TEST_FILES['source3'],
    }
    
    summary = {}
    for name, path in all_files.items():
        summary[name] = compute_file_summary(name, path)
        
    summary_path = ARTIFACTS_DIR / 'dataset_summary.json'
    summary_path.write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(f"Summary saved to {summary_path}")
    return summary

if __name__ == '__main__':
    generate_all_summaries()
