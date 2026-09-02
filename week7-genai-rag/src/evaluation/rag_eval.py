import re


STOP_WORDS = {
    "the",
    "is",
    "are",
    "a",
    "an",
    "what",
    "which",
    "who",
    "how",
    "to",
    "of",
    "in",
    "on",
    "for",
    "and"
}


def tokenize(text):
    tokens = re.findall(
        r"\b\w+\b",
        text.lower()
    )

    normalized_tokens = set()

    for token in tokens:

        if token in STOP_WORDS:
            continue

        # Simple plural normalization
        if token.endswith("s") and len(token) > 3:
            token = token[:-1]

        normalized_tokens.add(token)

    return normalized_tokens


def context_match_score(question, context):
    question_tokens = tokenize(question)
    context_tokens = tokenize(context)

    if not question_tokens:
        return 0.0

    common_tokens = question_tokens.intersection(
        context_tokens
    )

    score = len(common_tokens) / len(
        question_tokens
    )

    return round(score, 3)


def faithfulness_score(answer, context):
    answer_tokens = tokenize(answer)
    context_tokens = tokenize(context)

    if not answer_tokens:
        return 0.0

    common_tokens = answer_tokens.intersection(
        context_tokens
    )

    score = len(common_tokens) / len(
        answer_tokens
    )

    return round(score, 3)


def detect_hallucination(
    answer,
    context,
    threshold=0.5
):
    faithfulness = faithfulness_score(
        answer,
        context
    )

    return faithfulness < threshold


def confidence_score(
    question,
    answer,
    context
):
    context_score = context_match_score(
        question,
        context
    )

    faithfulness = faithfulness_score(
        answer,
        context
    )

    confidence = (
        context_score + faithfulness
    ) / 2

    return round(confidence, 3)


def evaluate_rag(
    question,
    answer,
    context
):
    context_score = context_match_score(
        question,
        context
    )

    faithfulness = faithfulness_score(
        answer,
        context
    )

    hallucination = detect_hallucination(
        answer,
        context
    )

    confidence = confidence_score(
        question,
        answer,
        context
    )

    return {
        "context_match_score": context_score,
        "faithfulness_score": faithfulness,
        "hallucination_detected": hallucination,
        "confidence_score": confidence
    }


def needs_refinement(
    evaluation,
    confidence_threshold=0.6
):
    if evaluation["hallucination_detected"]:
        return True

    if (
        evaluation["confidence_score"]
        < confidence_threshold
    ):
        return True

    return False


if __name__ == "__main__":

    question = (
        "What is the employee leave policy?"
    )

    context = (
        "Employees are entitled to "
        "24 paid leave days per year."
    )

    answer = (
        "Employees receive "
        "24 paid leave days per year."
    )

    evaluation = evaluate_rag(
        question,
        answer,
        context
    )

    print("========== RAG EVALUATION ==========")

    print(
        "Context Match Score:",
        evaluation["context_match_score"]
    )

    print(
        "Faithfulness Score:",
        evaluation["faithfulness_score"]
    )

    print(
        "Hallucination Detected:",
        evaluation["hallucination_detected"]
    )

    print(
        "Confidence Score:",
        evaluation["confidence_score"]
    )

    print(
        "Needs Refinement:",
        needs_refinement(evaluation)
    )