# AMAZON ML CHALLENGE 2026
# BUSINESS ENTITY RESOLUTION
# COMPLETE END-TO-END PROJECT MASTER PROMPT

You are the lead software engineer, ML engineer, data engineer, backend engineer, frontend engineer, and QA engineer for this project.

Your task is to BUILD THE COMPLETE PROJECT, NOT JUST EXPLAIN IT.

The project must become a fully working, evaluator-ready Business Entity Resolution system with:

1. Real dataset processing
2. Data inspection
3. Data preprocessing
4. Entity normalization
5. Candidate generation / blocking
6. Feature engineering
7. Machine learning model training
8. Validation and threshold tuning
9. Test-set inference
10. Required TSV output generation
11. Candidate-pairs generation
12. Official submission validation
13. FastAPI backend
14. Complete React/Vite frontend website
15. Interactive entity matching
16. Candidate explorer
17. Model information
18. Evaluation metrics
19. Final results explorer
20. Downloadable submission files
21. Documentation
22. Robust error handling
23. Large-dataset memory-safe processing
24. Complete local execution
25. No fake data or fake metrics

IMPORTANT:
DO NOT ONLY CREATE A DEMO.
DO NOT CREATE PLACEHOLDER LOGIC.
DO NOT CREATE FAKE ML RESULTS.
DO NOT CREATE SYNTHETIC DATA.
DO NOT PRETEND THAT THE PROJECT IS COMPLETE IF IMPORTANT COMPONENTS ARE MISSING.

The actual TSV files already exist in this project folder.

============================================================
1. PROJECT OBJECTIVE
============================================================

Build a Business Entity Resolution system for the Amazon ML Challenge.

The objective is:

Given business records from multiple independent sources with noisy and inconsistent information, identify which Source 2 and Source 3 records refer to the same real-world business as each Source 1 entity.

Source 1 is the deduplicated reference source.

For every Source 1 entity:

- Find zero, one, or multiple matching Source 2 entities.
- Find zero, one, or multiple matching Source 3 entities.

The system must produce the required final matching output and candidate-pairs output.

The system must prioritize precision because the official evaluation uses F0.5.

False matches are therefore more costly than missing some uncertain matches.

============================================================
2. IMPORTANT DATASET RULE
============================================================

USE ONLY THE REAL DATASET FILES PROVIDED IN THE PROJECT.

DO NOT GENERATE SYNTHETIC DATA.

DO NOT DOWNLOAD DATA FROM THE INTERNET.

DO NOT USE:

- Google
- business directories
- APIs
- government databases
- geocoding services
- external company databases
- external business lookup
- web scraping
- external entity-resolution datasets

The model must learn only from the supplied challenge data.

============================================================
3. DATA FILES
============================================================

The project root contains:

train_source1.tsv
train_source2.tsv
train_source3.tsv
train_ground_truth.tsv

test_source1.tsv
test_source2.tsv
test_source3.tsv

These files are TSV files.

Always read them with:

sep="\t"

Never assume CSV comma separation.

Before building the pipeline, inspect:

- column names
- number of rows
- data types
- missing values
- unique counts
- duplicate counts
- country distribution
- string length distributions
- sample records
- train/test differences

Create a dataset inspection utility.

The system must NEVER blindly load extremely large files into memory if doing so can cause failure.

Use:

- chunked reading
- streaming
- indexed lookup
- compact data structures
- caching
- batching

where appropriate.

============================================================
4. EXPECTED COLUMNS
============================================================

The source files contain:

entity_id
business_name
business_address
country

Ground truth contains:

source1_entity_id
matched_entity_ids

Do not rename these columns unless absolutely necessary internally.

Preserve original IDs in final outputs.

============================================================
5. GROUND TRUTH
============================================================

Training ground truth maps:

source1_entity_id

to:

matched_entity_ids

matched_entity_ids may contain multiple entity IDs.

The system must correctly parse multiple IDs.

It must support:

- one-to-one matches
- one-to-many matches
- zero matches

Do not assume every Source 1 entity has a match.

============================================================
6. OPEN-SET COUNTRY REQUIREMENT
============================================================

