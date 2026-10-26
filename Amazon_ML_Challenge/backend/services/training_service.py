from __future__ import annotations

import json
import random
from datetime import datetime
from typing import Dict, List, Set, Tuple
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance
import joblib

from backend.config import (
    ARTIFACTS_DIR,
    FEATURE_METADATA_PATH,
    MODEL_PATH,
    THRESHOLD_PATH,
    TRAINING_METADATA_PATH,
)
from backend.services.feature_service import FEATURE_ORDER, feature_vector_from_record
from backend.services.normalization import normalize_country, normalize_business_name
from backend.services.evaluation_service import compute_precision_recall_f05


def parse_ground_truth(ground_truth_df: pd.DataFrame) -> Dict[str, Set[str]]:
    matches = {}
    for _, row in ground_truth_df.iterrows():
        source1_id = str(row['source1_entity_id']).strip()
        raw = str(row.get('matched_entity_ids', '')).strip()
        vals = set()
        if raw and raw.lower() != 'nan':
            for item in raw.split(','):
                clean = item.strip()
                if clean:
                    vals.add(clean)
        matches[source1_id] = vals
    return matches


def build_training_pairs(
    source1_dict: Dict[str, Dict],
    source2_dict: Dict[str, Dict],
    source3_dict: Dict[str, Dict],
    ground_truth: Dict[str, Set[str]],
    max_positive: int = 4000,
    neg_to_pos_ratio: float = 2.0,
    random_seed: int = 42,
) -> Tuple[np.ndarray, np.ndarray, List[str], List[str]]:
    random.seed(random_seed)
    np.random.seed(random_seed)

    all_other = {**source2_dict, **source3_dict}

    # Group entities by country for hard negative sampling
    country_to_others = {}
    for eid, rec in all_other.items():
        c = normalize_country(rec.get('country', ''))
        country_to_others.setdefault(c, []).append(rec)

    positive_pairs = []
    source1_groups = []  # track source1_id for each pair to perform grouped split

    for s1_id, matched_ids in ground_truth.items():
        s1_rec = source1_dict.get(s1_id)
        if not s1_rec:
            continue
        for other_id in matched_ids:
            other_rec = all_other.get(other_id)
            if other_rec:
                positive_pairs.append((s1_rec, other_rec, 1, s1_id))
                if len(positive_pairs) >= max_positive:
                    break
        if len(positive_pairs) >= max_positive:
            break

    num_pos = len(positive_pairs)
    target_neg = int(num_pos * neg_to_pos_ratio)

    negative_pairs = []
    gt_pairs_set = {(s1_id, other_id) for s1_id, matches in ground_truth.items() for other_id in matches}

    # Sample hard negatives: same country, similar token or different entity
    s1_items = [p[0] for p in positive_pairs]
    random.shuffle(s1_items)

    for s1_rec in s1_items:
        if len(negative_pairs) >= target_neg:
            break
        s1_id = s1_rec['entity_id']
        c = normalize_country(s1_rec.get('country', ''))
        s1_name = normalize_business_name(s1_rec.get('business_name', ''))
        s1_tokens = set(s1_name.split())

        pool = country_to_others.get(c, list(all_other.values()))
        sample_pool = random.sample(pool, min(len(pool), 40))

        # Sort pool candidates by shared tokens with s1 to get hard negatives
        hard_pool = []
        for cand in sample_pool:
            cand_id = cand['entity_id']
            if (s1_id, cand_id) in gt_pairs_set:
                continue
            cand_tokens = set(normalize_business_name(cand.get('business_name', '')).split())
            overlap = len(s1_tokens & cand_tokens)
            hard_pool.append((overlap, cand))

        hard_pool.sort(key=lambda x: -x[0])
        for _, cand in hard_pool[:2]:
            negative_pairs.append((s1_rec, cand, 0, s1_id))
            if len(negative_pairs) >= target_neg:
                break

    all_pairs = positive_pairs + negative_pairs
    random.shuffle(all_pairs)

    X = []
    y = []
    groups = []
    for r1, r2, label, s1_id in all_pairs:
        X.append(feature_vector_from_record(r1, r2))
        y.append(label)
        groups.append(s1_id)

    return np.array(X, dtype=float), np.array(y, dtype=int), FEATURE_ORDER, groups


