import logging
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from pydantic import BaseModel, ValidationError
from typing import Optional, Dict
from src.pipeline.config import GRAPHQL_URL, DEFAULT_HEADERS

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# 1. Models
# -----------------------------------------------------------------------------

class UserProfile(BaseModel):
    username: str
    isSignedIn: bool
    isPremium: Optional[bool] = None

class UserStatusResponse(BaseModel):
    userStatus: UserProfile

class GraphQLResponse(BaseModel):
    data: UserStatusResponse

# -----------------------------------------------------------------------------
# 2. Exceptions
# -----------------------------------------------------------------------------

class AuthenticationError(Exception):
    """Raised when LeetCode authentication fails."""
    pass

# -----------------------------------------------------------------------------
# 3. Authenticator
# -----------------------------------------------------------------------------

QUERY_USER_STATUS = """
query globalData {
    userStatus {
        username
        isSignedIn
        isPremium
    }
}
"""

class LeetCodeAuthenticator:
    """
    Handles authentication with LeetCode using session cookies.
    """

    def __init__(self, session_id: str, csrf_token: str, cf_clearance: str):
        self.session_id = session_id
        self.csrf_token = csrf_token
        self.cf_clearance = cf_clearance
        
        if not all([session_id, csrf_token, cf_clearance]):
            raise ValueError("Missing one or more required credentials: LEETCODE_SESSION, CSRF_TOKEN, CF_CLEARANCE")

    def _get_cookies(self) -> Dict[str, str]:
        return {
            "LEETCODE_SESSION": self.session_id,
            "csrftoken": self.csrf_token,
            "cf_clearance": self.cf_clearance
        }

    def _get_headers(self) -> Dict[str, str]:
        headers = DEFAULT_HEADERS.copy()
        headers["X-CSRFToken"] = self.csrf_token
        return headers

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.RequestError),
        reraise=True
    )
    def validate(self) -> str:
        """
        Validates the credentials against LeetCode API.
        Returns the username if successful, raises AuthenticationError otherwise.
        """
        logger.debug("Validating LeetCode credentials...")
        
        with httpx.Client(http2=True, headers=self._get_headers(), cookies=self._get_cookies()) as client:
            try:
                response = client.post(
                    GRAPHQL_URL,
                    json={
                        "query": QUERY_USER_STATUS,
                        "operationName": "globalData"
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                
                # Parse with Pydantic
                data = GraphQLResponse.model_validate_json(response.content)
                status = data.data.userStatus
                
                if not status.isSignedIn:
                    raise AuthenticationError("LeetCode rejected the session (isSignedIn=False). Check your cookies.")
                
                logger.info(f"Authentication successful for user: {status.username}")
                return status.username

            except (httpx.HTTPStatusError, ValidationError) as e:
                logger.error(f"Authentication validation failed: {e}")
                raise AuthenticationError(f"Validation failed: {str(e)}") from e
            except httpx.RequestError as e:
                logger.warning(f"Network error during auth check: {e}")
                raise

    def get_client(self) -> httpx.Client:
        """
        Returns a configured httpx.Client ready for requests.
        The caller is responsible for closing the client (context manager recommended).
        """
        return httpx.Client(
            http2=True,
            headers=self._get_headers(),
            cookies=self._get_cookies(),
            timeout=15.0,
            follow_redirects=True
        )
