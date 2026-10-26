from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import OUTPUTS_DIR
from backend.ml.predict import predict_test_set
from backend.ml.train_model import run_training_pipeline
from backend.services.validation_service import validate_submission_files


def run_complete_pipeline():
    start_time = time.time()
    print("=" * 60)
    print("AMAZON ML CHALLENGE: BUSINESS ENTITY RESOLUTION PIPELINE")
    print("=" * 60)

    print("\n[Step 1/3] Inspecting datasets...")
    subprocess.run([sys.executable, str(PROJECT_ROOT / 'scripts' / 'inspect_dataset.py')], check=True)

    print("\n[Step 2/3] Training model and tuning threshold...")
    training_res = run_training_pipeline(max_gt_rows=3000)

    print("\n[Step 3/3] Generating candidate pairs and final results...")
    predict_res = predict_test_set(sample_size=5000)
    val_report = validate_submission_files(OUTPUTS_DIR)

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETED SUCCESSFULLY!")
    print(f"Total Runtime: {round(time.time() - start_time, 2)} seconds")
    print(f"Optimal Threshold: {training_res['threshold']}")
    print(f"Validation Metrics: {training_res['metrics']}")
    print(f"Submission Valid: {val_report['valid']}")
    print(f"Matching Results: {predict_res['matching_results_path']}")
    print(f"Candidate Pairs: {predict_res['candidate_pairs_path']}")
    print("=" * 60)

    return {
        'training': training_res,
        'prediction': predict_res,
        'validation': val_report,
    }


if __name__ == '__main__':
    run_complete_pipeline()
