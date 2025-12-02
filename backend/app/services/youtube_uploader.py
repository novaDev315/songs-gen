"""
YouTube uploader service using Google API Python Client.

Requires Google Cloud Project with YouTube Data API v3 enabled.
"""

import logging
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# OAuth 2.0 scopes
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']


class YouTubeUploader:
    """Handles YouTube OAuth and video uploads."""

    def __init__(self):
        self.credentials: Optional[Credentials] = None
        self.youtube = None
        self.tokens_file = Path(settings.DATA_FOLDER) / 'youtube_tokens.json'

    def load_credentials(self) -> bool:
        """Load existing credentials from file.

        Returns:
            True if credentials loaded and valid, False otherwise
        """
        if not self.tokens_file.exists():
            logger.info("No YouTube tokens file found")
            return False

        try:
            with open(self.tokens_file, 'r') as f:
                token_data = json.load(f)

            self.credentials = Credentials.from_authorized_user_info(
                token_data,
                SCOPES
            )

            # Refresh if expired
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
                self.save_credentials()
                logger.info("YouTube credentials refreshed")

            return self.credentials and self.credentials.valid

        except Exception as e:
            logger.error(f"Error loading YouTube credentials: {e}")
            return False

    def save_credentials(self) -> None:
        """Save credentials to file."""
        if not self.credentials:
            return

        token_data = {
            'token': self.credentials.token,
            'refresh_token': self.credentials.refresh_token,
            'token_uri': self.credentials.token_uri,
            'client_id': self.credentials.client_id,
            'client_secret': self.credentials.client_secret,
            'scopes': self.credentials.scopes
        }

        self.tokens_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.tokens_file, 'w') as f:
            json.dump(token_data, f, indent=2)

        logger.info("YouTube credentials saved")

    def get_auth_url(self) -> str:
        """
        Get OAuth authorization URL.

        Returns:
            Authorization URL to redirect user to

        Raises:
            ValueError: If YouTube OAuth credentials not configured

        Note:
            Requires Google Cloud credentials (CLIENT_ID and CLIENT_SECRET) in .env
        """
        if not settings.YOUTUBE_CLIENT_ID or not settings.YOUTUBE_CLIENT_SECRET:
            raise ValueError("YouTube OAuth credentials not configured in .env")

        # Create flow with client config
        client_config = {
            'web': {
                'client_id': settings.YOUTUBE_CLIENT_ID,
                'client_secret': settings.YOUTUBE_CLIENT_SECRET,
                'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                'token_uri': 'https://oauth2.googleapis.com/token',
                'redirect_uris': [settings.YOUTUBE_REDIRECT_URI]
            }
        }

        flow = InstalledAppFlow.from_client_config(
            client_config,
            SCOPES,
            redirect_uri=settings.YOUTUBE_REDIRECT_URI
        )

        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )

        return auth_url

    def handle_oauth_callback(self, code: str) -> bool:
        """
        Handle OAuth callback with authorization code.

        Args:
            code: Authorization code from OAuth redirect

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            client_config = {
                'web': {
                    'client_id': settings.YOUTUBE_CLIENT_ID,
                    'client_secret': settings.YOUTUBE_CLIENT_SECRET,
                    'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                    'token_uri': 'https://oauth2.googleapis.com/token',
                    'redirect_uris': [settings.YOUTUBE_REDIRECT_URI]
                }
            }

            flow = InstalledAppFlow.from_client_config(
                client_config,
                SCOPES,
                redirect_uri=settings.YOUTUBE_REDIRECT_URI
            )

            flow.fetch_token(code=code)
            self.credentials = flow.credentials
            self.save_credentials()

            logger.info("YouTube OAuth authentication successful")
            return True

        except Exception as e:
            logger.error(f"YouTube OAuth callback failed: {e}")
            return False

    def initialize_youtube(self) -> bool:
        """Initialize YouTube API client.

        Returns:
            True if initialization successful, False otherwise
        """
        if not self.credentials:
            if not self.load_credentials():
                logger.error("No valid YouTube credentials available")
                return False

        try:
            self.youtube = build('youtube', 'v3', credentials=self.credentials)
            logger.info("YouTube API client initialized")
            return True

        except Exception as e:
            logger.error(f"Error initializing YouTube client: {e}")
            return False

    async def upload_video(
        self,
        video_file: Path,
        title: str,
        description: str,
        tags: list[str],
        privacy_status: str = 'public'
    ) -> Dict[str, Any]:
        """
        Upload video to YouTube.

        Args:
            video_file: Path to video file (MP4)
            title: Video title (max 100 chars)
            description: Video description (max 5000 chars)
            tags: List of tags (max 500 chars total)
            privacy_status: 'public', 'private', or 'unlisted'

        Returns:
            Dict with video_id, video_url, and status

        Raises:
            ValueError: If YouTube client not initialized or video file not found
            HttpError: If YouTube API call fails
        """
        if not self.youtube:
            if not self.initialize_youtube():
                raise ValueError("YouTube client not initialized")

        if not video_file.exists():
            raise ValueError(f"Video file not found: {video_file}")

        try:
            # Prepare request body
            body = {
                'snippet': {
                    'title': title[:100],  # YouTube max 100 chars
                    'description': description[:5000],  # YouTube max 5000 chars
                    'tags': tags[:500] if isinstance(tags, str) else tags,  # Max 500 chars
                    'categoryId': '10'  # Music category
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': False
                }
            }

            # Upload with resumable media
            media = MediaFileUpload(
                str(video_file),
                mimetype='video/mp4',
                resumable=True,
                chunksize=1024*1024  # 1MB chunks
            )

            logger.info(f"Uploading video to YouTube: {title}")

            # Execute upload
            request = self.youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    logger.info(f"Upload progress: {progress}%")

            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            logger.info(f"Video uploaded successfully: {video_url}")

            return {
                'video_id': video_id,
                'video_url': video_url,
                'status': 'uploaded',
                'privacy': privacy_status
            }

        except HttpError as e:
            logger.error(f"YouTube API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Upload error: {e}")
            raise


# Global instance
_youtube_uploader: Optional[YouTubeUploader] = None


def get_youtube_uploader() -> YouTubeUploader:
    """Get the global YouTube uploader instance.

    Returns:
        The singleton YouTubeUploader instance
    """
    global _youtube_uploader
    if _youtube_uploader is None:
        _youtube_uploader = YouTubeUploader()
    return _youtube_uploader
