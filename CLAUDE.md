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

# Set OpenAI API key (required for DeepEval metrics)
export OPENAI_API_KEY="your-api-key"
```

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

The project currently contains a single test file (`main.py`) that demonstrates DeepEval usage:

- **Test Structure**: Tests use `LLMTestCase` objects that contain:
  - `input`: The query or prompt sent to the LLM
  - `actual_output`: The LLM's response
  - `retrieval_context`: Supporting context used for evaluation

- **Metrics**: Currently uses `AnswerRelevancyMetric` which evaluates whether an LLM's output is relevant to the input query. Each metric has a configurable `threshold` (0.0 to 1.0) that determines pass/fail criteria.

- **Assertion Pattern**: Tests use `assert_test(test_case, [metrics])` to validate LLM outputs against defined metrics.

## Adding New Tests

When adding new evaluation tests, follow this pattern:

1. Create a test function prefixed with `test_`
2. Instantiate the desired DeepEval metric(s) with appropriate thresholds
3. Create an `LLMTestCase` with input, actual_output, and optional retrieval_context
4. Use `assert_test()` to evaluate the test case

DeepEval provides various metrics beyond AnswerRelevancyMetric, such as Faithfulness, Contextual Relevancy, and others available in `deepeval.metrics`.
