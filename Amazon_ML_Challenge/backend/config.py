from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = PROJECT_ROOT
ARTIFACTS_DIR = PROJECT_ROOT / 'backend' / 'artifacts'
OUTPUTS_DIR = PROJECT_ROOT / 'backend' / 'outputs'
FRONTEND_DIR = PROJECT_ROOT / 'frontend'

TRAIN_FILES = {
    'source1': DATA_ROOT / 'train_source1.tsv',
    'source2': DATA_ROOT / 'train_source2.tsv',
    'source3': DATA_ROOT / 'train_source3.tsv',
    'ground_truth': DATA_ROOT / 'train_ground_truth.tsv',
}

TEST_FILES = {
    'source1': DATA_ROOT / 'test_source1.tsv',
    'source2': DATA_ROOT / 'test_source2.tsv',
    'source3': DATA_ROOT / 'test_source3.tsv',
}

REQUIRED_COLUMNS = ['entity_id', 'business_name', 'business_address', 'country']
MODEL_PATH = ARTIFACTS_DIR / 'model.joblib'
THRESHOLD_PATH = ARTIFACTS_DIR / 'threshold.json'
FEATURE_METADATA_PATH = ARTIFACTS_DIR / 'feature_metadata.json'
TRAINING_METADATA_PATH = ARTIFACTS_DIR / 'training_metadata.json'

ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
