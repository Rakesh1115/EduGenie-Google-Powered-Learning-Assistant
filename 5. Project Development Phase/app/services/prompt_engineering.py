from typing import Optional


def qa_prompt(question: str, context: Optional[str] = None) -> str:
    ctx = f"\nContext:\n{context}\n" if context else ""
    prompt = (
        "You are an expert tutor. Answer the question succinctly and clearly in Markdown. "
        "Provide a short direct answer, a brief explanation, and any relevant examples or formulas. "
        "When appropriate, include a 2-3 bullet list of follow-up questions or resources.\n\n"
        f"Question: {question}\n"
        f"{ctx}"
        "Produce structured markdown with headings: 'Answer', 'Explanation', 'Examples', 'Next Steps' (when relevant)."
    )
    return prompt


def explain_prompt(topic: str, level: str = "beginner") -> str:
    prompt = (
        "You are an expert instructor. Explain the following concept to a learner at the requested level. "
        "Use clear sections in Markdown: 'Overview', 'Key Ideas', 'Step-by-step Explanation', and 'Examples'. "
        "Finish with 3 practice prompts the learner can try.\n\n"
        f"Concept: {topic}\nLevel: {level}\n"
    )
    return prompt


def quiz_prompt(topic: str, num_questions: int = 5, difficulty: str = "medium") -> str:
    prompt = (
        "You are a quiz generator. Produce a quiz in Markdown. Each question should include: 'Question', 'Choices' (A-D), and 'Answer' on a separate line. "
        "Also include a short explanation for the correct answer. Output the quiz as a numbered list.\n\n"
        f"Topic: {topic}\nNumber of questions: {num_questions}\nDifficulty: {difficulty}\n"
    )
    return prompt


def summarize_prompt(text: str, max_length: int = 200) -> str:
    prompt = (
        "You are an advanced summarizer. Produce a concise summary in Markdown with a short title, a 2-3 sentence summary, and 3 bullet takeaways. "
        f"Keep the summary under {max_length} characters when possible.\n\n"
        f"Text:\n{text}\n"
    )
    return prompt


def roadmap_prompt(subject: str, goals: Optional[str] = None, duration_weeks: int = 8) -> str:
    goals_text = f"Goals: {goals}\n" if goals else ""
    prompt = (
        "You are an instructional designer. Produce a learning roadmap in Markdown with weeks as headings. "
        "For each week include objectives, recommended activities, and suggested resources. Keep the plan practical and scaffolded.\n\n"
        f"Subject: {subject}\n{goals_text}Duration (weeks): {duration_weeks}\n"
    )
    return prompt
