from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import ARTIFACTS_DIR


def evaluate_pipeline():
    eval_path = ARTIFACTS_DIR / 'evaluation.json'
    if eval_path.exists():
        data = json.loads(eval_path.read_text())
        return data

    threshold_path = ARTIFACTS_DIR / 'threshold.json'
    if threshold_path.exists():
        data = json.loads(threshold_path.read_text())
        return data

    return {'status': 'not_evaluated', 'message': 'Model has not been trained or evaluated yet.'}


if __name__ == '__main__':
    result = evaluate_pipeline()
    print(json.dumps(result, indent=2))
