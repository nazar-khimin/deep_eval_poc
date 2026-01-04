# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a proof-of-concept repository for testing DeepEval, a framework for evaluating LLM outputs. The project uses DeepEval's metrics to assess the quality and relevance of AI-generated responses.

## Development Setup

```bash
# Install dependencies using Poetry
poetry install

# Activate the virtual environment
poetry shell

# Create .env file from example and add your API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

**Environment Variables:**
- Copy `.env.example` to `.env`
- Add your `OPENAI_API_KEY` (required for DeepEval metrics)
- Environment variables are loaded automatically via `python-dotenv`

## Running Tests

```bash
# Run all tests directly
poetry run python main.py

# Run tests with pytest
poetry run pytest main.py -v

# Run a specific test function
poetry run pytest main.py::test_answer_relevancy -v
```

## Architecture

The project structure:

- **Constants Management** (`src/constants.py`): Centralized environment configuration
  - Uses frozen dataclasses for immutable constants
  - Automatically loads from `.env` file via `python-dotenv`
  - Singleton instance `const` provides access to configuration
  - Example usage: `from src.constants import const` then access `const.OPENAI_API_KEY`

- **Test Structure**: Tests use `LLMTestCase` objects that contain:
  - `input`: The query or prompt sent to the LLM
  - `actual_output`: The LLM's response
  - `retrieval_context`: Supporting context used for evaluation

- **Metrics**: Currently uses `AnswerRelevancyMetric` which evaluates whether an LLM's output is relevant to the input query. Each metric has a configurable `threshold` (0.0 to 1.0) that determines pass/fail criteria.

- **Assertion Pattern**: Tests use `assert_test(test_case, [metrics])` to validate LLM outputs against defined metrics.

## Migration Pilot

The `migration_pilot/` package validates whether DeepEval can replicate the evaluation logic from the auto-scan backend's custom LLM judge.

### Purpose

- **Goal**: Determine if DeepEval's custom GEval metrics can achieve the same evaluation results as the existing custom LLM judge
- **Approach**: Load real backend test data, evaluate with DeepEval, compare results side-by-side
- **Output**: Comprehensive reports showing agreement rates and disagreements

### Structure

```
migration_pilot/
├── data_adapter.py           # Loads backend JSON files (golden, RAG, evaluations)
├── deepeval_metrics.py       # Custom GEval metrics matching 4 backend boolean indicators
├── comparison.py             # Comparison logic and report generation
├── run_pilot.py              # Main execution script
└── README.md                 # Detailed usage guide
```

### Custom GEval Metrics

Four metrics replicate the backend's evaluation criteria:

1. **`is_question_answered`**: Determines if the answer addresses all significant parts of the question
   - Handles multi-part questions (all parts must be addressed)
   - Special case: "Document does not provide X but specifies Y" = answered

2. **`requires_additional_information`**: Detects if answer explicitly requests more info from the user
   - True only if answer asks user for details ("please provide", "I need", etc.)
   - False if answer simply states information is not in document

3. **`is_speculative`**: Identifies hypothetical or inferential language
   - True if uses hedging words: "might", "could", "seems", "possibly", "probably"
   - False if strictly reports facts or states document lacks information

4. **`is_confident`**: Analyzes if answer is phrased assertively
   - True if direct/assertive: "Yes, X is...", "The document states..."
   - False if uncertain/hedging: "It seems like", "I think", "maybe"

**Composite Metric**: `comprehensive_answer`
```python
comprehensive_answer = (
    is_question_answered AND
    NOT requires_additional_information AND
    NOT is_speculative AND
    is_confident
)
```

### Running the Pilot

```bash
poetry run python migration_pilot/run_pilot.py \
    --test-dir /path/to/auto-scan-backend/tests/ai_chat_evaluation_tests/test_output/1764025492 \
    --limit 10 \
    --threshold 0.5
```

**Arguments:**
- `--test-dir`: Path to backend test_output/<timestamp>/ directory (required)
- `--limit`: Number of test cases to evaluate (default: all)
- `--threshold`: Metric threshold for True/False (default: 0.5)
- `--output-dir`: Output directory (default: migration_pilot/output)

### Output Files

1. **Console**: Real-time progress and summary statistics
2. **JSON** (`deepeval_results_<timestamp>.json`): Raw evaluation results
3. **JSON** (`comparison_<timestamp>.json`): Comparison statistics
4. **Markdown** (`comparison_report_<timestamp>.md`): Human-readable report

### Interpreting Results

**Agreement Rate Thresholds:**
- **≥90%**: Excellent - proceed with migration
- **70-90%**: Good - review disagreements, fine-tune GEval criteria
- **<70%**: Significant differences - refine metrics or keep custom judge

**Common Adjustments:**
- Low agreement on specific metric → Review GEval criteria in `deepeval_metrics.py`
- Threshold too sensitive → Adjust `--threshold` parameter (try 0.4 or 0.6)
- Systematic disagreements → May indicate fundamental differences in evaluation philosophy

### Fine-Tuning Metrics

Edit `migration_pilot/deepeval_metrics.py` to adjust:

```python
def create_is_speculative_metric(threshold: float = 0.5) -> GEval:
    return GEval(
        name="is_speculative",
        criteria=(
            # Modify criteria text here to match your exact requirements
            "Determine whether the ANSWER uses assumptions..."
        ),
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
        threshold=threshold,
        evaluation_steps=[
            # Add or modify evaluation steps
            "Search for speculative/hedging words",
            "..."
        ]
    )
```

## Adding New Tests

When adding new evaluation tests, follow this pattern:

1. Create a test function prefixed with `test_`
2. Instantiate the desired DeepEval metric(s) with appropriate thresholds
3. Create an `LLMTestCase` with input, actual_output, and optional retrieval_context
4. Use `assert_test()` to evaluate the test case

DeepEval provides various metrics beyond AnswerRelevancyMetric, such as Faithfulness, Contextual Relevancy, and others available in `deepeval.metrics`.
