class AuthenticationError(Exception):
    """
    Raised when LeetCode authentication fails.
    
    This can happen due to:
    - Invalid or expired cookies (LEETCODE_SESSION, CSRF_TOKEN)
    - Session rejection by the server (isSignedIn: false)
    - Cloudflare challenges blocking the request
    """
    def __init__(self, message: str, context: dict = None):
        super().__init__(message)
        self.context = context or {}
