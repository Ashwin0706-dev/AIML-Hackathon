from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import OUTPUTS_DIR
from backend.services.validation_service import validate_submission_file


if __name__ == '__main__':
    result = validate_submission_file(OUTPUTS_DIR / 'matching_results.tsv')
    print(result)
