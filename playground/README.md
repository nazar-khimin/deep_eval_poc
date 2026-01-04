# DeepEval Playground

Experimental area for testing DeepEval features and evaluation patterns.

## Structure

```
playground/
├── README.md                      # This file
├── single_turn_example.py         # Main example script
└── data/
    └── sample_test_cases.json     # Sample test data
```

## Quick Start

### Prerequisites

1. Ensure you have a `.env` file with your `OPENAI_API_KEY`:
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

### Run the Example

```bash
poetry run python playground/single_turn_example.py
```

## What's Inside

### `single_turn_example.py`

Demonstrates 5 key DeepEval patterns:

1. **Answer Relevancy** - Evaluates if answers are relevant to questions
2. **Faithfulness** - Evaluates if answers are faithful to retrieval context
3. **Custom GEval** - Custom evaluation criteria (comprehensiveness example)
4. **Multiple Metrics** - Running multiple metrics on one test case
5. **Batch Evaluation** - Loading and evaluating multiple test cases from JSON

### `data/sample_test_cases.json`

Contains sample test cases with:
- Questions
- Actual outputs (simulated LLM responses)
- Expected outputs (golden answers)
- Retrieval context (supporting documents)

## Key DeepEval Concepts Demonstrated

### Test Case Structure

```python
from deepeval.test_case import LLMTestCase

test_case = LLMTestCase(
    input="What is X?",                    # The question/prompt
    actual_output="X is...",                # LLM's actual response
    expected_output="X is...",              # Golden/reference answer (optional)
    retrieval_context=["Context 1", ...]    # Supporting documents (optional)
)
```

### Metrics

**Built-in Metrics:**
- `AnswerRelevancyMetric` - Is the answer relevant to the question?
- `FaithfulnessMetric` - Is the answer faithful to the retrieval context?

**Custom Metrics:**
- `GEval` - Define your own evaluation criteria in natural language

### Evaluation

```python
from deepeval import assert_test

# Single metric
assert_test(test_case, [metric])

# Multiple metrics
assert_test(test_case, [metric1, metric2, metric3])

# Access results
print(metric.score)   # Numeric score (0.0 to 1.0)
print(metric.reason)  # Explanation of the score
```

## Extending the Playground

### Add More Test Cases

Edit `data/sample_test_cases.json` and add new test cases:

```json
{
  "id": 4,
  "question": "Your question here",
  "actual_output": "LLM's response",
  "expected_output": "Golden answer",
  "retrieval_context": ["Context 1", "Context 2"]
}
```

### Create Custom Metrics

Add new GEval metrics with custom criteria:

```python
custom_metric = GEval(
    name="YourMetricName",
    criteria="Your evaluation criteria here...",
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    threshold=0.7
)
```

### Experiment with Different Models

DeepEval uses OpenAI by default, but you can configure different models:

```python
# In your test setup
metric = AnswerRelevancyMetric(
    threshold=0.7,
    model="gpt-4"  # Specify model
)
```

## Migration to Auto-Scan Backend Tests

This playground is intentionally simple and standalone. When ready to migrate your auto-scan backend tests:

1. **Golden Dataset**: Convert `golden_dataset.json` to DeepEval `EvaluationDataset` format
2. **Backend Answers**: Keep your existing answer collection logic
3. **Evaluation**: Replace custom LLM judge with DeepEval metrics
4. **Metrics**: Map your 5 binary indicators to GEval criteria
5. **Analysis**: Keep custom analysis pipeline or build on top of DeepEval results

See the main project analysis for detailed migration strategy.

## Troubleshooting

### API Key Not Found

```
Error: OPENAI_API_KEY not found in environment
```

**Solution**: Create `.env` file with your API key:
```bash
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

### Rate Limiting

```
Error: Rate limit exceeded
```

**Solution**: DeepEval makes multiple API calls. Wait a moment and try again, or use a lower-tier model.

### Import Errors

```
ModuleNotFoundError: No module named 'deepeval'
```

**Solution**: Install dependencies:
```bash
poetry install
```

## Next Steps

1. Run the example and examine the output
2. Modify test cases in `data/sample_test_cases.json`
3. Experiment with custom GEval criteria
4. Try different threshold values
5. Compare results with your auto-scan backend tests

For more information, see:
- [DeepEval Documentation](https://deepeval.com/docs/getting-started)
- Main project `CLAUDE.md` for architecture details
- Auto-scan backend analysis for migration guidance