DO NOT HARD-CODE THE SYSTEM TO ONLY SUPPORT COUNTRIES PRESENT IN TRAINING.

The test set may contain France or other countries not represented in training.

Country must therefore be treated as a general field.

The system must support unseen countries.

Country can be used as:

- exact comparison feature
- normalization feature
- blocking feature where safe

but it must NOT be used as a hard-coded whitelist.

============================================================
7. REQUIRED PROJECT ARCHITECTURE
============================================================

Create the following structure:

Amazon_ML_Challenge/
│
├── train_source1.tsv
├── train_source2.tsv
├── train_source3.tsv
├── train_ground_truth.tsv
├── test_source1.tsv
├── test_source2.tsv
├── test_source3.tsv
│
├── MASTER_PROMPT.md
├── README.md
├── Documentation_template.md
├── requirements.txt
│
├── backend/
│   ├── main.py
│   ├── config.py
│   │
│   ├── models/
│   │   ├── schemas.py
│   │   └── ...
│   │
│   ├── services/
│   │   ├── data_service.py
│   │   ├── preprocessing.py
│   │   ├── normalization.py
│   │   ├── blocking.py
│   │   ├── feature_service.py
│   │   ├── matching_service.py
│   │   ├── training_service.py
│   │   ├── evaluation_service.py
│   │   ├── prediction_service.py
│   │   └── validation_service.py
│   │
│   ├── ml/
│   │   ├── train_model.py
│   │   ├── evaluate_model.py
│   │   └── predict.py
│   │
│   ├── artifacts/
│   │   ├── model.joblib
│   │   ├── threshold.json
│   │   ├── feature_metadata.json
│   │   └── training_metadata.json
│   │
│   └── outputs/
│       ├── matching_results.tsv
│       └── candidate_pairs.tsv
│
├── scripts/
│   ├── inspect_dataset.py
│   ├── train.py
│   ├── evaluate.py
│   ├── predict_test.py
│   ├── validate_submission.py
│   └── run_pipeline.py
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── api.js
│       │
│       ├── components/
│       │   ├── Sidebar.jsx
│       │   ├── Header.jsx
│       │   ├── MetricCard.jsx
│       │   ├── DataTable.jsx
│       │   ├── MatchBadge.jsx
│       │   ├── SimilarityBar.jsx
│       │   ├── CandidateTable.jsx
│       │   └── Loading.jsx
│       │
│       ├── pages/
│       │   ├── Dashboard.jsx
│       │   ├── EntityMatching.jsx
│       │   ├── CandidateExplorer.jsx
│       │   ├── ModelInsights.jsx
│       │   ├── Validation.jsx
│       │   ├── DataExplorer.jsx
│       │   ├── FinalResults.jsx
│       │   └── Methodology.jsx
│       │
│       └── styles/
│           └── app.css
│
└── utils/
    └── validate_submission.py

If some files already exist, inspect them before replacing them.

Do not unnecessarily duplicate functionality.

============================================================
8. TECHNOLOGY STACK
============================================================

Backend:

- Python 3.10+
- FastAPI
- Uvicorn
- Pandas
- NumPy
- scikit-learn
- RapidFuzz
- joblib
- Pydantic

Frontend:

- React
- Vite
- JavaScript
- CSS

Use simple, stable dependencies.

Do not introduce unnecessary frameworks.

============================================================
9. MACHINE LEARNING PIPELINE
============================================================

Implement a genuine entity-resolution ML pipeline.

Pipeline:

RAW DATA
    ↓
DATA VALIDATION
    ↓
NORMALIZATION
    ↓
BLOCKING / CANDIDATE GENERATION
    ↓
PAIR FEATURE GENERATION
    ↓
MODEL TRAINING
    ↓
VALIDATION
    ↓
THRESHOLD TUNING
    ↓
TEST CANDIDATE GENERATION
    ↓
PAIR SCORING
    ↓
MATCH DECISION
    ↓
FINAL OUTPUT
    ↓
OFFICIAL VALIDATION

============================================================
10. NORMALIZATION
============================================================

Create robust normalization functions.

