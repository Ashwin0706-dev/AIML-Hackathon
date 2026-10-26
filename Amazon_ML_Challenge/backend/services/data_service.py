from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd

from backend.config import (
    ARTIFACTS_DIR,
    DATA_ROOT,
    MODEL_PATH,
    OUTPUTS_DIR,
    THRESHOLD_PATH,
    TRAINING_METADATA_PATH,
    TRAIN_FILES,
    TEST_FILES,
)
from backend.services.blocking import BlockingIndex
from backend.services.feature_service import compute_pair_features, feature_vector_from_record
from backend.services.prediction_service import load_model_and_threshold

DB_PATH = ARTIFACTS_DIR / 'data_index.db'
SUMMARY_PATH = ARTIFACTS_DIR / 'dataset_summary.json'


def get_db_connection() -> Optional[sqlite3.Connection]:
    if DB_PATH.exists():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    return None


def inspect_dataset(file_name: str) -> Dict:
    # Use cached summary if available
    if SUMMARY_PATH.exists():
        try:
            summaries = json.loads(SUMMARY_PATH.read_text(encoding='utf-8'))
            if file_name in summaries:
                return summaries[file_name]
        except Exception:
            pass

    path = DATA_ROOT / file_name
    if not path.exists():
        return {'error': f'File {file_name} not found'}

    # Safe lightweight sample read
    sample = pd.read_csv(path, sep='\t', nrows=5, low_memory=False).fillna('')
    with open(path, 'rb') as fp:
        total_rows = sum(1 for _ in fp) - 1

    return {
        'name': file_name,
        'rows': total_rows,
        'columns': list(sample.columns),
        'sample_rows': sample.to_dict(orient='records'),
    }


def get_all_dataset_summaries() -> Dict[str, Dict]:
    if SUMMARY_PATH.exists():
        try:
            return json.loads(SUMMARY_PATH.read_text(encoding='utf-8'))
        except Exception:
            pass

    files = [
        'train_source1.tsv', 'train_source2.tsv', 'train_source3.tsv', 'train_ground_truth.tsv',
        'test_source1.tsv', 'test_source2.tsv', 'test_source3.tsv',
    ]
    return {f: inspect_dataset(f) for f in files}


def get_system_stats() -> Dict:
    summaries = get_all_dataset_summaries()
    threshold = 0.50
    f05 = 0.0
    precision = 0.0
    recall = 0.0

    if THRESHOLD_PATH.exists():
        try:
            t_data = json.loads(THRESHOLD_PATH.read_text())
            threshold = float(t_data.get('threshold', 0.50))
            f05 = float(t_data.get('f05', 0.0))
            precision = float(t_data.get('precision', 0.0))
            recall = float(t_data.get('recall', 0.0))
        except Exception:
            pass

    s1_count = summaries.get('train_source1.tsv', {}).get('rows', 2206821) + summaries.get('test_source1.tsv', {}).get('rows', 1732544)
    s2_count = summaries.get('train_source2.tsv', {}).get('rows', 5034616) + summaries.get('test_source2.tsv', {}).get('rows', 4887273)
    s3_count = summaries.get('train_source3.tsv', {}).get('rows', 5285603) + summaries.get('test_source3.tsv', {}).get('rows', 5082316)
    train_count = (
        summaries.get('train_source1.tsv', {}).get('rows', 2206821) +
        summaries.get('train_source2.tsv', {}).get('rows', 5034616) +
        summaries.get('train_source3.tsv', {}).get('rows', 5285603) +
        summaries.get('train_ground_truth.tsv', {}).get('rows', 2206821)
    )
    test_count = (
        summaries.get('test_source1.tsv', {}).get('rows', 1732544) +
        summaries.get('test_source2.tsv', {}).get('rows', 4887273) +
        summaries.get('test_source3.tsv', {}).get('rows', 5082316)
    )

    # Check output metrics if generated
    pred_count = 0
    cand_count = 0
    cand_file = OUTPUTS_DIR / 'candidate_pairs.tsv'
    match_file = OUTPUTS_DIR / 'matching_results.tsv'

    if match_file.exists():
        try:
            with open(match_file, 'rb') as fp:
                pred_count = sum(1 for _ in fp) - 1
        except Exception:
            pass

    if cand_file.exists():
        try:
            with open(cand_file, 'rb') as fp:
                cand_count = sum(1 for _ in fp) - 1
        except Exception:
            pass

    return {
        'source1_count': s1_count,
        'source2_count': s2_count,
        'source3_count': s3_count,
        'total_records': s1_count + s2_count + s3_count,
        'train_count': train_count,
        'test_count': test_count,
        'candidate_count': cand_count,
        'prediction_count': pred_count,
        'model_status': 'Trained & Ready' if MODEL_PATH.exists() else 'Not Trained',
        'threshold': threshold,
        'precision': precision,
        'recall': recall,
        'f05': f05,
    }


