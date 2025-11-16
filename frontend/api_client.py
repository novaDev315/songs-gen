"""API client for backend communication."""

import requests
from typing import Optional, Dict, Any, List
import os


class APIClient:
    """Client for Song Automation API."""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv('BACKEND_URL', 'http://backend:8000')
        self.token: Optional[str] = None

    def set_token(self, token: str) -> None:
        """Set JWT token for authenticated requests."""
        self.token = token

    def _headers(self) -> Dict[str, str]:
        """Get request headers with auth token."""
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers

    # Authentication
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login and get tokens."""
        response = requests.post(
            f'{self.base_url}/api/v1/auth/login',
            json={'username': username, 'password': password}
        )
        response.raise_for_status()
        return response.json()

    def get_me(self) -> Dict[str, Any]:
        """Get current user info."""
        response = requests.get(
            f'{self.base_url}/api/v1/auth/me',
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

    # Songs
    def list_songs(
        self,
        status: Optional[str] = None,
        genre: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List songs with filtering."""
        params = {'skip': skip, 'limit': limit}
        if status:
            params['status'] = status
        if genre:
            params['genre'] = genre

        response = requests.get(
            f'{self.base_url}/api/v1/songs',
            headers=self._headers(),
            params=params
        )
        response.raise_for_status()
        return response.json().get('items', [])

    def get_song(self, song_id: str) -> Dict[str, Any]:
        """Get song details."""
        response = requests.get(
            f'{self.base_url}/api/v1/songs/{song_id}',
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

    # Queue
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        response = requests.get(
            f'{self.base_url}/api/v1/queue/stats',
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

    def list_tasks(
        self,
        status: Optional[str] = None,
        task_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List queue tasks."""
        params = {'skip': skip, 'limit': limit}
        if status:
            params['status'] = status
        if task_type:
            params['task_type'] = task_type

        response = requests.get(
            f'{self.base_url}/api/v1/queue/tasks',
            headers=self._headers(),
            params=params
        )
        response.raise_for_status()
        return response.json().get('items', [])

    def retry_task(self, task_id: int) -> Dict[str, Any]:
        """Retry failed task."""
        response = requests.post(
            f'{self.base_url}/api/v1/queue/tasks/{task_id}/retry',
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

    # Evaluations
    def list_evaluations(
        self,
        approved: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List evaluations."""
        params = {'skip': skip, 'limit': limit}
        if approved is not None:
            params['approved'] = str(approved).lower()

        response = requests.get(
            f'{self.base_url}/api/v1/evaluations',
            headers=self._headers(),
            params=params
        )
        response.raise_for_status()
        return response.json().get('items', [])

    def approve_song(self, evaluation_id: int) -> Dict[str, Any]:
        """Approve song."""
        response = requests.post(
            f'{self.base_url}/api/v1/evaluations/{evaluation_id}/approve',
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

    def reject_song(self, evaluation_id: int, notes: str) -> Dict[str, Any]:
        """Reject song."""
        response = requests.post(
            f'{self.base_url}/api/v1/evaluations/{evaluation_id}/reject',
            headers=self._headers(),
            params={'notes': notes}
        )
        response.raise_for_status()
        return response.json()

    # YouTube
    def list_uploads(self, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        """List YouTube uploads."""
        response = requests.get(
            f'{self.base_url}/api/v1/youtube/uploads',
            headers=self._headers(),
            params={'skip': skip, 'limit': limit}
        )
        response.raise_for_status()
        return response.json().get('items', [])

    def get_oauth_url(self) -> str:
        """Get YouTube OAuth URL."""
        response = requests.get(
            f'{self.base_url}/api/v1/youtube/oauth-url',
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()['authorization_url']

    # System
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status."""
        response = requests.get(
            f'{self.base_url}/api/v1/system/status',
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()
