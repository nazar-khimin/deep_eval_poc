"""Data adapter for loading auto-scan backend test data."""

import json
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class BackendTestCase:
    """Represents a single test case from backend evaluation."""
    file_name: str
    question: str
    golden_answer: str
    backend_answer: str
    backend_evaluation: Dict[str, Any]


class BackendDataAdapter:
    """Adapter to load and parse auto-scan backend test data."""

    def __init__(self, test_output_dir: str):
        """
        Initialize adapter with test output directory.

        Args:
            test_output_dir: Path to test_output/<timestamp>/ directory
        """
        self.test_output_dir = Path(test_output_dir)

    def load_test_cases(self, limit: int = None) -> List[BackendTestCase]:
        """
        Load test cases from backend test output.

        Args:
            limit: Maximum number of test cases to load (None = all)

        Returns:
            List of BackendTestCase objects
        """
        # Load data files
        golden_answers = self._load_json("golden_answers.json")
        backend_answers = self._load_json("backend_answers.json")
        backend_evaluation = self._load_json("backend_evaluation_results.json")

        test_cases = []

        # Iterate through files
        for file_name in backend_evaluation.keys():
            if file_name not in golden_answers or file_name not in backend_answers:
                continue

            # Iterate through questions for this file
            for question in backend_evaluation[file_name].keys():
                if question not in golden_answers[file_name] or question not in backend_answers[file_name]:
                    continue

                test_case = BackendTestCase(
                    file_name=file_name,
                    question=question,
                    golden_answer=golden_answers[file_name][question],
                    backend_answer=backend_answers[file_name][question],
                    backend_evaluation=backend_evaluation[file_name][question]
                )

                test_cases.append(test_case)

                if limit and len(test_cases) >= limit:
                    return test_cases

        return test_cases

    def _load_json(self, filename: str) -> Dict:
        """Load JSON file from test output directory."""
        file_path = self.test_output_dir / filename
        if not file_path.exists():
            # Try in parent (test_artifacts/golden_dataset)
            alt_path = Path(self.test_output_dir).parent.parent / "test_artifacts" / "golden_dataset" / filename
            if alt_path.exists():
                file_path = alt_path
            else:
                raise FileNotFoundError(f"Could not find {filename} in {self.test_output_dir} or {alt_path}")

        with open(file_path, 'r') as f:
            return json.load(f)


def load_backend_test_data(test_output_dir: str, limit: int = None) -> List[BackendTestCase]:
    """
    Convenience function to load backend test data.

    Args:
        test_output_dir: Path to test_output/<timestamp>/ directory
        limit: Maximum number of test cases to load

    Returns:
        List of BackendTestCase objects
    """
    adapter = BackendDataAdapter(test_output_dir)
    return adapter.load_test_cases(limit=limit)