Business name normalization should handle:

- lowercase
- Unicode normalization
- punctuation removal
- whitespace normalization
- common symbols
- "&" and "and"
- legal suffixes where appropriate
- repeated whitespace
- transliteration where practical without requiring external services

Address normalization should handle:

- lowercase
- punctuation
- whitespace
- common address abbreviations
- common separators
- Unicode normalization
- apartment/unit formatting
- road/street abbreviations where safe

Country normalization should:

- trim whitespace
- lowercase
- normalize common textual variations

Do not destroy useful information.

Keep both:

- original values
- normalized values

============================================================
11. MATCHING FEATURES
============================================================

For each candidate pair, generate meaningful features.

At minimum implement:

Business Name:

- exact normalized match
- token overlap
- Jaccard similarity
- character similarity
- Levenshtein-style similarity
- RapidFuzz ratio
- RapidFuzz partial ratio
- token sort ratio
- token set ratio
- character n-gram similarity where useful

Business Address:

- exact normalized match
- token overlap
- Jaccard similarity
- character similarity
- fuzzy similarity
- token similarity
- length difference

Country:

- exact equality
- normalized equality

Additional:

- name length difference
- address length difference
- token count difference
- missing-value indicators
- combined similarity features

Make the feature-generation system modular.

============================================================
12. TF-IDF
============================================================

Implement TF-IDF cosine similarity where practical.

Because the dataset may be extremely large:

DO NOT build an enormous dense matrix.

Use sparse matrices.

If full TF-IDF is computationally impractical for the entire dataset:

- use it on candidate pairs
- or use a controlled vocabulary
- or use character n-gram TF-IDF
- or use another memory-safe implementation

Document the design decision.

============================================================
13. BLOCKING / CANDIDATE GENERATION
============================================================

Blocking is critical.

Do NOT compare every Source 1 record against every Source 2/Source 3 record.

Implement multiple blocking strategies.

Possible blocks:

1. normalized country
2. first character/token of normalized business name
3. business-name token prefixes
4. address token prefixes
5. postal-code-like fragments where available
6. normalized name n-grams
7. strong fuzzy candidate retrieval

Use multiple blocking strategies and combine candidates.

A record can enter the candidate set through more than one block.

Candidate generation must prioritize recall.

Never make blocking so strict that valid matches disappear unnecessarily.

Track:

- number of Source 1 entities
- candidate count
- average candidates per entity
- minimum candidates
- maximum candidates

============================================================
14. SOURCE 2 AND SOURCE 3
============================================================

Treat Source 2 and Source 3 independently.

For each Source 1 entity:

Generate candidates from Source 2.

Generate candidates from Source 3.

Score each candidate.

Do not mix Source 2 IDs and Source 3 IDs incorrectly.

The final matching_results.tsv must contain all matching entity IDs required by the challenge format.

============================================================
15. TRAINING PAIRS
============================================================

Construct positive and negative training pairs.

Positive pairs:

Use train_ground_truth.tsv.

For each Source 1 entity, create positive pairs for its true matched Source 2/Source 3 records.

Negative pairs:

Sample candidates that are not ground-truth matches.

Do not randomly sample impossible pairs only.

Prefer hard negatives:

- same country
- similar business names
- similar addresses
- same blocking group
- high fuzzy similarity but incorrect

Hard negatives are important for precision.

Avoid overwhelming the training set with trivial negatives.

============================================================
16. MODEL
============================================================

Use a strong but practical model.

Preferred first model:

HistGradientBoostingClassifier

or:

RandomForestClassifier

or:

LogisticRegression

Choose based on actual dataset size and feature behavior.

The final model must be:

- <= 8B parameters
- MIT or Apache 2.0 compatible
- practical to run locally

Do not use an unnecessarily large language model.

Save the trained model using joblib.

Save:

model.joblib
threshold.json
feature_metadata.json
training_metadata.json

============================================================
17. TRAINING / VALIDATION SPLIT
============================================================

Avoid leakage.

Where practical, split by Source 1 entity.

Do not randomly split individual candidate pairs if this causes the same Source 1 entity to appear in both training and validation.

