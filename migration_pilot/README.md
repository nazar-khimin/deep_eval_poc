# Migration Pilot: DeepEval vs Custom LLM Judge

This migration pilot validates whether DeepEval can replicate your auto-scan backend evaluation results using custom GEval metrics.

## Overview

The pilot:
1. Loads your existing backend test data (golden answers, RAG answers, LLM judge results)
2. Evaluates the same test cases using DeepEval with custom GEval metrics
3. Compares DeepEval results with your existing LLM judge results
4. Generates comprehensive reports (console + JSON + markdown)

## Architecture

```
migration_pilot/
├── __init__.py
├── README.md                  # This file
├── data_adapter.py            # Loads backend test JSON files
├── deepeval_metrics.py        # Custom GEval metrics (4 boolean indicators)
├── comparison.py              # Comparison logic and report generation
├── run_pilot.py               # Main script
└── output/                    # Generated reports (gitignored)
    ├── deepeval_results_*.json
    ├── comparison_*.json
    └── comparison_report_*.md
```

## Custom GEval Metrics

The pilot implements 4 GEval metrics matching your backend evaluation criteria:

### 1. `is_question_answered`
- **Purpose**: Did the answer address all significant parts of the question?
- **Backend logic**: True if ANSWER directly addresses all parts; False if off-topic/incomplete
- **DeepEval implementation**: GEval with multi-part question detection

### 2. `requires_additional_information`
- **Purpose**: Does the answer explicitly request more info from the user?
- **Backend logic**: True only if ANSWER explicitly asks user for details
- **DeepEval implementation**: GEval searching for request phrases ("please provide", "I need", etc.)

### 3. `is_speculative`
- **Purpose**: Does the answer use hypothetical/inferential language?
- **Backend logic**: True if uses "might", "could", "seems", "possibly", etc.
- **DeepEval implementation**: GEval detecting hedging/uncertainty markers

### 4. `is_confident`
- **Purpose**: Is the answer phrased directly and assertively?
- **Backend logic**: True if assertive ("Yes, X is..."); False if uncertain ("seems like")
- **DeepEval implementation**: GEval analyzing tone and phrasing

### Composite Metric: `comprehensive_answer`
```python
comprehensive_answer = (
    is_question_answered AND
    NOT requires_additional_information AND
    NOT is_speculative AND
    is_confident
)
```

## Usage

### Basic Usage

```bash
poetry run python migration_pilot/run_pilot.py \
    --test-dir /Users/nkhimin/PycharmProjects/auto-scan-backend/tests/ai_chat_evaluation_tests/test_output/1764025492 \
    --limit 5
```

### Full Options

```bash
poetry run python migration_pilot/run_pilot.py \
    --test-dir <path-to-test-output-dir> \
    --limit 10 \
    --threshold 0.5 \
    --output-dir migration_pilot/output
```

**Arguments:**
- `--test-dir`: Path to `test_output/<timestamp>/` directory (required)
- `--limit`: Number of test cases to evaluate (default: all)
- `--threshold`: DeepEval metric threshold for True/False (default: 0.5)
- `--output-dir`: Output directory for reports (default: migration_pilot/output)

## Output Files

### 1. Console Output

Real-time progress and summary:
```
==================================================================
SUMMARY
==================================================================
Total test cases: 10
Agreement rate: 85.0%

Metric agreements:
  is_question_answered: 90.0% (9/10)
  requires_additional_information: 100.0% (10/10)
  is_speculative: 80.0% (8/10)
  is_confident: 70.0% (7/10)
==================================================================
```

### 2. JSON Output

**`deepeval_results_<timestamp>.json`**:
```json
[
  {
    "file_name": "123216 - R0857_original-2",
    "question": "According to the text, who won the Nobel Prize in Physics?",
    "backend_answer": "The document does not provide this information.",
    "deepeval_scores": {
      "is_question_answered": {
        "score": 0.2,
        "threshold": 0.5,
        "passed": false,
        "reason": "..."
      },
      ...
    },
    "deepeval_comprehensive_answer": false,
    "backend_evaluation": {
      "is_question_answered": false,
      ...
    }
  }
]
```

