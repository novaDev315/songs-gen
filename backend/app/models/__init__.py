"""SQLAlchemy models for the Song Automation system."""

from app.models.evaluation import Evaluation
from app.models.playlist import Playlist, PlaylistSong
from app.models.song import Song
from app.models.style_template import StyleTemplate
from app.models.suno_job import SunoJob
from app.models.suno_variation import SunoVariation
from app.models.task_queue import TaskQueue
from app.models.user import User
from app.models.video_project import VideoProject
from app.models.youtube_upload import YouTubeUpload

__all__ = [
    "Evaluation",
    "Playlist",
    "PlaylistSong",
    "Song",
    "StyleTemplate",
    "SunoJob",
    "SunoVariation",
    "TaskQueue",
    "User",
    "VideoProject",
    "YouTubeUpload",
]
