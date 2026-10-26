from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
import numpy as np
import pandas as pd
import joblib

from backend.config import ARTIFACTS_DIR, MODEL_PATH, OUTPUTS_DIR, THRESHOLD_PATH
from backend.services.blocking import BlockingIndex
from backend.services.feature_service import feature_vector_from_record
from backend.services.normalization import normalize_country


def load_model_and_threshold():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Please train the model first.")
    model = joblib.load(MODEL_PATH)
    threshold = 0.50
    if THRESHOLD_PATH.exists():
        try:
            payload = json.loads(THRESHOLD_PATH.read_text())
            threshold = float(payload.get('threshold', 0.50))
        except Exception:
            threshold = 0.50
    return model, threshold


def run_batch_prediction(
    source1_records: List[Dict],
    source2_records: List[Dict],
    source3_records: List[Dict],
    model=None,
    threshold: float = 0.50,
    max_candidates_per_entity: int = 16,
) -> Tuple[Dict[str, List[str]], Dict[str, List[str]], List[Dict]]:
    if model is None:
        model, threshold = load_model_and_threshold()

    print(f"Building candidate blocking indexes (S2: {len(source2_records)}, S3: {len(source3_records)})...", flush=True)
    s2_index = BlockingIndex()
    s2_index.add_records(source2_records)

    s3_index = BlockingIndex()
    s3_index.add_records(source3_records)

    print("Generating candidate pairs...", flush=True)
    candidate_pairs_map: Dict[str, List[str]] = {}
    pair_tuples = []  # (s1_id, c_id, src_name, s1_dict, cand_dict)

    half_limit = max(1, max_candidates_per_entity // 2)

    for s1 in source1_records:
        s1_id = s1['entity_id']
        cands2 = s2_index.get_candidates(s1, max_candidates=half_limit)
        cands3 = s3_index.get_candidates(s1, max_candidates=half_limit)

        cand_eids = []
        for cand in cands2:
            c_id = cand['entity_id']
            if c_id not in cand_eids:
                cand_eids.append(c_id)
                pair_tuples.append((s1_id, c_id, 'source2', s1, cand))

        for cand in cands3:
            c_id = cand['entity_id']
            if c_id not in cand_eids:
                cand_eids.append(c_id)
                pair_tuples.append((s1_id, c_id, 'source3', s1, cand))

        candidate_pairs_map[s1_id] = cand_eids

    print(f"Generated {len(pair_tuples)} total candidate pairs. Computing feature matrix...", flush=True)

    matched_results_map: Dict[str, List[str]] = {s1['entity_id']: [] for s1 in source1_records}
    scored_details: List[Dict] = []

    if pair_tuples:
        # Vectorized feature computation
        X = [feature_vector_from_record(p[3], p[4]) for p in pair_tuples]
        print(f"Scoring {len(X)} pairs with model...", flush=True)
        probs = model.predict_proba(np.array(X, dtype=float))[:, 1]

        for idx, (s1_id, c_id, src_name, s1_rec, cand_rec) in enumerate(pair_tuples):
            prob = float(probs[idx])
            is_match = prob >= threshold

            if is_match and c_id in candidate_pairs_map[s1_id]:
                if c_id not in matched_results_map[s1_id]:
                    matched_results_map[s1_id].append(c_id)

            if idx < 200:  # keep first 200 for detailed inspector
                scored_details.append({
                    'source1_entity_id': s1_id,
                    'candidate_entity_id': c_id,
                    'source_type': src_name,
                    'probability': round(prob, 4),
                    'decision': 'Match' if is_match else 'Reject',
                    'business_name': cand_rec.get('business_name', ''),
                    'business_address': cand_rec.get('business_address', ''),
                    'country': cand_rec.get('country', ''),
                })

    return candidate_pairs_map, matched_results_map, scored_details


def save_submission_files(
    source1_ids_order: List[str],
    candidate_pairs_map: Dict[str, List[str]],
    matched_results_map: Dict[str, List[str]],
    outputs_dir: Path = OUTPUTS_DIR,
) -> Tuple[Path, Path]:
    outputs_dir.mkdir(parents=True, exist_ok=True)

    cand_path = outputs_dir / 'candidate_pairs.tsv'
    match_path = outputs_dir / 'matching_results.tsv'

    cand_rows = []
    match_rows = []

    for s1_id in source1_ids_order:
        cands = candidate_pairs_map.get(s1_id, [])
        matches = matched_results_map.get(s1_id, [])

        cand_rows.append({
            'source1_entity_id': s1_id,
            'candidate_entity_ids': ','.join(cands),
        })
        match_rows.append({
            'source1_entity_id': s1_id,
            'matched_entity_ids': ','.join(matches),
        })

    cand_df = pd.DataFrame(cand_rows, columns=['source1_entity_id', 'candidate_entity_ids'])
    match_df = pd.DataFrame(match_rows, columns=['source1_entity_id', 'matched_entity_ids'])

    cand_df.to_csv(cand_path, sep='\t', index=False)
    match_df.to_csv(match_path, sep='\t', index=False)

    return cand_path, match_path
