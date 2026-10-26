from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from backend.config import TRAIN_FILES
from backend.services.training_service import parse_ground_truth, train_model


def run_training_pipeline(max_gt_rows: int = 3000, random_seed: int = 42):
    print(f"Loading ground truth sample ({max_gt_rows} rows)...")
    gt_df = pd.read_csv(TRAIN_FILES['ground_truth'], sep='\t', nrows=max_gt_rows, low_memory=False)
    ground_truth = parse_ground_truth(gt_df)

    needed_s1 = set(ground_truth.keys())
    needed_s2 = set()
    needed_s3 = set()

    for matches in ground_truth.values():
        for mid in matches:
            if mid.startswith('S2-'):
                needed_s2.add(mid)
            elif mid.startswith('S3-'):
                needed_s3.add(mid)

    print(f"Entities to extract: S1: {len(needed_s1)}, S2: {len(needed_s2)}, S3: {len(needed_s3)}")

    # Extract S1 records
    s1_dict = {}
    for chunk in pd.read_csv(TRAIN_FILES['source1'], sep='\t', chunksize=100000, low_memory=False):
        m = chunk[chunk['entity_id'].isin(needed_s1)]
        for r in m.to_dict(orient='records'):
            s1_dict[r['entity_id']] = r
        if len(s1_dict) >= len(needed_s1):
            break

    # Extract S2 records + pool for negatives
    s2_dict = {}
    for chunk in pd.read_csv(TRAIN_FILES['source2'], sep='\t', chunksize=100000, low_memory=False):
        m = chunk[chunk['entity_id'].isin(needed_s2)]
        for r in m.to_dict(orient='records'):
            s2_dict[r['entity_id']] = r
        # Also grab a few rows from each chunk as pool
        if len(s2_dict) < len(needed_s2) + 2000:
            sample_sub = chunk.head(200).to_dict(orient='records')
            for r in sample_sub:
                s2_dict[r['entity_id']] = r
        if len(s2_dict) >= len(needed_s2) + 2000 and len(needed_s2.intersection(s2_dict.keys())) >= len(needed_s2):
            break

    # Extract S3 records + pool for negatives
    s3_dict = {}
    for chunk in pd.read_csv(TRAIN_FILES['source3'], sep='\t', chunksize=100000, low_memory=False):
        m = chunk[chunk['entity_id'].isin(needed_s3)]
        for r in m.to_dict(orient='records'):
            s3_dict[r['entity_id']] = r
        if len(s3_dict) < len(needed_s3) + 2000:
            sample_sub = chunk.head(200).to_dict(orient='records')
            for r in sample_sub:
                s3_dict[r['entity_id']] = r
        if len(s3_dict) >= len(needed_s3) + 2000 and len(needed_s3.intersection(s3_dict.keys())) >= len(needed_s3):
            break

    print(f"Extracted: S1: {len(s1_dict)}, S2: {len(s2_dict)}, S3: {len(s3_dict)}")
    print("Training HistGradientBoostingClassifier and tuning threshold...")

    results = train_model(
        s1_dict, s2_dict, s3_dict, ground_truth,
        max_positive=3000, random_seed=random_seed
    )

    print(f"Training complete! Selected threshold: {results['threshold']}")
    print(f"Validation F0.5: {results['metrics']['f05']}, Precision: {results['metrics']['precision']}, Recall: {results['metrics']['recall']}")
    return results


if __name__ == '__main__':
    run_training_pipeline()
