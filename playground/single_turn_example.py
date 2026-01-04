"""
Single-Turn Evaluation Example

Demonstrates basic DeepEval usage with single-turn LLM evaluations:
- AnswerRelevancyMetric: Evaluates if answer is relevant to the question
- FaithfulnessMetric: Evaluates if answer is faithful to retrieval context
- GEval: Custom evaluation criteria

Run: poetry run python playground/single_turn_example.py
"""

import json
from pathlib import Path

from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric, GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams


def load_sample_data():
    """Load sample test cases from JSON file."""
    data_file = Path(__file__).parent / "data" / "sample_test_cases.json"
    with open(data_file, "r") as f:
        return json.load(f)["test_cases"]


def example_answer_relevancy():
    """Example: Answer Relevancy Metric"""
    print("\n" + "="*60)
    print("Example 1: Answer Relevancy Metric")
    print("="*60)

    metric = AnswerRelevancyMetric(threshold=0.7)

    test_case = LLMTestCase(
        input="What is the capital of France?",
        actual_output="The capital of France is Paris.",
        retrieval_context=["Paris is the capital and most populous city of France."]
    )

    try:
        assert_test(test_case, [metric])
        print(f"✓ Test passed!")
        print(f"  Score: {metric.score:.3f}")
        print(f"  Reason: {metric.reason}")
    except AssertionError as e:
        print(f"✗ Test failed: {e}")


def example_faithfulness():
    """Example: Faithfulness Metric"""
    print("\n" + "="*60)
    print("Example 2: Faithfulness Metric")
    print("="*60)

    metric = FaithfulnessMetric(threshold=0.7)

    test_case = LLMTestCase(
        input="What wood is best to grow for sale?",
        actual_output="Oak and walnut are considered excellent choices for timber production due to their high market value and durability.",
        retrieval_context=[
            "Oak and walnut trees are highly valued in the timber market for their strength and beautiful grain patterns.",
            "Commercial forestry typically focuses on hardwood species that command premium prices."
        ]
    )

    try:
        assert_test(test_case, [metric])
        print(f"✓ Test passed!")
        print(f"  Score: {metric.score:.3f}")
        print(f"  Reason: {metric.reason}")
    except AssertionError as e:
        print(f"✗ Test failed: {e}")


def example_geval_custom():
    """Example: Custom GEval Metric"""
    print("\n" + "="*60)
    print("Example 3: Custom GEval Metric - Comprehensiveness")
    print("="*60)

    comprehensiveness_metric = GEval(
        name="Comprehensiveness",
        criteria=(
            "Evaluate if the answer is comprehensive and complete. "
            "The answer should:\n"
            "1. Address all parts of the question\n"
            "2. Avoid speculative language (might, could, seems, possibly)\n"
            "3. Use confident, assertive phrasing\n"
            "4. Not ask for additional information from the user\n"
            "5. Provide specific details rather than vague generalizations"
        ),
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
        threshold=0.7
    )

    test_case = LLMTestCase(
        input="Explain machine learning in simple terms.",
        actual_output="Machine learning is a type of artificial intelligence that allows computers to learn from data and improve their performance over time without being explicitly programmed.",
        expected_output="Machine learning enables computers to learn patterns from data and make predictions or decisions automatically."
    )

    try:
        assert_test(test_case, [comprehensiveness_metric])
        print(f"✓ Test passed!")
        print(f"  Score: {comprehensiveness_metric.score:.3f}")
        print(f"  Reason: {comprehensiveness_metric.reason}")
    except AssertionError as e:
        print(f"✗ Test failed: {e}")


def example_multiple_metrics():
    """Example: Evaluating with multiple metrics at once"""
    print("\n" + "="*60)
    print("Example 4: Multiple Metrics")
    print("="*60)

    metrics = [
        AnswerRelevancyMetric(threshold=0.7),
        FaithfulnessMetric(threshold=0.7)
    ]

    test_case = LLMTestCase(
        input="What is the capital of France?",
        actual_output="The capital of France is Paris.",
        retrieval_context=[
            "Paris is the capital and most populous city of France, located on the Seine River.",
            "France is a country in Western Europe with Paris as its capital city."
        ]
    )

    try:
        assert_test(test_case, metrics)
        print(f"✓ All tests passed!")
        for metric in metrics:
            print(f"  {metric.__class__.__name__}: {metric.score:.3f}")
    except AssertionError as e:
        print(f"✗ Test failed: {e}")


def example_from_json_data():
    """Example: Load test cases from JSON and evaluate"""
    print("\n" + "="*60)
    print("Example 5: Batch Evaluation from JSON")
    print("="*60)

    test_cases_data = load_sample_data()
    metric = AnswerRelevancyMetric(threshold=0.7)

    results = []
    for case_data in test_cases_data:
        print(f"\nEvaluating case #{case_data['id']}: {case_data['question'][:50]}...")

        test_case = LLMTestCase(
            input=case_data["question"],
            actual_output=case_data["actual_output"],
            expected_output=case_data.get("expected_output"),
            retrieval_context=case_data.get("retrieval_context", [])
        )

        try:
            assert_test(test_case, [metric])
            results.append({
                "id": case_data["id"],
                "passed": True,
                "score": metric.score
            })
            print(f"  ✓ Passed (score: {metric.score:.3f})")
        except AssertionError:
            results.append({
                "id": case_data["id"],
                "passed": False,
                "score": metric.score
            })
            print(f"  ✗ Failed (score: {metric.score:.3f})")

    # Summary
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    print(f"\n{'='*60}")
    print(f"Summary: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print(f"{'='*60}")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print(" DeepEval Single-Turn Evaluation Examples")
    print("="*70)
    print("\nNote: These examples require OPENAI_API_KEY in your .env file")
    print("Some examples may fail if the API key is not set or if API is unavailable")

    # Run all examples
    example_answer_relevancy()
    example_faithfulness()
    example_geval_custom()
    example_multiple_metrics()
    example_from_json_data()

    print("\n" + "="*70)
    print(" All examples completed!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
