from __future__ import annotations

from typing import Dict, List
from rapidfuzz import fuzz

from backend.services.normalization import (
    make_address_tokens,
    make_name_tokens,
    normalize_business_address,
    normalize_business_name,
    normalize_country,
)

FEATURE_ORDER = [
    'country_match',
    'name_exact_match',
    'name_ratio',
    'name_partial_ratio',
    'name_token_sort_ratio',
    'name_token_set_ratio',
    'name_token_jaccard',
    'address_exact_match',
    'address_ratio',
    'address_token_jaccard',
    'address_missing',
    'name_len_diff_ratio',
    'addr_len_diff_ratio',
    'shared_tokens',
]


def safe_ratio(a: str, b: str, scorer) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return float(scorer(a, b)) / 100.0


def compute_pair_features(source1_record: Dict, candidate_record: Dict) -> Dict[str, float]:
    name1 = normalize_business_name(source1_record.get('business_name', ''))
    name2 = normalize_business_name(candidate_record.get('business_name', ''))
    addr1 = normalize_business_address(source1_record.get('business_address', ''))
    addr2 = normalize_business_address(candidate_record.get('business_address', ''))
    c1 = normalize_country(source1_record.get('country', ''))
    c2 = normalize_country(candidate_record.get('country', ''))

    tokens1 = set(make_name_tokens(source1_record.get('business_name', '')))
    tokens2 = set(make_name_tokens(candidate_record.get('business_name', '')))
    addr_tokens1 = set(make_address_tokens(source1_record.get('business_address', '')))
    addr_tokens2 = set(make_address_tokens(candidate_record.get('business_address', '')))

    len_name1, len_name2 = len(name1), len(name2)
    len_addr1, len_addr2 = len(addr1), len(addr2)

    name_jaccard = len(tokens1 & tokens2) / max(1, len(tokens1 | tokens2)) if (tokens1 or tokens2) else 0.0
    addr_jaccard = len(addr_tokens1 & addr_tokens2) / max(1, len(addr_tokens1 | addr_tokens2)) if (addr_tokens1 or addr_tokens2) else 0.0

    features = {
        'country_match': float(c1 == c2 and c1 != ''),
        'name_exact_match': float(name1 == name2 and name1 != ''),
        'name_ratio': safe_ratio(name1, name2, fuzz.ratio),
        'name_partial_ratio': safe_ratio(name1, name2, fuzz.partial_ratio),
        'name_token_sort_ratio': safe_ratio(name1, name2, fuzz.token_sort_ratio),
        'name_token_set_ratio': safe_ratio(name1, name2, fuzz.token_set_ratio),
        'name_token_jaccard': float(name_jaccard),
        'address_exact_match': float(addr1 == addr2 and addr1 != ''),
        'address_ratio': safe_ratio(addr1, addr2, fuzz.ratio),
        'address_token_jaccard': float(addr_jaccard),
        'address_missing': float(not addr1 or not addr2),
        'name_len_diff_ratio': float(abs(len_name1 - len_name2) / max(1, max(len_name1, len_name2))),
        'addr_len_diff_ratio': float(abs(len_addr1 - len_addr2) / max(1, max(len_addr1, len_addr2))),
        'shared_tokens': float(len(tokens1 & tokens2) > 0),
    }
    return features


def feature_vector_from_record(record1: Dict, record2: Dict) -> List[float]:
    feature_map = compute_pair_features(record1, record2)
    return [feature_map[key] for key in FEATURE_ORDER]
