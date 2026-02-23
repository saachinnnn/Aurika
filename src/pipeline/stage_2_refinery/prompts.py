from typing import List, Dict, Any, Optional
from src.pipeline.database.models import Submission, Problem, ProblemTopic

class PromptBuilder:
    @staticmethod
    def build_analysis_prompt(
        submission: Submission,
        problem: Problem,
        topics: List[ProblemTopic],
        next_attempts: List[Submission] = []
    ) -> str:
        """
        Constructs the prompt for Claude to analyze a submission.
        """
        
        # 1. Problem Context
        topic_names = ", ".join([t.topic_name for t in topics])
        context = f"""
Problem: {problem.title} ({problem.difficulty})
Tags: {topic_names}
Description:
{problem.content_html} 
(Note: The description above is HTML, please focus on the algorithmic requirements.)
"""

        # 2. Submission Details
        status_info = f"Status: {submission.status}"
        if submission.status != "Accepted":
            status_info += f" (Runtime Error: {submission.runtime_error})" if submission.runtime_error else ""
        
        code_block = f"""
CODE (Language: {submission.language}):
```
{submission.code}
```
"""

        # 3. History (for failed attempts)
        history_block = ""
        if submission.status != "Accepted" and next_attempts:
            history_block = "\n\nSUBSEQUENT ATTEMPTS (For Context):\n"
            for i, attempt in enumerate(next_attempts):
                history_block += f"""
--- Next Attempt {i+1} ({attempt.status}) ---
```
{attempt.code}
```
"""
            history_block += "\n(Use these subsequent attempts to understand what the user was trying to fix or how they eventually solved it.)\n"

        # 4. Instructions
        instructions = """
You are an expert coding interview coach. Analyze the provided submission.

OUTPUT FORMAT:
You must return a JSON object matching this structure:
{
    "approach_name": "string",
    "approach_category": "string",
    "time_complexity": "string",
    "space_complexity": "string",
    "is_optimal": boolean,
    "interview_score": float (1-10, null if failed),
    "mistake_type": "string" (null if accepted),
    "mistake_detail": "string" (null if accepted),
    "analysis_summary": "string"
}

MISTAKE CATEGORIES (Choose one if failed, else null):
- logic_inversion: comparison or condition is backwards
- boundary_error: off-by-one, wrong loop condition
- wrong_approach: fundamentally wrong algorithm
- missing_edge_case: doesn't handle empty input, single element, etc.
- tle_brute_force: correct but too slow (brute force)
- tle_optimization: right algorithm but implementation is slow
- syntax_error: language mistake, typo
- incomplete: solution not finished
- wrong_data_structure: right idea, wrong data structure choice
- runtime_error: index out of bounds, null pointer, etc.

GUIDELINES:
- For Accepted submissions, provide an interview_score and set mistake fields to null.
- For Failed submissions, analyze the mistake. Use the 'next attempts' (if provided) to pinpoint exactly what was wrong in this version.
- Be concise in the analysis_summary.
"""

        return f"{context}\n{status_info}\n{code_block}\n{history_block}\n{instructions}"