Training data should remain isolated from validation data.

Tune the final matching threshold using validation data only.

Do not use the official test set to tune the threshold.

============================================================
18. EVALUATION
============================================================

The challenge uses F0.5.

Formula:

F0.5 = (1.25 * Precision * Recall)
       / (0.25 * Precision + Recall)

Precision is more important than recall.

Calculate:

- precision
- recall
- F0.5
- TP
- FP
- FN
- number of entities evaluated
- number of predicted matches
- number of true matches

Also calculate per-Source-1 metrics where possible.

Singleton entities must be handled correctly.

If the correct prediction is empty:

score should reflect a correct no-match decision.

Do not assume every entity has a match.

============================================================
19. THRESHOLD OPTIMIZATION
============================================================

Do not blindly use threshold = 0.5.

Evaluate multiple thresholds.

For example:

0.30
0.35
0.40
0.45
0.50
0.55
0.60
0.65
0.70
0.75
0.80
0.85
0.90
0.95

Select the threshold that gives the best validation F0.5.

Because this is precision-oriented, avoid aggressive low thresholds.

Store the selected threshold in:

backend/artifacts/threshold.json

Display it in the website.

============================================================
20. MATCH DECISION
============================================================

For each candidate pair:

Generate probability.

Then apply threshold.

However, implement safeguards against obvious false matches.

For example:

- very low name similarity
- very low address similarity
- conflicting country where country is reliable

Do not blindly override the model.

Any heuristic must be validated and documented.

============================================================
21. MULTIPLE MATCHES
============================================================

A Source 1 entity can have multiple true matches.

Therefore:

DO NOT force one-to-one matching.

Allow:

zero matches
one match
multiple matches

The final prediction must contain all candidates whose final decision passes the matching logic.

============================================================
22. CANDIDATE OUTPUT
============================================================

Create:

candidate_pairs.tsv

Required conceptual columns:

source1_entity_id
candidate_entity_ids

Each Source 1 entity must appear exactly once.

candidate_entity_ids should contain the IDs considered as candidates.

Final matched IDs must ALWAYS be a subset of candidate IDs.

Never output a final match that was not present in candidate_pairs.tsv.

============================================================
23. FINAL OUTPUT
============================================================

Create:

matching_results.tsv

Required columns:

source1_entity_id
matched_entity_ids

Rules:

- one row per test Source 1 entity
- every test Source 1 entity must appear exactly once
- matched_entity_ids is comma-separated if multiple
- empty if there are no matches
- only valid Source 2/Source 3 IDs
- no Source 1 IDs
- no duplicate IDs inside a row
- no invalid IDs
- no missing Source 1 test entities

Use:

sep="\t"

============================================================
24. OFFICIAL VALIDATION
============================================================

Use the supplied:

utils/validate_submission.py

if available.

The system must validate:

1. matching_results.tsv exists
2. candidate_pairs.tsv exists
3. columns are correct
4. TSV format is correct
5. every test Source 1 entity appears exactly once
6. no duplicate Source 1 entities
7. matched IDs are valid
8. candidate IDs are valid
9. final matches are a subset of candidate IDs
10. no Source 1 IDs appear as matches
11. no malformed rows
12. empty matches are represented correctly

Create a script:

python scripts/validate_submission.py

that runs the official validation logic where possible.

============================================================
25. LARGE DATASET HANDLING
============================================================

This is a very important requirement.

The real dataset can be very large.

DO NOT write code that blindly executes:

pd.read_csv("huge_file.tsv")

for every file and stores everything in RAM.

Instead design a memory-safe system.

Use:

- chunksize
- indexing
- precomputed normalized columns where practical
- dictionaries for compact indexes
- batching
- candidate retrieval
- caching
- parquet or pickle cache only if useful
- incremental processing

Do not create huge unnecessary intermediate files.

The pipeline must be restartable.

If a long-running step fails, it should be possible to resume where practical.

============================================================
26. PIPELINE COMMAND
============================================================

Create one command that runs the complete ML pipeline.

Example:

python scripts/run_pipeline.py

It should:

