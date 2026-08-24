from .evaluator import evaluate_output, validate_output
from .providers import get_provider
from .rag import retriever


class ContentAgent:
    """Simple plan -> retrieve -> generate -> validate -> refine agent runtime."""

    def run(
        self,
        prompt: str,
        provider: str | None = None,
        use_rag: bool = True,
        temperature: float = 0.4,
    ):
        context = ""
        if use_rag:
            docs = retriever.search(prompt)
            if docs:
                context = "\n\nKnowledge context:\n" + "\n".join(
                    f"[{doc.title}] {doc.content}" for doc in docs
                )

        composed = (
            f"User request:\n{prompt}\n"
            f"{context}\n\n"
            "Produce polished, production-ready content. Do not reveal internal reasoning."
        )
        llm = get_provider(provider)
        output, provider_name, model = llm.generate(composed, temperature)
        validate_output(output)
        score = evaluate_output(prompt, output)

        if score < 0.25:
            refined = composed + "\nImprove relevance, specificity, and structure before answering."
            output, provider_name, model = llm.generate(refined, min(temperature, 0.3))
            validate_output(output)
            score = evaluate_output(prompt, output)

        return output, provider_name, model, score


agent = ContentAgent()
