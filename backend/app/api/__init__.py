"""API routes."""

from app.api import auth, evaluation, queue, songs, youtube

__all__ = [
    "auth",
    "songs",
    "queue",
    "evaluation",
    "youtube",
]