1. inspect dataset
2. prepare data
3. generate training pairs
4. train model
5. evaluate model
6. tune threshold
7. process test data
8. generate candidates
9. score candidates
10. generate matching_results.tsv
11. generate candidate_pairs.tsv
12. validate outputs

Do not fake completion.

Print clear progress messages.

============================================================
27. FASTAPI BACKEND
============================================================

Create a FastAPI backend.

Run using:

uvicorn backend.main:app --reload

Backend must expose:

GET /api/health

GET /api/stats

GET /api/data/source1

GET /api/data/source2

GET /api/data/source3

GET /api/entity/{entity_id}

GET /api/entity/{entity_id}/matches

GET /api/entity/{entity_id}/candidates

GET /api/model/info

GET /api/evaluation

GET /api/results

GET /api/download/matching-results

GET /api/download/candidate-pairs

POST /api/train

POST /api/predict

GET /api/validation

============================================================
28. API DESIGN
============================================================

/api/health

Return:

status
backend
model_loaded
dataset_available

/api/stats

Return real values:

source1_count
source2_count
source3_count
train_count
test_count
candidate_count
prediction_count
model_status
threshold

/api/entity/{entity_id}

Return:

entity_id
business_name
business_address
country
source

/api/entity/{entity_id}/matches

Return ranked candidate matches including:

candidate_id
candidate_source
business_name
business_address
country
probability
decision
name_similarity
address_similarity
country_match

/api/entity/{entity_id}/candidates

Return candidate list before final matching.

/api/model/info

Return:

model name
features
training timestamp
threshold
training pair count
validation pair count
model path

/api/evaluation

Return:

precision
recall
F0.5
TP
FP
FN
threshold
validation entity count

/api/results

Return summary and paginated results.

============================================================
29. API PAGINATION
============================================================

Do not return millions of rows in one API call.

Implement:

page
page_size

for large result tables.

Default page size:

25 or 50.

Maximum:

100 or 200.

============================================================
30. REACT WEBSITE
============================================================

Create a professional ML/data-science dashboard.

Use React + Vite.

The website must actually connect to FastAPI.

NO STATIC FAKE VALUES.

Every metric displayed must come from backend APIs or actual generated artifacts.

============================================================
31. SIDEBAR
============================================================

Create sidebar navigation:

Dashboard
Entity Matching
Candidate Explorer
Model Insights
Validation
Data Explorer
Final Results
Methodology

Use clean icons if a lightweight icon library is installed.

Do not add unnecessary dependencies.

============================================================
32. DASHBOARD PAGE
============================================================

Dashboard should show:

- Source 1 record count
- Source 2 record count
- Source 3 record count
- Training records
- Test records
- Candidate count
- Predicted match count
- Validation Precision
- Validation Recall
- Validation F0.5
- Current threshold
- Model status

Also show a pipeline visualization:

Data
↓
Normalization
↓
Blocking
↓
Features
↓
ML Model
↓
Matching
↓
Validation
↓
Submission

Add a recent system status section.

All values must be real.

============================================================
33. ENTITY MATCHING PAGE
============================================================

This is one of the most important pages.

Allow user to enter:

Source 1 Entity ID

Then click:

Find Matches

Display:

SOURCE 1 ENTITY

Business Name
Address
Country

Then:

CANDIDATE MATCHES

For each candidate:

Candidate ID
Source
Business Name
Address
Country
Probability
Decision
Name Similarity
Address Similarity
Country Match

Use badges:

MATCH
REJECT

Use progress bars for similarities.

Sort candidates by probability descending.

============================================================
34. CANDIDATE EXPLORER
============================================================

Allow search by:

Source 1 Entity ID

Display:

candidate count
candidate IDs
candidate source
similarity values
model probability
final decision

Make it easy to understand why a candidate was selected.

============================================================
35. MODEL INSIGHTS
============================================================

Display:

Model name
Feature count
Training pair count
Validation pair count
Threshold
Training status

Display feature importance if supported.

For tree models:

show feature importance.

For Logistic Regression:

show coefficient magnitude.

Also explain the feature categories:

Name
Address
Country
String similarity
Length
Token features

