import asyncio
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.pipeline.database.connection import AsyncSessionLocal
from src.pipeline.database.models import Submission, SubmissionAnalysis, Problem, ProblemTopic
from src.pipeline.stage_2_refinery.llm_client import ClaudeClient
from src.pipeline.stage_2_refinery.prompts import PromptBuilder
from src.pipeline.stage_2_refinery.schemas import AnalysisOutput

class SubmissionAnalyzer:
    def __init__(self):
        self.llm_client = ClaudeClient()

    async def process_unanalyzed_submissions(self, batch_size: int = 10):
        """
        Fetches unanalyzed submissions and processes them.
        """
        submission_ids = []
        async with AsyncSessionLocal() as session:
            # 1. Fetch unanalyzed submissions
            # Left join to find submissions without an analysis entry
            stmt = (
                select(Submission.id)
                .outerjoin(SubmissionAnalysis, Submission.id == SubmissionAnalysis.submission_id)
                .where(SubmissionAnalysis.submission_id == None)
                .limit(batch_size)
            )
            result = await session.execute(stmt)
            submission_ids = result.scalars().all()

        if not submission_ids:
            print("No unanalyzed submissions found.")
            return

        print(f"Found {len(submission_ids)} submissions to analyze.")

        # Process each submission in its own transaction/session to avoid long-running transactions
        for sub_id in submission_ids:
            async with AsyncSessionLocal() as session:
                await self._analyze_single_submission(session, sub_id)

    async def _analyze_single_submission(self, session: AsyncSession, submission_id: int):
        try:
            submission = await session.get(Submission, submission_id)
            if not submission:
                return

            print(f"Analyzing submission {submission.id} ({submission.status})...")
            
            # 2. Fetch context (Problem, Topics)
            problem = await session.get(Problem, submission.problem_id)
            
            topic_stmt = select(ProblemTopic).where(ProblemTopic.problem_id == submission.problem_id)
            topic_res = await session.execute(topic_stmt)
            topics = topic_res.scalars().all()

            # 3. Fetch history (if failed)
            next_attempts = []
            if submission.status != "Accepted":
                history_stmt = (
                    select(Submission)
                    .where(
                        and_(
                            Submission.problem_id == submission.problem_id,
                            Submission.user_id == submission.user_id,
                            Submission.attempt_number > submission.attempt_number
                        )
                    )
                    .order_by(Submission.attempt_number.asc())
                    .limit(2)
                )
                history_res = await session.execute(history_stmt)
                next_attempts = history_res.scalars().all()

            # 4. Build Prompt
            prompt = PromptBuilder.build_analysis_prompt(submission, problem, topics, next_attempts)

            # 5. Call LLM
            analysis: AnalysisOutput = await self.llm_client.analyze_submission(prompt)

            # 6. Save Result
            db_analysis = SubmissionAnalysis(
                submission_id=submission.id,
                approach_name=analysis.approach_name,
                approach_category=analysis.approach_category,
                time_complexity=analysis.time_complexity,
                space_complexity=analysis.space_complexity,
                is_optimal=analysis.is_optimal,
                interview_score=analysis.interview_score,
                mistake_type=analysis.mistake_type,
                mistake_detail=analysis.mistake_detail,
                analysis_summary=analysis.analysis_summary,
                llm_model_used="claude-sonnet-4-20250514"
            )
            session.add(db_analysis)
            await session.commit()
            print(f"-> Saved analysis for {submission.id}")

        except Exception as e:
            print(f"Error analyzing submission {submission.id}: {e}")
            await session.rollback()

async def run_analyzer():
    analyzer = SubmissionAnalyzer()
    await analyzer.process_unanalyzed_submissions()

if __name__ == "__main__":
    # For testing directly
    asyncio.run(run_analyzer())