def get_entity_by_id(entity_id: str) -> Optional[Dict]:
    entity_id = entity_id.strip()
    conn = get_db_connection()
    if conn:
        row = conn.execute('SELECT * FROM entities WHERE entity_id = ?', (entity_id,)).fetchone()
        if row:
            res = dict(row)
            # If source1, also fetch ground truth match if available
            gt_row = conn.execute('SELECT matched_entity_ids FROM ground_truth WHERE source1_entity_id = ?', (entity_id,)).fetchone()
            if gt_row:
                res['ground_truth_matches'] = gt_row['matched_entity_ids']
            conn.close()
            return res
        conn.close()

    # Fallback to TSV search
    target_files = []
    if entity_id.startswith('S1-'):
        target_files = [TRAIN_FILES['source1'], TEST_FILES['source1']]
    elif entity_id.startswith('S2-'):
        target_files = [TRAIN_FILES['source2'], TEST_FILES['source2']]
    elif entity_id.startswith('S3-'):
        target_files = [TRAIN_FILES['source3'], TEST_FILES['source3']]

    for tf in target_files:
        if tf.exists():
            for chunk in pd.read_csv(tf, sep='\t', chunksize=50000, low_memory=False):
                m = chunk[chunk['entity_id'] == entity_id]
                if not m.empty:
                    rec = m.iloc[0].fillna('').to_dict()
                    rec['source'] = tf.stem
                    return rec
    return None


def get_paginated_records(source_name: str, page: int = 1, page_size: int = 25, query: str = '', country: str = '') -> Dict:
    conn = get_db_connection()
    if not conn:
        return {'items': [], 'total': 0, 'page': page, 'page_size': page_size}

    page_size = max(1, min(page_size, 100))
    offset = (max(1, page) - 1) * page_size

    if source_name == 'ground_truth':
        where_clauses = []
        params = []
        if query:
            where_clauses.append('(source1_entity_id LIKE ? OR matched_entity_ids LIKE ?)')
            params.extend([f"%{query}%", f"%{query}%"])

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        total = conn.execute(f"SELECT COUNT(*) FROM ground_truth {where_sql}", params).fetchone()[0]

        sql = f"SELECT source1_entity_id, matched_entity_ids FROM ground_truth {where_sql} LIMIT ? OFFSET ?"
        rows = conn.execute(sql, params + [page_size, offset]).fetchall()
        items = [dict(r) for r in rows]
    else:
        where_clauses = ["source LIKE ?"]
        params = [f"%{source_name}%"]

        if query:
            where_clauses.append('(entity_id LIKE ? OR business_name LIKE ? OR business_address LIKE ?)')
            params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])

        if country:
            where_clauses.append('LOWER(country) = LOWER(?)')
            params.append(country)

        where_sql = f"WHERE {' AND '.join(where_clauses)}"
        total = conn.execute(f"SELECT COUNT(*) FROM entities {where_sql}", params).fetchone()[0]

        sql = f"SELECT * FROM entities {where_sql} LIMIT ? OFFSET ?"
        rows = conn.execute(sql, params + [page_size, offset]).fetchall()
        items = [dict(r) for r in rows]

    conn.close()
    return {
        'items': items,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size if total > 0 else 1,
    }


def find_matches_for_entity(entity_id: str) -> Dict:
    s1 = get_entity_by_id(entity_id)
    if not s1:
        return {'found': False, 'message': f'Entity {entity_id} not found.'}

    model, threshold = load_model_and_threshold()

    # Look up candidates from database
    conn = get_db_connection()
    cands = []
    if conn:
        # Search by country and shared words
        country = s1.get('country', '')
        bname = s1.get('business_name', '')
        words = [w for w in bname.split() if len(w) >= 3][:3]

        query_conditions = ["source IN ('train_source2', 'train_source3', 'test_source2', 'test_source3')"]
        params = []

        if country:
            query_conditions.append("country = ?")
            params.append(country)

        if words:
            word_likes = " OR ".join(["business_name LIKE ?" for _ in words])
            query_conditions.append(f"({word_likes})")
            params.extend([f"%{w}%" for w in words])

        sql = f"SELECT * FROM entities WHERE {' AND '.join(query_conditions)} LIMIT 50"
        rows = conn.execute(sql, params).fetchall()
        cands = [dict(r) for r in rows]
        conn.close()

    # If few candidates found, pick nearest pool candidates
    if len(cands) < 10 and conn:
        conn = get_db_connection()
        sql = "SELECT * FROM entities WHERE source IN ('train_source2', 'train_source3') AND country = ? LIMIT 20"
        fallback_rows = conn.execute(sql, [s1.get('country', 'US')]).fetchall()
        cands.extend([dict(r) for r in fallback_rows if r['entity_id'] not in {c['entity_id'] for c in cands}])
        conn.close()

    # Score candidates
    scored_candidates = []
    for cand in cands:
        feat_map = compute_pair_features(s1, cand)
        vec = [feat_map[k] for k in feat_map]  # in order
        prob = float(model.predict_proba([vec])[0, 1])

        is_match = prob >= threshold
        scored_candidates.append({
            'candidate_id': cand['entity_id'],
            'candidate_source': cand.get('source', 'source2'),
            'business_name': cand.get('business_name', ''),
            'business_address': cand.get('business_address', ''),
            'country': cand.get('country', ''),
            'probability': round(prob, 4),
            'decision': 'Match' if is_match else 'Reject',
            'name_similarity': round(feat_map.get('name_ratio', 0.0), 3),
            'address_similarity': round(feat_map.get('address_ratio', 0.0), 3),
            'country_match': bool(feat_map.get('country_match', 0.0)),
            'features': feat_map,
        })

    # Sort descending by probability
    scored_candidates.sort(key=lambda x: -x['probability'])

    return {
        'found': True,
        'source_entity': s1,
        'threshold': threshold,
        'candidates_count': len(scored_candidates),
        'matched_count': sum(1 for c in scored_candidates if c['decision'] == 'Match'),
        'candidates': scored_candidates,
    }
