import re


def evaluate_output(prompt: str, output: str) -> float:
    if not output.strip():
        return 0.0
    words = output.split()
    length_score = min(len(words) / 180, 1.0)
    prompt_terms = set(re.findall(r"\w+", prompt.lower()))
    output_terms = set(re.findall(r"\w+", output.lower()))
    relevance = min(len(prompt_terms & output_terms) / max(len(prompt_terms), 1) * 2, 1.0)
    structure = 1.0 if any(mark in output for mark in ("\n", ":", "- ", "1.")) else 0.65
    return round(0.3 * length_score + 0.45 * relevance + 0.25 * structure, 3)


def validate_output(output: str) -> None:
    if len(output.strip()) < 20:
        raise ValueError("Generated output failed minimum quality validation")
    if output.strip().lower().startswith(("i cannot", "i'm unable")) and len(output) < 160:
        raise ValueError("Generated output appears to be a refusal rather than requested content")
