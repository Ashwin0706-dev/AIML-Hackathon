from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from backend.config import OUTPUTS_DIR, TEST_FILES
from backend.services.prediction_service import (
    load_model_and_threshold,
    run_batch_prediction,
    save_submission_files,
)
from backend.services.validation_service import validate_submission_files


def predict_test_set(sample_size: int = 5000):
    print(f"Loading test source1 ({sample_size} entities)...")
    test1_df = pd.read_csv(TEST_FILES['source1'], sep='\t', nrows=sample_size, low_memory=False).fillna('')
    test1_records = test1_df.to_dict(orient='records')
    test1_ids = [r['entity_id'] for r in test1_records]

    # Load candidate pool from test_source2 and test_source3
    print(f"Loading candidate pool from test_source2 and test_source3...")
    test2_df = pd.read_csv(TEST_FILES['source2'], sep='\t', nrows=sample_size * 5, low_memory=False).fillna('')
    test3_df = pd.read_csv(TEST_FILES['source3'], sep='\t', nrows=sample_size * 5, low_memory=False).fillna('')

    test2_records = test2_df.to_dict(orient='records')
    test3_records = test3_df.to_dict(orient='records')

    print(f"Loaded: S1: {len(test1_records)}, S2 pool: {len(test2_records)}, S3 pool: {len(test3_records)}")

    model, threshold = load_model_and_threshold()
    print(f"Loaded model. Running prediction with threshold={threshold}...")

    cand_map, match_map, scored_details = run_batch_prediction(
        test1_records,
        test2_records,
        test3_records,
        model=model,
        threshold=threshold,
        max_candidates_per_entity=20,
    )

    cand_path, match_path = save_submission_files(
        test1_ids,
        cand_map,
        match_map,
        outputs_dir=OUTPUTS_DIR,
    )

    print(f"Submission files saved to:\n  {cand_path}\n  {match_path}")

    # Validate submission files
    val_report = validate_submission_files(OUTPUTS_DIR, expected_source1_ids=set(test1_ids))
    print(f"Submission validation valid={val_report['valid']}")
    print(f"Metrics: {val_report['metrics']}")

    return {
        'candidate_pairs_path': str(cand_path),
        'matching_results_path': str(match_path),
        'records_predicted': len(test1_ids),
        'validation': val_report,
    }


if __name__ == '__main__':
    predict_test_set()
