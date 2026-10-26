from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Set, Tuple
import pandas as pd

from backend.services.normalization import (
    make_name_tokens,
    make_address_tokens,
    normalize_country,
    normalize_business_name,
    normalize_business_address,
)


def get_record_blocking_keys(record: Dict) -> Set[Tuple[str, str]]:
    keys = set()
    country = normalize_country(record.get('country', ''))
    norm_name = normalize_business_name(record.get('business_name', ''))
    name_tokens = [t for t in norm_name.split() if len(t) >= 3]
    addr_tokens = make_address_tokens(record.get('business_address', ''))

    # Strategy 1: Country + first 3 letters of business name
    if country and len(norm_name) >= 3:
        keys.add(('c_pfx', f"{country}_{norm_name[:3]}"))

    # Strategy 2: Exact normalized business name
    if norm_name and len(norm_name) >= 3:
        keys.add(('name_exact', norm_name))

    # Strategy 3: Country + significant name tokens
    if country:
        for t in name_tokens[:3]:
            keys.add(('c_token', f"{country}_{t}"))
            
    # Strategy 4: Significant name token without country (handles open-set / missing country)
    for t in name_tokens[:2]:
        keys.add(('token', t))

    # Strategy 5: Country + first address token (e.g. street number or name)
    if country and addr_tokens:
        keys.add(('c_addr', f"{country}_{addr_tokens[0]}"))

    return keys


class BlockingIndex:
    def __init__(self):
        self.index = defaultdict(list)
        self.records = {}

    def add_records(self, records: List[Dict]):
        for rec in records:
            eid = rec['entity_id']
            self.records[eid] = rec
            keys = get_record_blocking_keys(rec)
            for k in keys:
                self.index[k].append(eid)

    def get_candidates(self, query_record: Dict, max_candidates: int = 25) -> List[Dict]:
        keys = get_record_blocking_keys(query_record)
        seen = set()
        candidates = []

        # Sort candidate hits by frequency of shared blocking keys
        hit_counts = defaultdict(int)
        for k in keys:
            for eid in self.index.get(k, []):
                hit_counts[eid] += 1

        # Sort candidates with most shared blocking keys first
        sorted_eids = sorted(hit_counts.keys(), key=lambda eid: -hit_counts[eid])

        for eid in sorted_eids[:max_candidates]:
            if eid not in seen:
                seen.add(eid)
                candidates.append(self.records[eid])

        return candidates


def generate_candidate_pairs_stats(source1_records: List[Dict], s2_index: BlockingIndex, s3_index: BlockingIndex, max_candidates: int = 20):
    stats = {
        'total_entities': len(source1_records),
        'total_candidates': 0,
        'min_candidates': 999999,
        'max_candidates': 0,
        'candidate_map': {},
    }

    total_cands = 0
    for s1 in source1_records:
        eid = s1['entity_id']
        c2 = [c['entity_id'] for c in s2_index.get_candidates(s1, max_candidates=max_candidates // 2)]
        c3 = [c['entity_id'] for c in s3_index.get_candidates(s1, max_candidates=max_candidates // 2)]
        all_c = list(dict.fromkeys(c2 + c3))  # unique preserving order
        stats['candidate_map'][eid] = all_c
        count = len(all_c)
        total_cands += count
        if count < stats['min_candidates']:
            stats['min_candidates'] = count
        if count > stats['max_candidates']:
            stats['max_candidates'] = count

    if stats['total_entities'] > 0:
        stats['avg_candidates'] = round(total_cands / stats['total_entities'], 2)
        if stats['min_candidates'] == 999999:
            stats['min_candidates'] = 0
    else:
        stats['avg_candidates'] = 0
        stats['min_candidates'] = 0

    stats['total_candidates'] = total_cands
    return stats
