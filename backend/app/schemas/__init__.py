"""Pydantic schemas for API validation."""

from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse, UserResponse
from app.schemas.evaluation import (
    BatchApproval,
    BatchApprovalResult,
    EvaluationCreate,
    EvaluationList,
    EvaluationResponse,
    EvaluationUpdate,
    ManualEvaluation,
)
from app.schemas.queue import (
    QueueStats,
    TaskQueueCreate,
    TaskQueueList,
    TaskQueueResponse,
    TaskQueueUpdate,
)
from app.schemas.song import (
    SongCreate,
    SongList,
    SongResponse,
    SongStatus,
    SongUpdate,
)
from app.schemas.youtube import (
    OAuthCallback,
    OAuthURL,
    YouTubeUploadCreate,
    YouTubeUploadList,
    YouTubeUploadResponse,
    YouTubeUploadUpdate,
)

__all__ = [
    # Auth
    "LoginRequest",
    "TokenResponse",
    "RefreshRequest",
    "UserResponse",
    # Song
    "SongCreate",
    "SongUpdate",
    "SongResponse",
    "SongStatus",
    "SongList",
    # Queue
    "TaskQueueCreate",
    "TaskQueueUpdate",
    "TaskQueueResponse",
    "TaskQueueList",
    "QueueStats",
    # Evaluation
    "EvaluationCreate",
    "EvaluationUpdate",
    "ManualEvaluation",
    "EvaluationResponse",
    "EvaluationList",
    "BatchApproval",
    "BatchApprovalResult",
    # YouTube
    "YouTubeUploadCreate",
    "YouTubeUploadUpdate",
    "YouTubeUploadResponse",
    "YouTubeUploadList",
    "OAuthURL",
    "OAuthCallback",
]
