import json
from typing import List, Dict, Any, Tuple
from pathlib import Path

from src.pipeline.processing.schemas import UserSchema, ProblemSchema, TopicSchema, SubmissionSchema

class DataParser:
    def __init__(self):
        pass

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parses a LeetCode JSON file and returns a dictionary containing
        validated Pydantic models for User, Problem, Topics, and Submissions.
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 1. Extract User
        # The user data is embedded in the submissions.
        # Check if submissions list is not empty
        submissions_data = data.get('submissions', [])
        if submissions_data:
            first_submission = submissions_data[0]
            user_data = first_submission.get('user', {})
            user = UserSchema(
                username=user_data.get('username', 'unknown'),
                real_name=user_data.get('profile', {}).get('realName')
            )
        else:
            # Fallback if no submissions (unlikely for valid files but possible)
            # We might need to infer username from path or just use unknown
            user = UserSchema(username='unknown')

        # 2. Extract Problem
        problem_metadata = data.get('problem_metadata', {})
        # The schema now handles stats parsing internally via model_validator
        problem = ProblemSchema(**problem_metadata)

        # 3. Extract Topics
        topics_data = problem_metadata.get('topicTags', [])
        topics = [TopicSchema(slug=t.get('slug'), name=t.get('name')) for t in topics_data]

        # 4. Extract Submissions
        
        # Sort by timestamp ascending to calculate attempt_number
        # Timestamps in JSON are Unix timestamps (integers or strings)
        submissions_data.sort(key=lambda x: int(x.get('timestamp', 0)))

        submissions = []
        for idx, sub_data in enumerate(submissions_data):
            # Create SubmissionSchema
            # Note: We are passing the raw sub_data as raw_api_response
            submission = SubmissionSchema(
                id=sub_data.get('id'),
                statusDisplay=sub_data.get('statusDisplay'),
                statusCode=sub_data.get('statusCode'),
                lang=sub_data.get('lang'), # Schema validator handles dict extraction
                runtime=sub_data.get('runtime'),
                runtimePercentile=sub_data.get('runtimePercentile'),
                memory=sub_data.get('memory'),
                memoryPercentile=sub_data.get('memoryPercentile'),
                code=sub_data.get('code'),
                timestamp=sub_data.get('timestamp'),
                attempt_number=idx + 1,
                runtimeError=sub_data.get('runtimeError'),
                compileError=sub_data.get('compileError'),
                raw_api_response=sub_data
            )
            submissions.append(submission)

        return {
            "user": user,
            "problem": problem,
            "topics": topics,
            "submissions": submissions
        }

def parse_file(file_path: str) -> Dict[str, Any]:
    parser = DataParser()
    return parser.parse_file(file_path)
