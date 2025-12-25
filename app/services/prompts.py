ANSWER_SYSTEM = (
    "You are a grounded enterprise assistant. Answer ONLY using the provided context. "
    "If the context is insufficient, say so clearly. Do not invent facts."
)

def build_answer_prompt(question: str, contexts: list[str]) -> str:
    joined = "\n\n---\n\n".join([f"Context #{i+1}:\n{c}" for i, c in enumerate(contexts)])
    return f"""Question:
{question}

Context:
{joined}

Rules:
- Use only the context above.
- If incomplete, explicitly say what is missing.
- When you make a claim, add a citation like [Context #2].
- Keep the answer concise but complete.
"""

def build_completeness_prompt(question: str, answer: str, contexts: list[str]) -> str:
    joined = "\n\n---\n\n".join([f"Context #{i+1}:\n{c}" for i, c in enumerate(contexts)])
    return f"""You are verifying whether the answer is fully supported by the context.

Question:
{question}

Answer Draft:
{answer}

Context Snippets:
{joined}

Return STRICT JSON with keys:
- confidence: number between 0 and 1
- missing_info: array of strings describing what is required to answer fully
- reasoning: short string
"""

def build_enrichment_prompt(missing_info: list[str]) -> str:
    missing = "\n".join([f"- {m}" for m in missing_info]) if missing_info else "- (none)"
    return f"""Given this missing information list, propose enrichment steps.

Missing Info:
{missing}

Return STRICT JSON with key:
- enrichment_suggestions: array of objects with:
  - type: "document" | "data" | "action" | "external_source"
  - suggestion: string
"""
