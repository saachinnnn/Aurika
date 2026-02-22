import uuid
from datetime import datetime
from typing import List, Optional, Any
from sqlalchemy import (
    String, Integer, Float, Boolean, Text, DateTime, ForeignKey, JSON, BigInteger, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.pipeline.database.connection import Base

# -----------------------------------------------------------------------------
# 1. User Table
# -----------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    real_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Auth / Session (Encrypted in real app, keeping simple for now as per plan)
    leetcode_session: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    leetcode_csrf: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Computed Stats
    level: Mapped[Optional[str]] = mapped_column(String, nullable=True) # beginner, intermediate, advanced
    total_problems: Mapped[int] = mapped_column(Integer, default=0)
    total_submissions: Mapped[int] = mapped_column(Integer, default=0)
    
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    submissions: Mapped[List["Submission"]] = relationship(back_populates="user")


# -----------------------------------------------------------------------------
# 2. Problem Table
# -----------------------------------------------------------------------------
class Problem(Base):
    __tablename__ = "problems"

    id: Mapped[str] = mapped_column(String, primary_key=True) # LeetCode questionId
    title: Mapped[str] = mapped_column(String, nullable=False)
    title_slug: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    difficulty: Mapped[str] = mapped_column(String, nullable=False) # Easy, Medium, Hard
    content_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Parsed Stats
    acceptance_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_accepted: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    total_submissions: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    
    raw_api_response: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    submissions: Mapped[List["Submission"]] = relationship(back_populates="problem")
    topics: Mapped[List["ProblemTopic"]] = relationship(back_populates="problem")


# -----------------------------------------------------------------------------
# 3. Problem Topics (Join Table / Entity)
# -----------------------------------------------------------------------------
class ProblemTopic(Base):
    __tablename__ = "problem_topics"

    problem_id: Mapped[str] = mapped_column(ForeignKey("problems.id"), primary_key=True)
    topic_name: Mapped[str] = mapped_column(String, primary_key=True)
    topic_slug: Mapped[str] = mapped_column(String, nullable=False, index=True)

    # Relationships
    problem: Mapped["Problem"] = relationship(back_populates="topics")


# -----------------------------------------------------------------------------
# 4. Submission Table
# -----------------------------------------------------------------------------
class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[str] = mapped_column(String, primary_key=True) # LeetCode submissionId
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    problem_id: Mapped[str] = mapped_column(ForeignKey("problems.id"), nullable=False, index=True)
    
    status: Mapped[str] = mapped_column(String, nullable=False) # Accepted, Wrong Answer, etc.
    status_code: Mapped[int] = mapped_column(Integer, nullable=False) # 10 = AC, 11 = WA
    language: Mapped[str] = mapped_column(String, nullable=False)
    
    runtime_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    runtime_percentile: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    memory_bytes: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    memory_percentile: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    code: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False) # Computed
    
    runtime_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    compile_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    raw_api_response: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user: Mapped["User"] = relationship(back_populates="submissions")
    problem: Mapped["Problem"] = relationship(back_populates="submissions")
    analysis: Mapped[Optional["SubmissionAnalysis"]] = relationship(back_populates="submission", uselist=False)
    
    # Composite Index for common query: "Get this user's submissions for this problem"
    __table_args__ = (
        Index("ix_submissions_user_problem", "user_id", "problem_id"), 
    )


# -----------------------------------------------------------------------------
# 5. Submission Analysis (LLM Output)
# -----------------------------------------------------------------------------
class SubmissionAnalysis(Base):
    __tablename__ = "submission_analyses"

    submission_id: Mapped[str] = mapped_column(ForeignKey("submissions.id"), primary_key=True)
    
    approach_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    approach_category: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    time_complexity: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    space_complexity: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    is_optimal: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    interview_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    mistake_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    mistake_detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    analysis_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    llm_model_used: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    analyzed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    submission: Mapped["Submission"] = relationship(back_populates="analysis")


# -----------------------------------------------------------------------------
# 6. Topic Prerequisites (Static Knowledge Graph)
# -----------------------------------------------------------------------------
class TopicPrerequisite(Base):
    __tablename__ = "topic_prerequisites"

    topic_slug: Mapped[str] = mapped_column(String, primary_key=True)
    prerequisite_of_slug: Mapped[str] = mapped_column(String, primary_key=True)