Do not claim feature importance if the model does not support it.

============================================================
36. VALIDATION PAGE
============================================================

Display actual validation metrics.

Cards:

Precision
Recall
F0.5
TP
FP
FN

Display threshold comparison table.

Example:

Threshold | Precision | Recall | F0.5

Use real calculated values.

Highlight the selected threshold.

Do not fabricate metrics.

============================================================
37. DATA EXPLORER
============================================================

Allow viewing sample rows from:

Source 1
Source 2
Source 3
Ground Truth

Add:

- search
- pagination
- country filter where practical

Do not load the entire dataset into browser memory.

============================================================
38. FINAL RESULTS PAGE
============================================================

Display:

matching_results.tsv summary

candidate_pairs.tsv summary

Show:

Total Source 1 entities
Entities with matches
Entities without matches
Total matched IDs
Total candidate IDs

Provide buttons:

Download matching_results.tsv

Download candidate_pairs.tsv

Also show a paginated table:

Source 1 ID
Matched Entity IDs

============================================================
39. METHODOLOGY PAGE
============================================================

Explain the actual implementation:

1. Problem
2. Data
3. Preprocessing
4. Normalization
5. Blocking
6. Candidate generation
7. Feature engineering
8. Model
9. Validation
10. Threshold tuning
11. Final prediction
12. Output validation

Use diagrams/cards where useful.

Do not claim methods that were not implemented.

============================================================
40. FRONTEND DESIGN
============================================================

Design should look like a professional ML analytics application.

Requirements:

- responsive
- clean sidebar
- top header
- cards
- tables
- badges
- progress bars
- charts only where useful
- loading states
- error states
- empty states
- success messages
- dark/light friendly styling

Do not overdesign.

Prioritize functionality.

============================================================
41. FRONTEND API CONFIGURATION
============================================================

Use a centralized API base URL.

Example:

http://localhost:8000

Do not hard-code the same URL in every component.

Create:

frontend/src/api.js

All API calls should go through this file.

============================================================
42. ERROR HANDLING
============================================================

Backend:

- proper HTTP status codes
- meaningful error messages
- logging
- validation

Frontend:

- loading indicators
- API failure messages
- empty states
- retry buttons where appropriate

Do not allow the UI to silently fail.

============================================================
43. TRAIN BUTTON
============================================================

Model Insights page should optionally contain:

Train Model

button.

When clicked:

POST /api/train

Show:

Training started
Training progress/status
Training completed
Validation metrics

Do not allow multiple training jobs simultaneously.

If training is expensive, return a job/status mechanism instead of freezing the API.

============================================================
44. PREDICT BUTTON
============================================================

Provide:

Generate Test Predictions

button.

It should trigger:

POST /api/predict

Then generate:

matching_results.tsv
candidate_pairs.tsv

Show progress/status.

============================================================
45. FILE DOWNLOADS
============================================================

The backend must allow direct download of:

matching_results.tsv

candidate_pairs.tsv

The frontend must provide download buttons.

============================================================
46. CACHING
============================================================

If useful, cache:

- normalized datasets
- indexes
- model artifacts
- feature metadata
- candidate indexes

Do not cache stale results without detecting dataset changes.

Document cache behavior.

============================================================
47. LOGGING
============================================================

Use Python logging.

Log:

- dataset loading
- chunk progress
- normalization
- candidate generation
- training
- validation
- prediction
- output generation
- errors

Do not print millions of lines.

Use periodic progress messages.

============================================================
48. DATA VALIDATION
============================================================

Before training:

Verify required columns exist.

Check:

- missing IDs
- duplicate IDs
- invalid ground truth references
- malformed rows
- unexpected columns

Do not silently ignore serious data problems.

============================================================
49. TESTING
============================================================

Create tests for:

Normalization
Feature generation
Blocking
Ground truth parsing
Candidate subset rule
Output generation
Prediction logic
API health
API entity lookup
Validation

Use pytest.

Create:

tests/

with meaningful tests.

Tests must not require the entire huge dataset.

Use small fixtures extracted from real schema/data when appropriate.

