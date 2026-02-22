# schemas.py
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import json
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict

# -----------------------------------------------------------------------------
# 1. User Schema
# -----------------------------------------------------------------------------
class UserSchema(BaseModel):
    username: str
    real_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# -----------------------------------------------------------------------------
# 2. Topic Schema
# -----------------------------------------------------------------------------
class TopicSchema(BaseModel):
    slug: str
    name: str
    
    model_config = ConfigDict(from_attributes=True)

# -----------------------------------------------------------------------------
# 3. Problem Schema
# -----------------------------------------------------------------------------
class ProblemSchema(BaseModel):
    question_id: str = Field(alias="questionId")
    title: str
    title_slug: str = Field(alias="titleSlug")
    difficulty: str
    content_html: Optional[str] = Field(default=None, alias="content")
    
    # Stats fields extracted from the JSON string in "stats"
    acceptance_rate: Optional[float] = None
    total_accepted: Optional[int] = None
    total_submissions: Optional[int] = None
    
    # Raw API response to store everything else
    raw_api_response: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @model_validator(mode='before')
    @classmethod
    def parse_stats_and_populate(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Auto-populate raw_api_response if not present
            if "raw_api_response" not in data:
                 data["raw_api_response"] = data.copy()
            # Parse stats string if present
            stats_str = data.get("stats")
            if stats_str and isinstance(stats_str, str):
                try:
                    stats = json.loads(stats_str)
                    
                    # Populate fields if not explicitly provided
                    if data.get("acceptance_rate") is None:
                        ac_rate_raw = stats.get("acRate")
                        if ac_rate_raw:
                            try:
                                # Handle "60.4%" -> 60.4
                                data["acceptance_rate"] = float(str(ac_rate_raw).strip('%'))
                            except ValueError:
                                data["acceptance_rate"] = 0.0
                    
                    if data.get("total_accepted") is None:
                        data["total_accepted"] = stats.get("totalAcceptedRaw")
                        
                    if data.get("total_submissions") is None:
                        data["total_submissions"] = stats.get("totalSubmissionRaw")
                        
                except json.JSONDecodeError:
                    pass
            
            

        return data

# -----------------------------------------------------------------------------
# 4. Submission Schema
# -----------------------------------------------------------------------------
class SubmissionSchema(BaseModel):
    id: str
    # We don't include user_id and problem_id here as they are foreign keys 
    # determined by the context, but we can include them if we want to validate 
    # the full object structure.
    
    status: str = Field(alias="statusDisplay")
    status_code: int = Field(alias="statusCode")
    language: str = Field(alias="lang") # We'll need to extract name from the lang dict
    
    runtime_ms: Optional[int] = Field(default=None, alias="runtime") # "0" or "N/A" might need handling
    runtime_percentile: Optional[float] = Field(default=None, alias="runtimePercentile")
    
    memory_bytes: Optional[int] = Field(default=None, alias="memory")
    memory_percentile: Optional[float] = Field(default=None, alias="memoryPercentile")
    
    code: str
    timestamp: datetime
    
    attempt_number: int
    
    runtime_error: Optional[str] = Field(default=None, alias="runtimeError")
    compile_error: Optional[str] = Field(default=None, alias="compileError")
    
    raw_api_response: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @field_validator("language", mode="before")
    @classmethod
    def extract_language(cls, v: Any) -> str:
        if isinstance(v, dict):
            return v.get("name", "unknown")
        return v

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, v: Any) -> datetime:
        if isinstance(v, (int, str)):
            try:
                # LeetCode timestamps are Unix timestamps (seconds)
                return datetime.fromtimestamp(int(v), tz=timezone.utc)
            except ValueError:
                pass
        return v
    
    @field_validator("runtime_ms", "memory_bytes", mode="before")
    @classmethod
    def parse_metrics(cls, v: Any) -> Optional[int]:
        if v == "N/A" or v is None:
            return None
        try:
            return int(v)
        except (ValueError, TypeError):
            return None
