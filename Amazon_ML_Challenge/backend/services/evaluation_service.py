from __future__ import annotations

from typing import List, Tuple

import numpy as np


def compute_precision_recall_f05(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)

    tp = np.sum((y_pred == 1) & (y_true == 1))
    fp = np.sum((y_pred == 1) & (y_true == 0))
    fn = np.sum((y_pred == 0) & (y_true == 1))

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f05 = (1.25 * precision * recall) / (0.25 * precision + recall) if (precision + recall) else 0.0
    return {
        'precision': float(precision),
        'recall': float(recall),
        'f05': float(f05),
        'tp': int(tp),
        'fp': int(fp),
        'fn': int(fn),
    }


def evaluate_model(model, X_test, y_test):
    probabilities = model.predict_proba(X_test)[:, 1]
    preds = (probabilities >= 0.5).astype(int)
    return compute_precision_recall_f05(y_test, preds)