DO NOT generate fake business data merely to demonstrate the website.

============================================================
50. PERFORMANCE
============================================================

The system should be optimized for large datasets.

Avoid:

O(N × M)

full pairwise comparison between all Source 1 and Source 2/3 records.

Use blocking.

Avoid:

nested Python loops over millions of rows where vectorized/indexed alternatives exist.

Use:

- pandas vectorization
- RapidFuzz
- dictionaries
- indexes
- batching
- multiprocessing only where safe and useful

Do not introduce complex distributed infrastructure unless actually required.

============================================================
51. REPRODUCIBILITY
============================================================

Use fixed random seeds where randomness is involved.

Save:

training configuration
threshold
feature names
model type
sample sizes
random seed

Create:

config.py

or equivalent configuration system.

============================================================
52. DOCUMENTATION
============================================================

Create README.md containing:

Project overview
Problem statement
Architecture
Folder structure
Dataset setup
Installation
Backend setup
Frontend setup
Training
Evaluation
Prediction
Validation
Output format
API documentation
Website usage
Troubleshooting

Also create:

Documentation_template.md

containing:

Title
Abstract
Problem Statement
Dataset
Methodology
Architecture
Preprocessing
Blocking
Feature Engineering
Machine Learning
Evaluation
Results
Frontend
Backend
Output Files
Limitations
Future Improvements
Conclusion

Only write claims supported by actual implementation/results.

============================================================
53. REQUIREMENTS.TXT
============================================================

Generate an accurate requirements.txt.

Include only packages actually used.

At minimum consider:

fastapi
uvicorn
pandas
numpy
scikit-learn
rapidfuzz
joblib
pydantic
python-multipart
pytest

Add other packages only if required.

============================================================
54. PACKAGE.JSON
============================================================

Create a valid React/Vite package.json.

Use only necessary dependencies.

============================================================
55. SECURITY / SAFETY
============================================================

Do not execute arbitrary uploaded commands.

Do not expose filesystem paths unnecessarily through APIs.

Do not allow arbitrary file paths from frontend requests.

Validate entity IDs and parameters.

============================================================
56. NO FAKE CONTENT
============================================================

This is extremely important.

NEVER write:

"F0.5 = 0.92"

unless the system actually calculated 0.92.

NEVER write:

"10 million matches"

unless the dataset actually contains that number.

NEVER use placeholder dashboard metrics.

NEVER use fake candidate records.

NEVER use fake business names.

NEVER create synthetic TSV files to make the UI look populated.

The UI must reflect actual backend data.

If data has not yet been processed, display:

"Not available yet"

or:

"Run pipeline"

instead of fake values.

============================================================
57. ACTUAL DATASET FIRST
============================================================

Before implementing complicated ML logic:

1. Inspect the actual seven TSV files.
2. Determine their actual sizes.
3. Determine their actual columns.
4. Determine missingness.
5. Determine ID formats.
6. Determine country distribution.
7. Determine ground truth format.
8. Determine whether Source 2 and Source 3 IDs overlap.
9. Determine actual memory requirements.

Then adapt the implementation accordingly.

DO NOT assume dataset characteristics without checking.

============================================================
58. DEVELOPMENT ORDER
============================================================

Build in this order:

PHASE 1
Dataset inspection

PHASE 2
Project architecture

PHASE 3
Normalization

PHASE 4
Blocking

PHASE 5
Training pair generation

PHASE 6
Feature engineering

PHASE 7
Model training

PHASE 8
Validation and threshold tuning

PHASE 9
Test prediction

PHASE 10
Output validation

PHASE 11
FastAPI backend

PHASE 12
React frontend

PHASE 13
Integration

PHASE 14
Testing

PHASE 15
Performance optimization

PHASE 16
Documentation

============================================================
59. IMPORTANT AGENT BEHAVIOR
============================================================

You are working directly inside the project repository.

DO NOT merely tell me what code I should write.

CREATE THE FILES.

EDIT THE FILES.

RUN THE COMMANDS.

FIX ERRORS.

TEST THE APPLICATION.

If a dependency is missing:

install or clearly provide the exact installation command.

