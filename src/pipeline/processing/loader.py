# loader.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, and_
from sqlalchemy.sql import func
from typing import Dict, Any, List
import uuid

from src.pipeline.database.models import User, Problem, ProblemTopic, Submission
from src.pipeline.processing.schemas import UserSchema, ProblemSchema, TopicSchema, SubmissionSchema

async def load_data(session: AsyncSession, parsed_data: Dict[str, Any]):
    """
    Loads parsed data into the database using upsert logic.
    """
    user_schema: UserSchema = parsed_data['user']
    problem_schema: ProblemSchema = parsed_data['problem']
    topics_schemas: List[TopicSchema] = parsed_data['topics']
    submissions_schemas: List[SubmissionSchema] = parsed_data['submissions']

    # 1. Upsert User
    # Check if user exists by username
    stmt = select(User).where(User.username == user_schema.username)
    result = await session.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        # Update existing user
        if user_schema.real_name:
            existing_user.real_name = user_schema.real_name
        user_id = existing_user.id
    else:
        # Create new user
        new_user = User(
            username=user_schema.username,
            real_name=user_schema.real_name
        )
        session.add(new_user)
        await session.flush() # Flush to get the ID
        user_id = new_user.id

    # 2. Upsert Problem
    problem_values = {
        "id": problem_schema.question_id,
        "title": problem_schema.title,
        "title_slug": problem_schema.title_slug,
        "difficulty": problem_schema.difficulty,
        "content_html": problem_schema.content_html,
        "acceptance_rate": problem_schema.acceptance_rate,
        "total_accepted": problem_schema.total_accepted,
        "total_submissions": problem_schema.total_submissions,
        "raw_api_response": problem_schema.raw_api_response
    }

    stmt = insert(Problem).values(problem_values)
    stmt = stmt.on_conflict_do_update(
        index_elements=[Problem.id],
        set_={
            "title": stmt.excluded.title,
            "title_slug": stmt.excluded.title_slug,
            "difficulty": stmt.excluded.difficulty,
            "content_html": stmt.excluded.content_html,
            "acceptance_rate": stmt.excluded.acceptance_rate,
            "total_accepted": stmt.excluded.total_accepted,
            "total_submissions": stmt.excluded.total_submissions,
            "raw_api_response": stmt.excluded.raw_api_response,
            "updated_at": func.now()
        }
    )
    await session.execute(stmt)

    # 3. Insert Topics
    for topic in topics_schemas:
        # Check if topic exists for this problem
        # Optimization: We can use ON CONFLICT DO NOTHING directly without select
        stmt = insert(ProblemTopic).values(
            problem_id=problem_schema.question_id,
            topic_name=topic.name,
            topic_slug=topic.slug
        ).on_conflict_do_nothing()
        await session.execute(stmt)

    # 4. Insert Submissions
    for sub in submissions_schemas:
        sub_values = {
            "id": sub.id,
            "user_id": user_id,
            "problem_id": problem_schema.question_id,
            "status": sub.status,
            "status_code": sub.status_code,
            "language": sub.language,
            "runtime_ms": sub.runtime_ms,
            "runtime_percentile": sub.runtime_percentile,
            "memory_bytes": sub.memory_bytes,
            "memory_percentile": sub.memory_percentile,
            "code": sub.code,
            "timestamp": sub.timestamp,
            "attempt_number": sub.attempt_number,
            "runtime_error": sub.runtime_error,
            "compile_error": sub.compile_error,
            "raw_api_response": sub.raw_api_response
        }
        
        stmt = insert(Submission).values(sub_values).on_conflict_do_nothing()
        await session.execute(stmt)
            
    # 5. Update user stats
    problem_count_result = await session.execute(
        select(func.count(func.distinct(Submission.problem_id)))
        .where(Submission.user_id == user_id)
    )
    submission_count_result = await session.execute(
        select(func.count(Submission.id))
        .where(Submission.user_id == user_id)
    )

    existing_user_obj = await session.get(User, user_id)
    if existing_user_obj:
        existing_user_obj.total_problems = problem_count_result.scalar()
        existing_user_obj.total_submissions = submission_count_result.scalar()

    # Commit all changes
    await session.commit()