**`comparison_<timestamp>.json`**:
```json
{
  "summary": {
    "total_cases": 10,
    "successful_evaluations": 10,
    "agreement_rate": 0.85
  },
  "metric_comparisons": {
    "is_question_answered": {
      "agreements": 9,
      "disagreements": 1,
      "agreement_rate": 0.9
    },
    ...
  },
  "disagreements": [...]
}
```

### 3. Markdown Report

**`comparison_report_<timestamp>.md`**:
- Summary statistics
- Metric-by-metric comparison table
- Detailed disagreements with reasoning
- Interpretation and recommendations

## Interpreting Results

### Agreement Rate Thresholds

| Agreement Rate | Interpretation | Action |
|----------------|----------------|--------|
| ≥ 90% | Excellent - DeepEval matches backend judge | ✅ Proceed with migration |
| 70-90% | Good with minor differences | ⚠️ Review disagreements, fine-tune GEval |
| < 70% | Significant differences | ❌ Refine GEval or keep custom judge |

### Reviewing Disagreements

When DeepEval disagrees with backend judge:
1. Check **DeepEval score** - is it close to threshold (0.4-0.6)?
2. Read **DeepEval reason** - does the logic make sense?
3. Compare with **backend evaluation** - which one is correct?
4. Adjust GEval criteria or threshold if needed

### Common Issues

**Low agreement on `is_speculative`:**
- DeepEval may detect hedging words backend judge misses
- Adjust GEval criteria to match your definition of "speculative"

**Low agreement on `is_confident`:**
- Confidence detection is nuanced
- Review disagreements to calibrate tone detection

## Fine-Tuning GEval Metrics

Edit `migration_pilot/deepeval_metrics.py` to adjust:

### 1. Criteria Text
```python
def create_is_speculative_metric(threshold: float = 0.5) -> GEval:
    return GEval(
        name="is_speculative",
        criteria=(
            "Your refined criteria here..."
        ),
        ...
    )
```

### 2. Evaluation Steps
```python
evaluation_steps=[
    "Step 1: ...",
    "Step 2: ...",
    ...
]
```

### 3. Threshold
```python
# In run_pilot.py --threshold argument
# Or per-metric:
create_is_speculative_metric(threshold=0.6)
```

## Next Steps After Pilot

### If Agreement ≥ 90%:
1. Run pilot on larger dataset (--limit 50+)
2. Validate with domain experts
3. Plan full migration

### If Agreement 70-90%:
1. Analyze disagreements
2. Refine GEval criteria
3. Re-run pilot
4. Consider hybrid approach (DeepEval + custom metrics)

### If Agreement < 70%:
1. Deep dive into disagreements
2. Consider if GEval can capture your logic
3. May need to keep custom LLM judge or build custom DeepEval metrics

## Troubleshooting

### FileNotFoundError
```
Could not find backend_answers.json
```
**Solution**: Ensure `--test-dir` points to `test_output/<timestamp>/` directory containing:
- `backend_answers.json`
- `backend_evaluation_results.json`
- Access to `test_artifacts/golden_dataset/golden_answers.json` in parent directories

### API Rate Limiting
```
Error: Rate limit exceeded
```
**Solution**: Use `--limit` to reduce test cases or wait between runs

### Low Scores
```
All DeepEval scores are < 0.3
```
**Solution**: Check that GEval criteria match your intent. Run on known good/bad examples first.

## Contributing

To extend the pilot:
1. Add new metrics in `deepeval_metrics.py`
2. Update comparison logic in `comparison.py`
3. Modify report generation in `generate_comparison_report()`

## Support

For issues specific to:
- **DeepEval**: See [DeepEval docs](https://deepeval.com/docs)
- **This pilot**: Check main project `CLAUDE.md` or migration analysis