If code fails:

diagnose it and fix it.

If an assumption about the dataset is wrong:

inspect the real data and adapt.

Do not stop after generating a skeleton.

Continue until the application can actually run.

============================================================
60. FIRST ACTION
============================================================

Before creating the full implementation:

1. Inspect the repository.
2. Confirm the seven TSV files exist.
3. Inspect their schemas.
4. Inspect representative rows.
5. Measure file sizes.
6. Determine whether they can be processed normally or require chunking.
7. Inspect train_ground_truth.tsv carefully.
8. Inspect whether any official validator already exists.
9. Create a short internal implementation plan based on the REAL dataset.

Then start implementing.

Do not ask me to create synthetic data.

Do not ask me to download another dataset.

============================================================
61. REQUIRED RUNNING COMMANDS
============================================================

After implementation, ensure these commands are available.

Backend:

pip install -r requirements.txt

uvicorn backend.main:app --reload

Frontend:

cd frontend
npm install
npm run dev

Training:

python scripts/train.py

Evaluation:

python scripts/evaluate.py

Prediction:

python scripts/predict_test.py

Full pipeline:

python scripts/run_pipeline.py

Validation:

python scripts/validate_submission.py

Testing:

pytest

============================================================
62. FINAL ACCEPTANCE CHECKLIST
============================================================

Do not consider the project complete until the following are true:

[ ] Real seven TSV files detected
[ ] Dataset schema inspected
[ ] Large-file handling implemented
[ ] Normalization implemented
[ ] Blocking implemented
[ ] Candidate generation implemented
[ ] Positive training pairs implemented
[ ] Hard-negative sampling implemented
[ ] Features implemented
[ ] ML model trained
[ ] Validation performed
[ ] F0.5 calculated
[ ] Threshold tuned
[ ] Model artifact saved
[ ] Test prediction implemented
[ ] candidate_pairs.tsv generated
[ ] matching_results.tsv generated
[ ] Output validation implemented
[ ] FastAPI runs
[ ] All required APIs work
[ ] React frontend runs
[ ] Dashboard uses real values
[ ] Entity matching works
[ ] Candidate explorer works
[ ] Model insights works
[ ] Validation page works
[ ] Data explorer works
[ ] Final results works
[ ] Downloads work
[ ] Error handling works
[ ] Tests pass
[ ] README created
[ ] Documentation created
[ ] No fake data
[ ] No fake metrics
[ ] No external business data
[ ] No synthetic dataset
[ ] No hard-coded country limitation
[ ] Final matches are subset of candidates
[ ] Every test Source 1 entity appears exactly once
[ ] Submission files are valid TSV

============================================================
63. FINAL WEBSITE EXPERIENCE
============================================================

The final website should allow an evaluator to:

1. Open Dashboard
2. See actual dataset statistics
3. Navigate to Entity Matching
4. Enter a real Source 1 entity ID
5. View its real candidate records
6. See similarity features
7. See model probability
8. See match/reject decision
9. Open Candidate Explorer
10. Inspect candidate generation
11. Open Model Insights
12. See actual model information
13. Open Validation
14. See actual Precision, Recall and F0.5
15. Open Data Explorer
16. Inspect real records
17. Open Final Results
18. Browse actual predictions
19. Download matching_results.tsv
20. Download candidate_pairs.tsv
21. Open Methodology
22. Understand the complete pipeline

Everything shown must be backed by the real implementation.

============================================================
64. IMPORTANT FINAL INSTRUCTION
============================================================

BUILD THIS PROJECT END-TO-END.

Do not stop at a prototype.

Do not stop after frontend creation.

Do not stop after model training.

Do not stop after API creation.

Integrate all components.

The final system must be:

REAL DATA
+
REAL ML
+
REAL CANDIDATE GENERATION
+
REAL VALIDATION
+
REAL OUTPUT FILES
+
REAL FASTAPI
+
REAL REACT WEBSITE
+
REAL TESTING
+
REAL DOCUMENTATION

The final goal is a complete, locally runnable, challenge-ready Business Entity Resolution application.

Start by inspecting the actual dataset and then implement the project.