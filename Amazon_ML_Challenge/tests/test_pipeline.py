from __future__ import annotations

import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.normalization import (
    normalize_business_name,
    normalize_business_address,
    normalize_country,
    make_name_tokens,
)
from backend.services.blocking import BlockingIndex, get_record_blocking_keys
from backend.services.feature_service import compute_pair_features, feature_vector_from_record, FEATURE_ORDER
from backend.services.training_service import parse_ground_truth
from backend.services.validation_service import validate_submission_files
from backend.config import OUTPUTS_DIR


# 1. Normalization Tests
def test_normalization():
    assert normalize_business_name("Acme Corp. LLC") == "acme"
    assert normalize_business_name("Maure Williams Colombier Inc") == "maure williams colombier"
    assert normalize_business_address("123 Main Street, Suite 4") == "123 main st ste 4"
    assert normalize_country("US") == "us"
    assert normalize_country("United States") == "united states"
    assert normalize_country("France") == "france"
    tokens = make_name_tokens("Orelee's Barbershop")
    assert "orelee's" in tokens or "orelees" in tokens or "barbershop" in tokens


# 2. Feature Generation Tests
def test_feature_generation():
    r1 = {
        'entity_id': 'S1-1',
        'business_name': 'Maure Williams Colombier Inc',
        'business_address': '85 Wayne Avenue, Ticonderoga, NY',
        'country': 'US',
    }
    r2 = {
        'entity_id': 'S2-1',
        'business_name': 'Maure Wilblims Colombier Inc',
        'business_address': '',
        'country': 'US',
    }

    features = compute_pair_features(r1, r2)
    assert features['country_match'] == 1.0
    assert features['name_ratio'] > 0.85
    assert features['address_missing'] == 1.0

    vec = feature_vector_from_record(r1, r2)
    assert len(vec) == len(FEATURE_ORDER)


# 3. Blocking Tests
def test_blocking_index():
    index = BlockingIndex()
    records = [
        {'entity_id': 'S2-100', 'business_name': 'Apple Inc', 'business_address': '1 Infinite Loop', 'country': 'US'},
        {'entity_id': 'S2-200', 'business_name': 'Microsoft Corp', 'business_address': '1 Microsoft Way', 'country': 'US'},
    ]
    index.add_records(records)

    query = {'entity_id': 'S1-1', 'business_name': 'Apple Store', 'business_address': '1 Infinite Loop', 'country': 'US'}
    candidates = index.get_candidates(query, max_candidates=5)
    cand_ids = [c['entity_id'] for c in candidates]
    assert 'S2-100' in cand_ids


# 4. Ground Truth Parsing Tests
def test_ground_truth_parsing():
    df = pd.DataFrame([
        {'source1_entity_id': 'S1-100', 'matched_entity_ids': 'S2-1,S3-2'},
        {'source1_entity_id': 'S1-200', 'matched_entity_ids': ''},
        {'source1_entity_id': 'S1-300', 'matched_entity_ids': 'S2-99'},
    ])
    gt = parse_ground_truth(df)
    assert gt['S1-100'] == {'S2-1', 'S3-2'}
    assert gt['S1-200'] == set()
    assert gt['S1-300'] == {'S2-99'}


# 5. Candidate Subset Rule and Validation Tests
def test_submission_validation_rules(tmp_path):
    # Create valid dummy submission
    cand_df = pd.DataFrame([
        {'source1_entity_id': 'S1-1', 'candidate_entity_ids': 'S2-10,S3-20'},
        {'source1_entity_id': 'S1-2', 'candidate_entity_ids': 'S2-30'},
    ])
    match_df = pd.DataFrame([
        {'source1_entity_id': 'S1-1', 'matched_entity_ids': 'S2-10'},
        {'source1_entity_id': 'S1-2', 'matched_entity_ids': ''},
    ])

    cand_path = tmp_path / 'candidate_pairs.tsv'
    match_path = tmp_path / 'matching_results.tsv'
    cand_df.to_csv(cand_path, sep='\t', index=False)
    match_df.to_csv(match_path, sep='\t', index=False)

    report = validate_submission_files(tmp_path)
    assert report['valid'] is True
    assert report['checks']['matches_are_subset_of_candidates'] is True
    assert report['checks']['no_source1_in_matches'] is True


# 6. Actual Outputs Validation Test
def test_real_outputs_validation():
    report = validate_submission_files(OUTPUTS_DIR)
    assert report['valid'] is True
    assert report['metrics']['total_source1_entities'] > 0


# 7. FastAPI Endpoint Tests
def test_api_health():
    client = TestClient(app)
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'ok'
    assert data['model_loaded'] is True


def test_api_stats():
    client = TestClient(app)
    response = client.get('/api/stats')
    assert response.status_code == 200
    data = response.json()
    assert data['total_records'] > 20000000
    assert data['threshold'] > 0.0


def test_api_entity_lookup():
    client = TestClient(app)
    response = client.get('/api/entity/S1-965667')
    assert response.status_code == 200
    data = response.json()
    assert data['entity_id'] == 'S1-965667'
    assert 'Maure' in data['business_name']


def test_api_entity_matches():
    client = TestClient(app)
    response = client.get('/api/entity/S1-965667/matches')
    assert response.status_code == 200
    data = response.json()
    assert data['found'] is True
    assert 'candidates' in data
    assert len(data['candidates']) > 0
