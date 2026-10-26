from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from backend.services.normalization import (
    normalize_business_name,
    normalize_business_address,
    normalize_country,
    make_name_tokens,
)
from backend.services.blocking import BlockingIndex
from backend.services.feature_service import compute_pair_features, feature_vector_from_record, FEATURE_ORDER
from backend.services.training_service import parse_ground_truth
from backend.services.validation_service import validate_submission_files
from backend.config import OUTPUTS_DIR


class TestPipeline(unittest.TestCase):
    def test_normalization(self):
        self.assertEqual(normalize_business_name("Acme Corp. LLC"), "acme")
        self.assertEqual(normalize_business_name("Maure Williams Colombier Inc"), "maure williams colombier")
        self.assertEqual(normalize_business_address("123 Main Street, Suite 4"), "123 main st ste 4")
        self.assertEqual(normalize_country("US"), "us")
        self.assertEqual(normalize_country("France"), "france")

    def test_features(self):
        r1 = {'entity_id': 'S1-1', 'business_name': 'Maure Williams Colombier Inc', 'business_address': '85 Wayne Ave', 'country': 'US'}
        r2 = {'entity_id': 'S2-1', 'business_name': 'Maure Wilblims Colombier Inc', 'business_address': '', 'country': 'US'}
        feats = compute_pair_features(r1, r2)
        self.assertEqual(feats['country_match'], 1.0)
        self.assertGreater(feats['name_ratio'], 0.85)
        vec = feature_vector_from_record(r1, r2)
        self.assertEqual(len(vec), len(FEATURE_ORDER))

    def test_blocking(self):
        index = BlockingIndex()
        index.add_records([
            {'entity_id': 'S2-100', 'business_name': 'Apple Inc', 'business_address': '1 Infinite Loop', 'country': 'US'},
        ])
        cands = index.get_candidates({'entity_id': 'S1-1', 'business_name': 'Apple Store', 'business_address': '1 Infinite Loop', 'country': 'US'})
        self.assertIn('S2-100', [c['entity_id'] for c in cands])

    def test_ground_truth_parsing(self):
        df = pd.DataFrame([{'source1_entity_id': 'S1-1', 'matched_entity_ids': 'S2-1,S3-2'}])
        gt = parse_ground_truth(df)
        self.assertEqual(gt['S1-1'], {'S2-1', 'S3-2'})

    def test_real_outputs_validation(self):
        report = validate_submission_files(OUTPUTS_DIR)
        self.assertTrue(report['valid'])
        self.assertTrue(report['checks']['matching_results_exists'])
        self.assertTrue(report['checks']['candidate_pairs_exists'])
        self.assertTrue(report['checks']['matches_are_subset_of_candidates'])
        self.assertTrue(report['checks']['no_source1_in_matches'])


if __name__ == '__main__':
    unittest.main()
