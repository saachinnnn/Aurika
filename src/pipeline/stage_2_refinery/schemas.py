from typing import Optional, List
from pydantic import BaseModel, Field

class AnalysisOutput(BaseModel):
    """
    Structured output for submission analysis from Claude.
    """
    approach_name: str = Field(description="Name of the algorithmic approach used (e.g., 'Binary Search', 'DFS')")
    approach_category: str = Field(description="Broader category of the approach (e.g., 'Two Pointers', 'Dynamic Programming')")
    time_complexity: str = Field(description="Time complexity in Big O notation (e.g., 'O(n)', 'O(log n)')")
    space_complexity: str = Field(description="Space complexity in Big O notation (e.g., 'O(1)', 'O(n)')")
    is_optimal: bool = Field(description="Whether this solution is considered optimal for the problem")
    interview_score: Optional[float] = Field(default=None, description="Score from 1-10 for code quality and correctness (only for Accepted solutions)")
    mistake_type: Optional[str] = Field(default=None, description="Category of mistake if failed (e.g., 'boundary_error', 'logic_inversion')")
    mistake_detail: Optional[str] = Field(default=None, description="Specific details about the mistake")
    analysis_summary: str = Field(description="Brief summary of the analysis")
