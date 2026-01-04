"""Custom DeepEval GEval metrics matching auto-scan backend evaluation criteria."""

from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams


def create_is_question_answered_metric(threshold: float = 0.5) -> GEval:
    """
    Metric: is_question_answered

    Evaluates if the answer directly and reasonably addresses the main intent
    of all significant parts of the question.

    Matches backend criteria:
    - True: ANSWER directly addresses all significant parts of QUESTION
    - False: Off-topic, incomplete, or misses central point
    - For multi-part questions: ALL significant parts must be addressed
    """
    return GEval(
        name="is_question_answered",
        criteria=(
            "Determine whether the ANSWER directly and reasonably addresses the main intent "
            "of ALL significant parts of the QUESTION.\n\n"
            "Set to 1.0 (True) if:\n"
            "- The ANSWER provides relevant information that directly responds to the question's core intent\n"
            "- For multi-part questions, ALL significant parts are addressed\n"
            "- Special case: If the ANSWER states the information is absent from the document BUT provides "
            "concrete factual alternatives from the document (e.g., 'The document does not specify X. "
            "Instead, it specifies Y'), consider the question answered\n\n"
            "Set to 0.0 (False) if:\n"
            "- The ANSWER is off-topic or incomplete\n"
            "- The ANSWER misses the central point of the question\n"
            "- The ANSWER only states information is not in the document without providing alternatives\n"
            "- For multi-part questions, some parts are unanswered"
        ),
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
        threshold=threshold,
        evaluation_steps=[
            "Identify all significant parts of the QUESTION",
            "Check if each part is addressed in the ANSWER",
            "Determine if 'document does not provide' is supplemented with factual alternatives",
            "Return 1.0 if all parts addressed, 0.0 otherwise"
        ]
    )


def create_requires_additional_information_metric(threshold: float = 0.5) -> GEval:
    """
    Metric: requires_additional_information

    Evaluates if the answer explicitly requests or requires additional details
    from the user.

    Matches backend criteria:
    - True: ANSWER explicitly requests more details from the user
    - False: No additional information requested
    - Note: Do NOT set true merely because answer cannot be found in document
    """
    return GEval(
        name="requires_additional_information",
        criteria=(
            "Determine whether the ANSWER explicitly requests or requires additional details from the USER.\n\n"
            "Set to 1.0 (True) if the ANSWER contains:\n"
            "- Explicit requests: 'please provide', 'I need', 'could you share', 'what is the [missing field]?'\n"
            "- Statements indicating the question lacks necessary context that the user could supply\n"
            "- Requests for clarification like 'more context is needed to answer'\n\n"
            "Set to 0.0 (False) if:\n"
            "- The ANSWER does not request any additional information from the user\n"
            "- The ANSWER simply states information is not in the provided document (this is NOT a request for user input)\n\n"
            "IMPORTANT: Do NOT set to 1.0 merely because the answer cannot be found in the provided document. "
            "Only set to 1.0 if the ANSWER explicitly asks the user for more information."
        ),
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
        threshold=threshold,
        evaluation_steps=[
            "Search for explicit requests in the ANSWER ('please provide', 'I need', etc.)",
            "Check if ANSWER asks for clarification or more context from the user",
            "Distinguish between 'document does not have this' vs 'user needs to provide this'",
            "Return 1.0 if explicit request found, 0.0 otherwise"
        ]
    )


def create_is_speculative_metric(threshold: float = 0.5) -> GEval:
    """
    Metric: is_speculative

    Evaluates if the answer uses assumptions, hypothetical, or inferential language
    beyond facts.

    Matches backend criteria:
    - True: ANSWER uses speculative language (might, could, possibly, seems, etc.)
    - False: ANSWER strictly reports facts or explicitly states text lacks information
    """
    return GEval(
        name="is_speculative",
        criteria=(
            "Determine whether the ANSWER uses assumptions, hypothetical, or inferential language beyond facts.\n\n"
            "Set to 1.0 (True) if the ANSWER contains speculative/hedging words:\n"
            "- Uncertainty markers: 'might', 'could', 'possibly', 'probably', 'seems', 'appears'\n"
            "- Inferential language: 'assuming', 'I suspect', 'likely', 'would'\n"
            "- Conditional language: 'if', 'may', 'perhaps'\n\n"
            "Set to 0.0 (False) if:\n"
            "- The ANSWER strictly reports facts from the provided text\n"
            "- The ANSWER explicitly states the text lacks the information (e.g., 'The document does not provide this')\n"
            "- The ANSWER uses assertive, fact-based language without hedging\n\n"
            "Note: An answer that says 'The document does not provide this information' is NOT speculative unless "
            "it uses hedging words."
        ),
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
        threshold=threshold,
        evaluation_steps=[
            "Search for speculative/hedging words in the ANSWER",
            "Check for assumptions or hypothetical language",
            "Verify if ANSWER is fact-based or contains inference",
            "Return 1.0 if speculative language found, 0.0 otherwise"
        ]
    )


def create_is_confident_metric(threshold: float = 0.5) -> GEval:
    """
    Metric: is_confident

    Evaluates if the answer is phrased directly and assertively.

    Matches backend criteria:
    - True: ANSWER is phrased directly/assertively (Yes, No, The document states...)
    - False: ANSWER uses uncertain/hedging phrasing (seems like, I think, maybe)
    """
    return GEval(
        name="is_confident",
        criteria=(
            "Determine whether the ANSWER is phrased directly and assertively.\n\n"
            "Set to 1.0 (True) if the ANSWER uses:\n"
            "- Direct statements: 'Yes, X is...', 'No, the document states...', 'The text indicates...'\n"
            "- Assertive phrasing: 'The document specifies...', 'According to the text...'\n"
            "- Definitive tone even when reporting absence: 'The document does not provide this information' (assertive)\n\n"
            "Set to 0.0 (False) if the ANSWER uses:\n"
            "- Uncertain phrasing: 'It seems like', 'I think', 'It could be'\n"
            "- Hedging language: 'maybe', 'perhaps', 'possibly'\n"
            "- Tentative tone: 'It appears', 'It might be'\n\n"
            "Note: An assertive statement that reports 'document does not provide this' should be 1.0 (True) "
            "unless hedged with uncertain language."
        ),
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
        threshold=threshold,
        evaluation_steps=[
            "Analyze the tone and phrasing of the ANSWER",
            "Check for assertive vs uncertain language",
            "Determine if ANSWER is direct and definitive",
            "Return 1.0 if confident/assertive, 0.0 if uncertain/hedging"
        ]
    )


def create_all_backend_metrics(threshold: float = 0.5) -> list[GEval]:
    """
    Create all 4 backend evaluation metrics.

    Args:
        threshold: Threshold for all metrics (0.5 means >= 0.5 is considered True)

    Returns:
        List of 4 GEval metrics matching backend evaluation
    """
    return [
        create_is_question_answered_metric(threshold),
        create_requires_additional_information_metric(threshold),
        create_is_speculative_metric(threshold),
        create_is_confident_metric(threshold),
    ]
