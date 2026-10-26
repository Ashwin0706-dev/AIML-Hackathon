from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Set
import pandas as pd

from backend.config import OUTPUTS_DIR


def validate_submission_files(
    outputs_dir: Path = OUTPUTS_DIR,
    expected_source1_ids: Set[str] = None,
) -> Dict:
    matching_path = outputs_dir / 'matching_results.tsv'
    candidate_path = outputs_dir / 'candidate_pairs.tsv'

    checks = {}
    errors = []

    # 1. matching_results.tsv exists
    checks['matching_results_exists'] = matching_path.exists()
    if not checks['matching_results_exists']:
        errors.append('matching_results.tsv does not exist')

    # 2. candidate_pairs.tsv exists
    checks['candidate_pairs_exists'] = candidate_path.exists()
    if not checks['candidate_pairs_exists']:
        errors.append('candidate_pairs.tsv does not exist')

    if errors:
        return {'valid': False, 'checks': checks, 'errors': errors, 'metrics': {}}

    # Load TSVs
    try:
        match_df = pd.read_csv(matching_path, sep='\t', dtype=str).fillna('')
        checks['matching_tsv_parseable'] = True
    except Exception as e:
        checks['matching_tsv_parseable'] = False
        errors.append(f'Could not parse matching_results.tsv as TSV: {e}')
        return {'valid': False, 'checks': checks, 'errors': errors, 'metrics': {}}

    try:
        cand_df = pd.read_csv(candidate_path, sep='\t', dtype=str).fillna('')
        checks['candidate_tsv_parseable'] = True
    except Exception as e:
        checks['candidate_tsv_parseable'] = False
        errors.append(f'Could not parse candidate_pairs.tsv as TSV: {e}')
        return {'valid': False, 'checks': checks, 'errors': errors, 'metrics': {}}

    # 3. Columns are correct
    match_cols = list(match_df.columns)
    checks['matching_columns_correct'] = (match_cols == ['source1_entity_id', 'matched_entity_ids'])
    if not checks['matching_columns_correct']:
        errors.append(f"Expected matching columns ['source1_entity_id', 'matched_entity_ids'], got {match_cols}")

    cand_cols = list(cand_df.columns)
    checks['candidate_columns_correct'] = (cand_cols == ['source1_entity_id', 'candidate_entity_ids'])
    if not checks['candidate_columns_correct']:
        errors.append(f"Expected candidate columns ['source1_entity_id', 'candidate_entity_ids'], got {cand_cols}")

    # 4 & 5. No duplicates in Source 1 entities and exact alignment
    match_s1 = match_df['source1_entity_id'].tolist()
    cand_s1 = cand_df['source1_entity_id'].tolist()

    checks['no_duplicate_matching_source1'] = len(match_s1) == len(set(match_s1))
    if not checks['no_duplicate_matching_source1']:
        errors.append(f"Found {len(match_s1) - len(set(match_s1))} duplicate Source 1 entities in matching_results.tsv")

    checks['no_duplicate_candidate_source1'] = len(cand_s1) == len(set(cand_s1))
    if not checks['no_duplicate_candidate_source1']:
        errors.append(f"Found {len(cand_s1) - len(set(cand_s1))} duplicate Source 1 entities in candidate_pairs.tsv")

    # If expected IDs provided, verify every expected ID is present exactly once
    if expected_source1_ids:
        checks['all_expected_source1_present'] = set(match_s1) == expected_source1_ids
        if not checks['all_expected_source1_present']:
            errors.append(f"Matching results has {len(set(match_s1))} entities, expected {len(expected_source1_ids)}")
    else:
        checks['all_expected_source1_present'] = True

    # 6. Candidate map and match map
    cand_map: Dict[str, Set[str]] = {}
    for _, row in cand_df.iterrows():
        s1 = row['source1_entity_id']
        raw = row['candidate_entity_ids'].strip()
        cands = {c.strip() for c in raw.split(',') if c.strip()} if raw else set()
        cand_map[s1] = cands

    # 7. Validate matches are strict subset of candidate pairs and no Source 1 IDs in matches
    subset_violations = 0
    invalid_ids = 0
    source1_in_matches = 0
    total_matches = 0
    matched_entities_count = 0

    for _, row in match_df.iterrows():
        s1 = row['source1_entity_id']
        raw = row['matched_entity_ids'].strip()
        matched = [m.strip() for m in raw.split(',') if m.strip()] if raw else []

        if matched:
            matched_entities_count += 1
            total_matches += len(matched)

        cands = cand_map.get(s1, set())
        for m in matched:
            if m.startswith('S1-'):
                source1_in_matches += 1
            if not (m.startswith('S2-') or m.startswith('S3-')):
                invalid_ids += 1
            if m not in cands:
                subset_violations += 1

    checks['matches_are_subset_of_candidates'] = (subset_violations == 0)
    if subset_violations > 0:
        errors.append(f"{subset_violations} matches were not present in candidate_pairs.tsv")

    checks['no_source1_in_matches'] = (source1_in_matches == 0)
    if source1_in_matches > 0:
        errors.append(f"{source1_in_matches} Source 1 IDs found inside matches")

    checks['all_matched_ids_valid'] = (invalid_ids == 0)
    if invalid_ids > 0:
        errors.append(f"{invalid_ids} matched IDs do not follow S2- or S3- format")

    valid = len(errors) == 0

    metrics = {
        'total_source1_entities': len(match_df),
        'entities_with_matches': matched_entities_count,
        'entities_without_matches': len(match_df) - matched_entities_count,
        'total_matched_ids': total_matches,
        'total_candidates': sum(len(c) for c in cand_map.values()),
        'avg_candidates_per_entity': round(sum(len(c) for c in cand_map.values()) / max(1, len(match_df)), 2),
    }

    return {
        'valid': valid,
        'checks': checks,
        'errors': errors,
        'metrics': metrics,
    }


def validate_submission_file(path: str | Path):
    p = Path(path)
    if p.is_file():
        return validate_submission_files(p.parent)
    return validate_submission_files(p)
