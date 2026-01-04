# DeepEval Proof of Concept

A proof-of-concept repository for testing [DeepEval](https://deepeval.com), a framework for evaluating LLM outputs.

## Project Structure

```
deep_eval_poc/
├── src/
│   ├── constants.py              # Environment configuration
│   └── deepeval_introduction.py  # DeepEval feature examples
├── playground/                   # Experimental testing area
│   ├── single_turn_example.py    # Runnable single-turn examples
│   ├── data/                     # Sample test data
│   └── README.md                 # Playground documentation
├── migration_pilot/              # Migration validation pilot
│   ├── run_pilot.py              # Main pilot script
│   ├── deepeval_metrics.py       # Custom GEval metrics
│   ├── data_adapter.py           # Backend data loader
│   ├── comparison.py             # Comparison & reporting
│   └── README.md                 # Pilot documentation
├── main.py                       # Basic test examples
├── pyproject.toml                # Poetry dependencies
├── .env.example                  # Environment variables template
└── CLAUDE.md                     # Project documentation for Claude Code
```

## Quick Start

### 1. Install Dependencies

```bash
poetry install
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Run Examples

**Basic tests:**
```bash
poetry run python main.py
poetry run pytest main.py -v
```

**Playground (recommended):**
```bash
poetry run python playground/single_turn_example.py
```

**Migration Pilot (validate DeepEval vs custom judge):**
```bash
poetry run python migration_pilot/run_pilot.py --test-dir <path-to-backend-test-output> --limit 5
```

## What's Inside

### Main Examples (`main.py`)

Basic DeepEval test examples using `AnswerRelevancyMetric`.

### Playground (`playground/`)

Comprehensive single-turn evaluation examples demonstrating:
- Answer Relevancy Metric
- Faithfulness Metric
- Custom GEval metrics
- Multiple metrics evaluation
- Batch evaluation from JSON

See [`playground/README.md`](playground/README.md) for details.

### Migration Pilot (`migration_pilot/`)

Validates whether DeepEval can replicate auto-scan backend evaluation results:
- Loads existing backend test data (golden answers, RAG answers, LLM judge results)
- Evaluates with custom GEval metrics matching 4 boolean indicators
- Compares DeepEval vs custom judge results
- Generates comprehensive reports (console + JSON + markdown)

See [`migration_pilot/README.md`](migration_pilot/README.md) for usage.

### Source (`src/`)

- **constants.py**: Environment configuration with `.env` loading
- **deepeval_introduction.py**: Advanced DeepEval features (single-turn, multi-turn, tracing)

## Key Concepts

### LLMTestCase

```python
from deepeval.test_case import LLMTestCase

test_case = LLMTestCase(
    input="What is X?",
    actual_output="X is...",
    expected_output="X is...",         # Optional
    retrieval_context=["Context..."]   # Optional
)
```

### Metrics

```python
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric

# Built-in metrics
relevancy = AnswerRelevancyMetric(threshold=0.7)
faithfulness = FaithfulnessMetric(threshold=0.7)

# Custom metrics
from deepeval.metrics import GEval

custom = GEval(
    name="Comprehensiveness",
    criteria="Your evaluation criteria...",
    threshold=0.7
)
```

### Evaluation

```python
from deepeval import assert_test

assert_test(test_case, [metric1, metric2])
```

## Documentation

- **[CLAUDE.md](CLAUDE.md)**: Detailed project architecture and DeepEval usage patterns
- **[playground/README.md](playground/README.md)**: Playground documentation
- **[migration_pilot/README.md](migration_pilot/README.md)**: Migration pilot guide
- **[DeepEval Docs](https://deepeval.com/docs/getting-started)**: Official documentation

## Use Cases

This POC helps evaluate:
- **RAG Systems**: Answer relevancy and faithfulness to retrieval context
- **Chat Quality**: Multi-turn conversational evaluation
- **Custom Criteria**: Business-specific evaluation rules via GEval

## Next Steps

1. Explore the playground examples
2. Add your own test cases in `playground/data/sample_test_cases.json`
3. Experiment with custom GEval criteria
4. **Run the migration pilot** to validate DeepEval on your real test data
5. Review migration strategy for existing test suites (see CLAUDE.md)
