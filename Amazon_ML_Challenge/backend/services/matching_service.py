from __future__ import annotations

from typing import Dict, List

from backend.services.feature_service import FEATURE_ORDER, feature_vector_from_record


def predict_probability(model, source1_record: Dict, source2_record: Dict) -> float:
    vector = feature_vector_from_record(source1_record, source2_record)
    prob = model.predict_proba([vector])[0, 1]
    return float(prob)


def predict_pair(model, source1_record: Dict, source2_record: Dict, threshold: float = 0.5) -> Dict:
    prob = predict_probability(model, source1_record, source2_record)
    decision = 'Match' if prob >= threshold else 'No match'
    return {
        'probability': prob,
        'decision': decision,
        'feature_vector': {key: value for key, value in zip(FEATURE_ORDER, feature_vector_from_record(source1_record, source2_record))},
    }