def train_model(
    source1_dict: Dict[str, Dict],
    source2_dict: Dict[str, Dict],
    source3_dict: Dict[str, Dict],
    ground_truth: Dict[str, Set[str]],
    max_positive: int = 4000,
    random_seed: int = 42,
):
    X, y, feature_names, groups = build_training_pairs(
        source1_dict, source2_dict, source3_dict, ground_truth,
        max_positive=max_positive, random_seed=random_seed
    )

    # Grouped split by Source 1 entity to avoid data leakage
    unique_groups = list(dict.fromkeys(groups))
    random.Random(random_seed).shuffle(unique_groups)
    split_idx = int(len(unique_groups) * 0.8)
    train_groups = set(unique_groups[:split_idx])

    train_mask = np.array([g in train_groups for g in groups])
    val_mask = ~train_mask

    X_train, y_train = X[train_mask], y[train_mask]
    X_val, y_val = X[val_mask], y[val_mask]

    # Train HistGradientBoostingClassifier
    model = HistGradientBoostingClassifier(
        random_state=random_seed,
        max_iter=120,
        learning_rate=0.08,
        min_samples_leaf=20,
        class_weight='balanced',
    )
    model.fit(X_train, y_train)

    # Calculate validation probabilities
    val_probs = model.predict_proba(X_val)[:, 1]

    # Threshold tuning for F0.5
    threshold_results = []
    best_threshold = 0.50
    best_f05 = -1.0
    best_metrics = {}

    for t in [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]:
        preds = (val_probs >= t).astype(int)
        m = compute_precision_recall_f05(y_val, preds)
        m['threshold'] = round(t, 2)
        threshold_results.append(m)
        if m['f05'] > best_f05:
            best_f05 = m['f05']
            best_threshold = t
            best_metrics = m

    # Save artifacts
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(MODEL_PATH, 'wb') as f:
        joblib.dump(model, f)

    threshold_payload = {
        'threshold': round(best_threshold, 2),
        'f05': round(best_f05, 4),
        'precision': round(best_metrics.get('precision', 0.0), 4),
        'recall': round(best_metrics.get('recall', 0.0), 4),
        'tp': int(best_metrics.get('tp', 0)),
        'fp': int(best_metrics.get('fp', 0)),
        'fn': int(best_metrics.get('fn', 0)),
        'updated_at': datetime.now().isoformat(),
    }
    THRESHOLD_PATH.write_text(json.dumps(threshold_payload, indent=2))

    # Feature importances via permutation importance
    perm_importance = permutation_importance(model, X_val, y_val, n_repeats=5, random_state=random_seed)
    importances = {name: round(float(imp), 4) for name, imp in zip(feature_names, perm_importance.importances_mean)}

    feature_metadata = {
        'feature_names': feature_names,
        'feature_importances': importances,
        'train_samples': int(len(X_train)),
        'val_samples': int(len(X_val)),
        'positive_count': int(y.sum()),
        'negative_count': int(len(y) - y.sum()),
    }
    FEATURE_METADATA_PATH.write_text(json.dumps(feature_metadata, indent=2))

    training_metadata = {
        'model_type': 'HistGradientBoostingClassifier',
        'random_seed': random_seed,
        'trained_at': datetime.now().isoformat(),
        'hyperparameters': {
            'max_iter': 120,
            'learning_rate': 0.08,
            'class_weight': 'balanced',
            'min_samples_leaf': 20,
        },
        'best_threshold': round(best_threshold, 2),
        'best_metrics': best_metrics,
        'threshold_comparison': threshold_results,
    }
    TRAINING_METADATA_PATH.write_text(json.dumps(training_metadata, indent=2))

    # Also save evaluation.json
    eval_path = ARTIFACTS_DIR / 'evaluation.json'
    eval_path.write_text(json.dumps(training_metadata, indent=2))

    return {
        'model': model,
        'threshold': best_threshold,
        'metrics': best_metrics,
        'feature_metadata': feature_metadata,
        'training_metadata': training_metadata,
    }
