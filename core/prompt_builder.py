"""
core/prompt_builder.py

Combine job description + retrieved chunks + user request into prompts.

Every builder returns a (system_prompt, user_prompt) tuple.
"""

from __future__ import annotations

SYSTEM_PROMPT = (
    "You are an expert technical recruiter. Evaluate candidates ONLY using the "
    "evidence provided (job description and resume excerpts). Never invent skills "
    "or experience. When the evidence does not cover something, say so explicitly "
    "rather than guessing. Be concise, specific, and fair."
)


def build_chat_prompt(jd: str, question: str, context: str) -> tuple[str, str]:
    user = (
        f"JOB DESCRIPTION:\n{_or_none(jd)}\n\n"
        f"RELEVANT RESUME EXCERPTS:\n{context}\n\n"
        f"QUESTION:\n{question}\n\n"
        "Answer using only the excerpts above. Cite candidate names where relevant."
    )
    return SYSTEM_PROMPT, user


def build_ranking_prompt(jd: str, per_candidate_context: str) -> tuple[str, str]:
    user = (
        f"JOB DESCRIPTION:\n{_or_none(jd)}\n\n"
        f"CANDIDATE EVIDENCE (grouped per candidate):\n{per_candidate_context}\n\n"
        "Rank these candidates from best to worst fit for the role. For each, give:\n"
        "  1. Rank and candidate name\n"
        "  2. A fit score out of 100\n"
        "  3. A 1-2 sentence justification grounded in their evidence\n"
        "End with a one-line overall recommendation."
    )
    return SYSTEM_PROMPT, user


def build_skill_gap_prompt(jd: str, name: str, context: str) -> tuple[str, str]:
    user = (
        f"JOB DESCRIPTION:\n{_or_none(jd)}\n\n"
        f"CANDIDATE: {name}\n"
        f"RESUME EXCERPTS:\n{context}\n\n"
        "Identify this candidate's skill gaps versus the job description. List:\n"
        "  - Matched requirements (skills they clearly have)\n"
        "  - Missing / unproven requirements\n"
        "  - Suggested areas to probe in an interview"
    )
    return SYSTEM_PROMPT, user


def build_interview_prompt(jd: str, name: str, context: str) -> tuple[str, str]:
    user = (
        f"JOB DESCRIPTION:\n{_or_none(jd)}\n\n"
        f"CANDIDATE: {name}\n"
        f"RESUME EXCERPTS:\n{context}\n\n"
        "Generate 6-8 tailored interview questions for this candidate. Mix:\n"
        "  - Technical questions probing claimed skills\n"
        "  - Questions targeting gaps or unproven requirements\n"
        "  - At least one behavioural question\n"
        "Number them and keep each question on one line."
    )
    return SYSTEM_PROMPT, user


def build_report_prompt(jd: str, title: str, per_candidate_context: str) -> tuple[str, str]:
    user = (
        f"REPORT TITLE: {title}\n\n"
        f"JOB DESCRIPTION:\n{_or_none(jd)}\n\n"
        f"CANDIDATE EVIDENCE (grouped per candidate):\n{per_candidate_context}\n\n"
        "Write a concise hiring report with these sections:\n"
        "  1. Role summary\n"
        "  2. Candidate pool overview\n"
        "  3. Ranked shortlist with scores and rationale\n"
        "  4. Key risks / gaps across the pool\n"
        "  5. Recommendation"
    )
    return SYSTEM_PROMPT, user


def _or_none(text: str) -> str:
    return text.strip() if text and text.strip() else "(no job description provided)"
