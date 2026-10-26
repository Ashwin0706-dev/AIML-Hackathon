# Project Documentation

## Dataset overview

The training and test files are stored as tab-separated values with the following required columns:

- `entity_id`
- `business_name`
- `business_address`
- `country`

The `train_ground_truth.tsv` file maps `source1_entity_id` to a comma-separated list of matched target entity IDs.

## Matching pipeline

1. Load and validate TSVs with `sep='\t'`
2. Normalize names and addresses
3. Generate candidate pairs using blocking rules
4. Compute pairwise matching features
5. Train a logistic regression model on labeled candidate pairs
6. Tune threshold to favor precision
7. Apply model to test candidates and write required output files

## Data quality safeguards

- Nulls are treated explicitly instead of silently converting to strings
- Chunked data operations are used where practical
- Blocking is intentionally limited to keep memory usage manageable
- Country fields are treated as general features rather than as a hard-coded whitelist

## Validation

The validation service checks that final outputs contain the required columns and that no malformed IDs or duplicate rows are produced.
