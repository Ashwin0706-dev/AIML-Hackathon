# Amazon ML Challenge 2026 - Business Entity Resolution

This project implements an end-to-end business-entity resolution pipeline for the Amazon ML Challenge 2026 using the real TSV datasets under the project root.

## Project goals

- Inspect and validate the source data
- Normalize business names and addresses
- Generate candidates with blocking logic
- Engineer matching features
- Train an ML model for entity matching
- Tune a decision threshold for F0.5 precision-oriented matching
- Generate final match outputs for all source-1 entities
- Expose a FastAPI backend and a React dashboard for local exploration

## Quick start

1. Create a Python environment and install dependencies:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Run the dataset inspection:
   ```bash
   python scripts/inspect_dataset.py
   ```
3. Train the matching model:
   ```bash
   python scripts/train.py
   ```
4. Generate predictions and validation output:
   ```bash
   python scripts/predict_test.py
   python scripts/validate_submission.py
   ```
5. Start the backend:
   ```bash
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```
6. Start the frontend:
   ```bash
   cd frontend
   npm install
   npm run dev -- --host 0.0.0.0
   ```

## Structure

- `backend/` - FastAPI app, services, and machine learning logic
- `scripts/` - dataset inspection, training, prediction, validation, pipeline entry points
- `frontend/` - React + Vite dashboard
- `utils/` - submission validation utilities

## Notes

- The project uses the real challenge data only.
- Matching is precision-focused because the official metric is F0.5.
- Candidate generation uses a memory-safe, blocking-first approach.
