from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase


def test_answer_relevancy():
    """
    Test example using DeepEval's AnswerRelevancyMetric.
    This evaluates whether an LLM's response is relevant to the input query.
    """
    answer_relevancy_metric = AnswerRelevancyMetric(threshold=0.7)

    test_case = LLMTestCase(
        input="What is the capital of France?",
        actual_output="The capital of France is Paris.",
        retrieval_context=["Paris is the capital and most populous city of France."]
    )

    assert_test(test_case, [answer_relevancy_metric])


def test_custom_evaluation():
    """
    Example of a custom test case for evaluating LLM outputs.
    Replace with your own test scenarios.
    """
    answer_relevancy_metric = AnswerRelevancyMetric(threshold=0.5)

    test_case = LLMTestCase(
        input="Explain machine learning in simple terms.",
        actual_output="Machine learning is a type of artificial intelligence that allows computers to learn from data and improve their performance over time without being explicitly programmed.",
        retrieval_context=["Machine learning is a subset of AI focused on building systems that learn from data."]
    )

    assert_test(test_case, [answer_relevancy_metric])


if __name__ == '__main__':
    print("Running DeepEval tests...")
    test_answer_relevancy()
    test_custom_evaluation()
    print("All tests completed!")
