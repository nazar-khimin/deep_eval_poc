"""
DeepEval Introduction Examples
Based on: https://deepeval.com/docs/getting-started
"""

from deepeval import assert_test
from deepeval.test_case import LLMTestCase, LLMTestCaseParams, Turn, ConversationalTestCase
from deepeval.metrics import GEval, ConversationalGEval, AnswerRelevancyMetric
from deepeval.tracing import observe, update_current_span
from deepeval.dataset import EvaluationDataset, Golden

# Import constants to ensure .env is loaded
from constants import const


# Single-Turn Evaluation
def test_correctness():
    correctness_metric = GEval(
        name="Correctness",
        criteria="Determine if the 'actual output' is correct based on the 'expected output'.",
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
        threshold=0.5
    )
    test_case = LLMTestCase(
        input="I have a persistent cough and fever. Should I be worried?",
        actual_output="A persistent cough and fever could be a viral infection or something more serious. See a doctor if symptoms worsen or don't improve in a few days.",
        expected_output="A persistent cough and fever could indicate a range of illnesses, from a mild viral infection to more serious conditions..."
    )
    assert_test(test_case, [correctness_metric])


# Multi-Turn Conversational Test
def test_professionalism():
    professionalism_metric = ConversationalGEval(
        name="Professionalism",
        criteria="Determine whether the assistant has acted professionally based on the content.",
        threshold=0.5
    )
    test_case = ConversationalTestCase(
        turns=[
            Turn(role="user", content="What is DeepEval?"),
            Turn(role="assistant", content="DeepEval is an open-source LLM eval package.")
        ]
    )
    assert_test(test_case, [professionalism_metric])


# Component-Level Testing with Tracing
@observe()
def llm_app(input: str):
    @observe(metrics=[AnswerRelevancyMetric()])
    def inner_component():
        update_current_span(test_case=LLMTestCase(input="Why is the blue sky?", actual_output="..."))
    return inner_component()


dataset = EvaluationDataset(goldens=[Golden(input="Test input")])
for golden in dataset.evals_iterator():
    llm_app(golden.input)
