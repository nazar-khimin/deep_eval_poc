"""Comparison logic for DeepEval vs Custom LLM Judge results."""

from typing import List, Dict, Any


def compare_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compare DeepEval results with backend LLM judge results.

    Args:
        results: List of evaluation results from run_pilot.py

    Returns:
        Dictionary with comparison statistics
    """
    metric_names = ["is_question_answered", "requires_additional_information", "is_speculative", "is_confident"]

    comparison = {
        "summary": {
            "total_cases": len(results),
            "successful_evaluations": 0,
            "failed_evaluations": 0,
            "agreement_rate": 0.0,
        },
        "metric_comparisons": {},
        "comprehensive_answer_comparison": {
            "agreements": 0,
            "disagreements": 0,
            "agreement_rate": 0.0,
        },
        "disagreements": []
    }

    # Initialize metric comparison counters
    for metric in metric_names:
        comparison["metric_comparisons"][metric] = {
            "agreements": 0,
            "disagreements": 0,
            "total": 0,
            "agreement_rate": 0.0,
            "backend_true": 0,
            "backend_false": 0,
            "deepeval_true": 0,
            "deepeval_false": 0,
        }

    # Compare each result
    for result in results:
        if result.get("error") or not result.get("deepeval_scores"):
            comparison["summary"]["failed_evaluations"] += 1
            continue

        comparison["summary"]["successful_evaluations"] += 1

        backend_eval = result["backend_evaluation"]
        deepeval_scores = result["deepeval_scores"]

        # Compare individual metrics
        for metric in metric_names:
            backend_value = backend_eval.get(metric, None)
            deepeval_passed = deepeval_scores[metric]["passed"]

            if backend_value is None:
                continue

            stats = comparison["metric_comparisons"][metric]
            stats["total"] += 1

            # Track backend values
            if backend_value:
                stats["backend_true"] += 1
            else:
                stats["backend_false"] += 1

            # Track deepeval values
            if deepeval_passed:
                stats["deepeval_true"] += 1
            else:
                stats["deepeval_false"] += 1

            # Check agreement
            if backend_value == deepeval_passed:
                stats["agreements"] += 1
            else:
                stats["disagreements"] += 1

                # Record disagreement
                comparison["disagreements"].append({
                    "file_name": result["file_name"],
                    "question": result["question"],
                    "metric": metric,
                    "backend_value": backend_value,
                    "deepeval_value": deepeval_passed,
                    "deepeval_score": deepeval_scores[metric]["score"],
                    "deepeval_reason": deepeval_scores[metric].get("reason", "N/A"),
                })

        # Compare comprehensive_answer
        backend_comp = (
            backend_eval.get("is_question_answered", False) and
            not backend_eval.get("requires_additional_information", False) and
            not backend_eval.get("is_speculative", False) and
            backend_eval.get("is_confident", False)
        )
        deepeval_comp = result["deepeval_comprehensive_answer"]

        if backend_comp == deepeval_comp:
            comparison["comprehensive_answer_comparison"]["agreements"] += 1
        else:
            comparison["comprehensive_answer_comparison"]["disagreements"] += 1

    # Calculate rates
    if comparison["summary"]["successful_evaluations"] > 0:
        comparison["comprehensive_answer_comparison"]["agreement_rate"] = (
            comparison["comprehensive_answer_comparison"]["agreements"] /
            comparison["summary"]["successful_evaluations"]
        )
        comparison["summary"]["agreement_rate"] = comparison["comprehensive_answer_comparison"]["agreement_rate"]

    for metric in metric_names:
        stats = comparison["metric_comparisons"][metric]
        if stats["total"] > 0:
            stats["agreement_rate"] = stats["agreements"] / stats["total"]

    return comparison


def generate_comparison_report(comparison: Dict[str, Any], results: List[Dict[str, Any]]) -> str:
    """
    Generate markdown comparison report.

    Args:
        comparison: Comparison statistics from compare_results()
        results: Original evaluation results

    Returns:
        Markdown formatted report
    """
    report = []

    # Header
    report.append("# DeepEval Migration Pilot - Comparison Report\n")
    report.append(f"**Generated**: {comparison.get('timestamp', 'N/A')}\n")

    # Summary
    report.append("## Summary\n")
    report.append(f"- **Total test cases**: {comparison['summary']['total_cases']}")
    report.append(f"- **Successful evaluations**: {comparison['summary']['successful_evaluations']}")
    report.append(f"- **Failed evaluations**: {comparison['summary']['failed_evaluations']}")
    report.append(f"- **Overall agreement rate**: {comparison['summary']['agreement_rate']:.1%}\n")

    # Comprehensive Answer Comparison
    report.append("## Comprehensive Answer Comparison\n")
    comp_stats = comparison["comprehensive_answer_comparison"]
    report.append(f"- **Agreements**: {comp_stats['agreements']}")
    report.append(f"- **Disagreements**: {comp_stats['disagreements']}")
    report.append(f"- **Agreement rate**: {comp_stats['agreement_rate']:.1%}\n")

    # Metric-by-Metric Comparison
    report.append("## Individual Metric Comparisons\n")
    report.append("| Metric | Agreement Rate | Agreements | Disagreements | Backend T/F | DeepEval T/F |")
    report.append("|--------|----------------|------------|---------------|-------------|--------------|")

    for metric, stats in comparison["metric_comparisons"].items():
        report.append(
            f"| `{metric}` | {stats['agreement_rate']:.1%} | "
            f"{stats['agreements']} | {stats['disagreements']} | "
            f"{stats['backend_true']}/{stats['backend_false']} | "
            f"{stats['deepeval_true']}/{stats['deepeval_false']} |"
        )

    report.append("")

    # Disagreements Detail
    if comparison["disagreements"]:
        report.append("## Disagreements Detail\n")
        report.append(f"Found {len(comparison['disagreements'])} disagreements:\n")

        for idx, disagreement in enumerate(comparison["disagreements"][:20], 1):  # Limit to first 20
            report.append(f"### {idx}. {disagreement['metric']}\n")
            report.append(f"**File**: `{disagreement['file_name']}`\n")
            report.append(f"**Question**: {disagreement['question'][:100]}...\n")
            report.append(f"- **Backend**: `{disagreement['backend_value']}`")
            report.append(f"- **DeepEval**: `{disagreement['deepeval_value']}` (score: {disagreement['deepeval_score']:.3f})")
            report.append(f"- **Reason**: {disagreement['deepeval_reason'][:200]}...\n")

        if len(comparison["disagreements"]) > 20:
            report.append(f"\n*(Showing first 20 of {len(comparison['disagreements'])} disagreements)*\n")
    else:
        report.append("## Disagreements Detail\n")
        report.append("No disagreements found! DeepEval perfectly matches backend evaluation.\n")

    # Interpretation
    report.append("## Interpretation\n")

    agreement_rate = comparison['summary']['agreement_rate']

    if agreement_rate >= 0.9:
        report.append("**Verdict**: ✅ **Excellent Agreement**\n")
        report.append(
            "DeepEval metrics show excellent agreement (>90%) with your custom LLM judge. "
            "This suggests DeepEval can effectively replicate your evaluation logic. "
            "Consider proceeding with migration.\n"
        )
    elif agreement_rate >= 0.7:
        report.append("**Verdict**: ⚠️ **Good Agreement with Minor Differences**\n")
        report.append(
            "DeepEval metrics show good agreement (70-90%) with your custom LLM judge. "
            "Review the disagreements to understand where the evaluation logic differs. "
            "You may need to fine-tune GEval criteria or thresholds.\n"
        )
    else:
        report.append("**Verdict**: ❌ **Significant Differences**\n")
        report.append(
            "DeepEval metrics show significant disagreement (<70%) with your custom LLM judge. "
            "Carefully review the disagreements to understand the gaps. "
            "Consider refining GEval criteria or sticking with your custom judge.\n"
        )

    # Recommendations
    report.append("## Recommendations\n")

    for metric, stats in comparison["metric_comparisons"].items():
        if stats["agreement_rate"] < 0.7 and stats["total"] > 0:
            report.append(f"- **{metric}**: Low agreement ({stats['agreement_rate']:.1%}). "
                         f"Review GEval criteria and adjust threshold or wording.\n")

    if comparison['summary']['failed_evaluations'] > 0:
        report.append(f"- {comparison['summary']['failed_evaluations']} evaluations failed. "
                     f"Check API errors or rate limiting.\n")

    return "\n".join(report)
