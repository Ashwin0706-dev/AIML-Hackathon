from __future__ import annotations

import re
import unicodedata


def unicode_nfkc(value: str) -> str:
    if value is None:
        return ''
    return unicodedata.normalize('NFKC', str(value))


def normalize_text(value: str, lowercase: bool = True) -> str:
    text = unicode_nfkc(value or '')
    text = text.replace('&', ' and ')
    text = text.replace(' + ', ' and ')
    text = text.replace('’', "'")
    text = text.replace('–', '-')
    text = text.replace('—', '-')
    text = re.sub(r'[^\w\s\-\./,]', ' ', text, flags=re.UNICODE)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    if lowercase:
        text = text.lower()
    return text


def normalize_business_name(value: str) -> str:
    text = normalize_text(value)
    text = re.sub(r'\b(inc|incorporated|llc|ltd|limited|corp|corporation|company|co|sa|sas|sarl|gmbh|pvt|private|ltd\.?|plc|bv)\b', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def normalize_business_address(value: str) -> str:
    text = normalize_text(value)
    replacements = {
        'street': 'st',
        'st.': 'st',
        'road': 'rd',
        'rd.': 'rd',
        'avenue': 'ave',
        'ave.': 'ave',
        'boulevard': 'blvd',
        'blvd.': 'blvd',
        'lane': 'ln',
        'ln.': 'ln',
        'drive': 'dr',
        'dr.': 'dr',
        'court': 'ct',
        'ct.': 'ct',
        'apartment': 'apt',
        'apt.': 'apt',
        'unit': 'unit',
        'suite': 'ste',
        'ste.': 'ste',
        'no.': 'no',
        'nº': 'no',
    }
    for src, dst in replacements.items():
        text = re.sub(rf'\b{src}\b', dst, text)
    text = re.sub(r'[^\w\s\-/,]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def normalize_country(value: str) -> str:
    return normalize_text(value, lowercase=True)


def make_name_tokens(value: str):
    normalized = normalize_business_name(value)
    if not normalized:
        return []
    return [token for token in normalized.split() if token]


def make_address_tokens(value: str):
    normalized = normalize_business_address(value)
    if not normalized:
        return []
    return [token for token in normalized.split() if token]
