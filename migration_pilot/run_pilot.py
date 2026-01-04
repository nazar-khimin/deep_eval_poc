"""
Migration Pilot: DeepEval vs Custom LLM Judge Comparison

This script evaluates the same test cases using DeepEval and compares the results
with your existing custom LLM judge evaluations.

Usage:
    poetry run python migration_pilot/run_pilot.py --test-dir /path/to/test_output/1764025492 --limit 5
"""

import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from deepeval import assert_test
from deepeval.test_case import LLMTestCase

from migration_pilot.data_adapter import load_backend_test_data, BackendTestCase
from migration_pilot.deepeval_metrics import create_all_backend_metrics
from migration_pilot.comparison import compare_results, generate_comparison_report


def evaluate_with_deepeval(test_cases: List[BackendTestCase], threshold: float = 0.5) -> List[Dict[str, Any]]:
    """
    Evaluate test cases using DeepEval metrics.

    Args:
        test_cases: List of BackendTestCase objects
        threshold: Threshold for metrics (0.5 = >= 0.5 is True)

    Returns:
        List of evaluation results
    """
    print(f"\n{'='*70}")
    print("EVALUATING WITH DEEPEVAL")
    print(f"{'='*70}\n")

    results = []
    metrics = create_all_backend_metrics(threshold=threshold)

    for idx, test_case in enumerate(test_cases, 1):
        print(f"[{idx}/{len(test_cases)}] Evaluating: {test_case.file_name}")
        print(f"  Question: {test_case.question[:80]}...")

        # Create DeepEval test case
        llm_test_case = LLMTestCase(
            input=test_case.question,
            actual_output=test_case.backend_answer,
            expected_output=test_case.golden_answer
        )

        # Run evaluation
        try:
            # Note: We're not using assert_test here because we want to capture scores
            # even if they don't meet threshold
            for metric in metrics:
                metric.measure(llm_test_case)

            # Collect scores
            deepeval_scores = {
                metric.name: {
                    "score": metric.score,
                    "threshold": metric.threshold,
                    "passed": metric.score >= metric.threshold,
                    "reason": metric.reason
                }
                for metric in metrics
            }

            # Calculate comprehensive_answer
            comprehensive_answer = (
                deepeval_scores["is_question_answered"]["passed"] and
                not deepeval_scores["requires_additional_information"]["passed"] and
                not deepeval_scores["is_speculative"]["passed"] and
                deepeval_scores["is_confident"]["passed"]
            )

            result = {
                "file_name": test_case.file_name,
                "question": test_case.question,
                "backend_answer": test_case.backend_answer,
                "deepeval_scores": deepeval_scores,
                "deepeval_comprehensive_answer": comprehensive_answer,
                "backend_evaluation": test_case.backend_evaluation,
            }

            results.append(result)

            print(f"  ✓ DeepEval comprehensive_answer: {comprehensive_answer}")

        except Exception as e:
            print(f"  ✗ Error: {e}")
            result = {
                "file_name": test_case.file_name,
                "question": test_case.question,
                "backend_answer": test_case.backend_answer,
                "deepeval_scores": None,
                "deepeval_comprehensive_answer": None,
                "backend_evaluation": test_case.backend_evaluation,
                "error": str(e)
            }
            results.append(result)

    return results


def main():
    """Main entry point for migration pilot."""
    parser = argparse.ArgumentParser(description="Run DeepEval migration pilot")
    parser.add_argument(
        "--test-dir",
        required=True,
        help="Path to test_output/<timestamp>/ directory"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of test cases to evaluate"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Threshold for DeepEval metrics (default: 0.5)"
    )
    parser.add_argument(
        "--output-dir",
        default="migration_pilot/output",
        help="Output directory for results"
    )

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"\n{'='*70}")
    print("DEEPEVAL MIGRATION PILOT")
    print(f"{'='*70}")
    print(f"Test directory: {args.test_dir}")
    print(f"Limit: {args.limit or 'None (all)'}")
    print(f"Threshold: {args.threshold}")
    print(f"Output directory: {output_dir}")
    print(f"{'='*70}\n")

    # Load test data
    print("Loading backend test data...")
    test_cases = load_backend_test_data(args.test_dir, limit=args.limit)
    print(f"✓ Loaded {len(test_cases)} test cases\n")

    # Evaluate with DeepEval
    results = evaluate_with_deepeval(test_cases, threshold=args.threshold)

    # Save raw results
    results_file = output_dir / f"deepeval_results_{timestamp}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✓ Raw results saved to: {results_file}")

    # Generate comparison report
    print(f"\n{'='*70}")
    print("GENERATING COMPARISON REPORT")
    print(f"{'='*70}\n")

    comparison = compare_results(results)

    # Save comparison JSON
    comparison_file = output_dir / f"comparison_{timestamp}.json"
    with open(comparison_file, 'w') as f:
        json.dump(comparison, f, indent=2)
    print(f"✓ Comparison JSON saved to: {comparison_file}")

    # Generate and save markdown report
    markdown_report = generate_comparison_report(comparison, results)
    markdown_file = output_dir / f"comparison_report_{timestamp}.md"
    with open(markdown_file, 'w') as f:
        f.write(markdown_report)
    print(f"✓ Markdown report saved to: {markdown_file}")

    # Print summary to console
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"Total test cases: {comparison['summary']['total_cases']}")
    print(f"Agreement rate: {comparison['summary']['agreement_rate']:.1%}")
    print(f"\nMetric agreements:")
    for metric, stats in comparison['metric_comparisons'].items():
        print(f"  {metric}: {stats['agreement_rate']:.1%} ({stats['agreements']}/{stats['total']})")
    print(f"{'='*70}\n")

    print(f"✓ Pilot completed successfully!")
    print(f"  View detailed report: {markdown_file}")


if __name__ == "__main__":
    main()
