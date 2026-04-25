"""ez-ragify SDK exceptions."""

from __future__ import annotations
from typing import Any, Optional


class EzRagifyError(Exception):
    """Base exception for all ez-ragify SDK errors."""

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        body: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.body = body

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, status_code={self.status_code})"


class AuthenticationError(EzRagifyError):
    """Raised on 401 Unauthorized responses."""


class PermissionError(EzRagifyError):
    """Raised on 403 Forbidden responses."""


class NotFoundError(EzRagifyError):
    """Raised on 404 Not Found responses."""


class ValidationError(EzRagifyError):
    """Raised on 422 Unprocessable Entity responses."""


class RateLimitError(EzRagifyError):
    """Raised on 429 Too Many Requests responses."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int = 429,
        body: Any = None,
        retry_after: Optional[float] = None,
    ) -> None:
        super().__init__(message, status_code=status_code, body=body)
        self.retry_after = retry_after


class ServerError(EzRagifyError):
    """Raised on 5xx server error responses."""


_STATUS_TO_EXCEPTION: dict[int, type[EzRagifyError]] = {
    401: AuthenticationError,
    403: PermissionError,
    404: NotFoundError,
    422: ValidationError,
    429: RateLimitError,
}


def raise_for_status(status_code: int, body: Any) -> None:
    """Raise an appropriate exception based on HTTP status code."""
    if 200 <= status_code < 300:
        return

    detail = ""
    if isinstance(body, dict):
        detail = body.get("detail", str(body))
    else:
        detail = str(body)

    exc_cls = _STATUS_TO_EXCEPTION.get(status_code)
    if exc_cls is None:
        if status_code >= 500:
            exc_cls = ServerError
        else:
            exc_cls = EzRagifyError

    kwargs: dict[str, Any] = {"status_code": status_code, "body": body}
    if exc_cls is RateLimitError:
        kwargs["retry_after"] = None  # could parse Retry-After header upstream
    raise exc_cls(detail, **kwargs)
