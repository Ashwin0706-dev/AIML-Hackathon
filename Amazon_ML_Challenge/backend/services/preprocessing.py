from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd


def coerce_string_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in ['entity_id', 'business_name', 'business_address', 'country']:
        if col in df.columns:
            df[col] = df[col].replace({np.nan: None})
            df[col] = df[col].astype('string')
    return df


def fill_missing_fields(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in ['business_name', 'business_address', 'country']:
        if col in df.columns:
            df[col] = df[col].fillna('')
    return df


def sanitize_business_records(df: pd.DataFrame) -> pd.DataFrame:
    df = coerce_string_columns(df)
    df = fill_missing_fields(df)
    df['business_name'] = df['business_name'].astype(str).str.strip()
    df['business_address'] = df['business_address'].astype(str).str.strip()
    df['country'] = df['country'].astype(str).str.strip()
    return df


def ensure_required_columns(df: pd.DataFrame) -> pd.DataFrame:
    required = ['entity_id', 'business_name', 'business_address', 'country']
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f'Missing required columns: {missing}')
    return df


def normalize_country_values(df: pd.DataFrame) -> pd.DataFrame:
    if 'country' in df.columns:
        df['country'] = df['country'].fillna('').astype(str).str.strip()
    return df
