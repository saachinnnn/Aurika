import logging # This is the standard library for logging in Python. Basically for debugging and error tracking.
import httpx # Modern HTTP client for Python, supports async and sync requests.
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type # Retry logic for handling transient errors.
from pydantic import BaseModel, ValidationError # Data validation and settings management using Python type annotations.
from typing import Optional, Dict # Type hinting for better code clarity.
from src.pipeline.config import GRAPHQL_URL, DEFAULT_HEADERS # Graph endpoint and default headers for LeetCode API.
from .exceptions import AuthenticationError # Custom exception for authentication errors.

logger = logging.getLogger(__name__)
# Creating a logger instance.
# -----------------------------------------------------------------------------
# Models
# -----------------------------------------------------------------------------

class UserProfile(BaseModel):
    username: str
    isSignedIn: bool
    isPremium: Optional[bool] = None # This is seriously not necessary at all.

class UserStatusResponse(BaseModel):
    userStatus: UserProfile

class GraphQLResponse(BaseModel):
    data: UserStatusResponse

# -----------------------------------------------------------------------------
# Constants
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

# -----------------------------------------------------------------------------
# Authenticator
# -----------------------------------------------------------------------------

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
    # The code @retry means the following.
    def validate(self) -> str:
        """
        Validates the credentials against LeetCode API.
        Returns the username if successful, raises AuthenticationError otherwise.
        """
        logger.debug("Validating LeetCode credentials...")
        
        with httpx.Client(http2=False, headers=self._get_headers(), cookies=self._get_cookies()) as client:
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
                # Note: LeetCode might return 200 OK with "errors" in JSON
                json_data = response.json()
                if "errors" in json_data:
                    raise AuthenticationError(f"GraphQL Error: {json_data['errors']}")
                
                data = GraphQLResponse.model_validate(json_data) # model_validate(): Ensures response matches expected structure
                status = data.data.userStatus # Accessing nested data for userstatus.
                
                # The below occurs if the session is invalid or if the credentials are wrong.
                if not status.isSignedIn:
                    raise AuthenticationError(
                        "LeetCode rejected the session (isSignedIn=False). Check your cookies.",
                        context={"username": status.username}
                    )
                
                logger.info(f"Authentication successful for user: {status.username}")
                return status.username

            except (httpx.HTTPStatusError, ValidationError) as e: # Validation error is the data from the GraphQL response not matching the expected schema.
                logger.error(f"Authentication validation failed: {e}")
                raise AuthenticationError(f"Validation failed: {str(e)}") from e # This is the custom class we have created to handle authentication errors.
            except httpx.RequestError as e:
                logger.warning(f"Network error during auth check: {e}")
                raise

    def get_client(self) -> httpx.AsyncClient:
        """
        Returns a configured httpx.AsyncClient ready for requests.
        The caller is responsible for closing the client (context manager recommended).
        """
        return httpx.AsyncClient(
            http2=False,
            headers=self._get_headers(),
            cookies=self._get_cookies(),
            timeout=15.0,
            follow_redirects=True
        )
