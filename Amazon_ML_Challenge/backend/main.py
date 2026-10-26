from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from backend.config import (
    ARTIFACTS_DIR,
    FEATURE_METADATA_PATH,
    MODEL_PATH,
    OUTPUTS_DIR,
    PROJECT_ROOT,
    THRESHOLD_PATH,
    TRAINING_METADATA_PATH,
)
from backend.services.data_service import (
    find_matches_for_entity,
    get_all_dataset_summaries,
    get_entity_by_id,
    get_paginated_records,
    get_system_stats,
    inspect_dataset,
)
from backend.services.validation_service import validate_submission_files

app = FastAPI(
    title="Amazon ML Challenge - Business Entity Resolution API",
    description="Real dataset processing, candidate blocking, HistGradientBoosting scoring, and F0.5 optimization",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Training lock to prevent concurrent runs
is_training = False
is_predicting = False


# ============================================================
# API ENDPOINTS (As specified in file.md Section 27)
# ============================================================

@app.get("/api/health")
@app.get("/health")
def api_health():
    return {
        "status": "ok",
        "backend": "FastAPI",
        "model_loaded": MODEL_PATH.exists(),
        "dataset_available": True,
        "project_root": str(PROJECT_ROOT),
    }


@app.get("/api/stats")
def api_stats():
    return get_system_stats()


@app.get("/api/data/{source_name}")
def api_data_source(
    source_name: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    query: str = Query("", description="Search term for name or ID"),
    country: str = Query("", description="Country filter"),
):
    valid_sources = ["source1", "source2", "source3", "ground_truth"]
    if source_name not in valid_sources:
        raise HTTPException(status_code=400, detail=f"Invalid source '{source_name}'. Valid: {valid_sources}")
    return get_paginated_records(source_name, page=page, page_size=page_size, query=query, country=country)


@app.get("/api/entity/{entity_id}")
def api_entity_details(entity_id: str):
    entity = get_entity_by_id(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity '{entity_id}' not found")
    return entity


@app.get("/api/entity/{entity_id}/matches")
def api_entity_matches(entity_id: str):
    result = find_matches_for_entity(entity_id)
    if not result.get("found"):
        raise HTTPException(status_code=404, detail=result.get("message", "Entity not found"))
    return result


@app.get("/api/entity/{entity_id}/candidates")
def api_entity_candidates(entity_id: str):
    result = find_matches_for_entity(entity_id)
    if not result.get("found"):
        raise HTTPException(status_code=404, detail=result.get("message", "Entity not found"))
    return {
        "entity_id": entity_id,
        "source_entity": result.get("source_entity"),
        "candidate_count": result.get("candidates_count"),
        "candidates": result.get("candidates"),
    }


@app.get("/api/model/info")
@app.get("/model-info")
def api_model_info():
    info = {
        "model_exists": MODEL_PATH.exists(),
        "model_path": str(MODEL_PATH) if MODEL_PATH.exists() else None,
        "outputs_dir": str(OUTPUTS_DIR),
    }

    if TRAINING_METADATA_PATH.exists():
        try:
            t_meta = json.loads(TRAINING_METADATA_PATH.read_text())
            info["training_metadata"] = t_meta
            info["model_type"] = t_meta.get("model_type", "HistGradientBoostingClassifier")
            info["threshold"] = t_meta.get("best_threshold", 0.50)
            info["trained_at"] = t_meta.get("trained_at")
        except Exception:
            pass

    if FEATURE_METADATA_PATH.exists():
        try:
            f_meta = json.loads(FEATURE_METADATA_PATH.read_text())
            info["feature_metadata"] = f_meta
            info["features"] = f_meta.get("feature_names", [])
            info["feature_importances"] = f_meta.get("feature_importances", {})
            info["train_samples"] = f_meta.get("train_samples", 0)
            info["val_samples"] = f_meta.get("val_samples", 0)
        except Exception:
            pass

    return info


@app.get("/api/evaluation")
def api_evaluation():
    eval_path = ARTIFACTS_DIR / "evaluation.json"
    if eval_path.exists():
        try:
            return json.loads(eval_path.read_text())
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading evaluation data: {e}")
    raise HTTPException(status_code=404, detail="Evaluation results not yet generated. Please train the model.")


@app.get("/api/results")
@app.get("/final-results")
def api_results(page: int = Query(1, ge=1), page_size: int = Query(25, ge=1, le=100)):
    match_path = OUTPUTS_DIR / "matching_results.tsv"
    cand_path = OUTPUTS_DIR / "candidate_pairs.tsv"

    if not match_path.exists():
        return {
            "exists": False,
            "message": "No submission results generated yet. Please run test prediction.",
        }

    validation_report = validate_submission_files(OUTPUTS_DIR)

    # Read paginated slice from matching_results.tsv
    import pandas as pd
    offset = (page - 1) * page_size
    df = pd.read_csv(match_path, sep="\t", dtype=str).fillna("")
    total = len(df)
    slice_df = df.iloc[offset : offset + page_size]

    return {
        "exists": True,
        "matching_path": str(match_path),
        "candidate_path": str(cand_path),
        "validation": validation_report,
        "metrics": validation_report.get("metrics", {}),
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 1,
        "items": slice_df.to_dict(orient="records"),
    }


@app.get("/api/candidate-pairs")
@app.get("/candidate-pairs")
def api_candidate_pairs(page: int = Query(1, ge=1), page_size: int = Query(25, ge=1, le=100)):
    cand_path = OUTPUTS_DIR / "candidate_pairs.tsv"
    if not cand_path.exists():
        return {"exists": False, "message": "No candidate-pairs generated yet."}

    import pandas as pd
    offset = (page - 1) * page_size
    df = pd.read_csv(cand_path, sep="\t", dtype=str).fillna("")
    total = len(df)
    slice_df = df.iloc[offset : offset + page_size]

    return {
        "exists": True,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 1,
        "items": slice_df.to_dict(orient="records"),
    }


@app.get("/api/download/matching-results")
def api_download_matching():
    path = OUTPUTS_DIR / "matching_results.tsv"
    if not path.exists():
        raise HTTPException(status_code=404, detail="matching_results.tsv not found.")
    return FileResponse(path, media_type="text/tab-separated-values", filename="matching_results.tsv")


@app.get("/api/download/candidate-pairs")
def api_download_candidates():
    path = OUTPUTS_DIR / "candidate_pairs.tsv"
    if not path.exists():
        raise HTTPException(status_code=404, detail="candidate_pairs.tsv not found.")
    return FileResponse(path, media_type="text/tab-separated-values", filename="candidate_pairs.tsv")


@app.get("/api/validation")
def api_validation():
    return validate_submission_files(OUTPUTS_DIR)


@app.get("/dataset-summary")
def legacy_dataset_summary():
    # Return precomputed lightning fast summary
    return get_all_dataset_summaries()


# ============================================================
# TRAINING & PREDICTION TRIGGERS
# ============================================================

def _background_train():
    global is_training
    try:
        from backend.ml.train_model import run_training_pipeline
        run_training_pipeline(max_gt_rows=3000)
    finally:
        is_training = False


def _background_predict():
    global is_predicting
    try:
        from backend.ml.predict import predict_test_set
        predict_test_set(sample_size=5000)
    finally:
        is_predicting = False


@app.post("/api/train")
def api_trigger_train(background_tasks: BackgroundTasks):
    global is_training
    if is_training:
        return {"status": "in_progress", "message": "Training is already running in background."}
    is_training = True
    background_tasks.add_task(_background_train)
    return {"status": "started", "message": "Model training started in background."}


@app.post("/api/predict")
def api_trigger_predict(background_tasks: BackgroundTasks):
    global is_predicting
    if is_predicting:
        return {"status": "in_progress", "message": "Prediction is already running in background."}
    is_predicting = True
    background_tasks.add_task(_background_predict)
    return {"status": "started", "message": "Test set candidate generation and inference started."}
