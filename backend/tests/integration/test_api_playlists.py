"""Integration tests for playlists API endpoints.

Tests playlist management including CRUD, song management, and reordering.
"""

import pytest


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def playlist_factory(test_db, test_user):
    """Factory for creating test playlists."""
    from app.models.playlist import Playlist

    def create_playlist(
        name: str = "Test Playlist",
        playlist_type: str = "playlist",
        is_public: bool = True,
        **kwargs,
    ) -> Playlist:
        playlist = Playlist(
            name=name,
            description=kwargs.get("description", "A test playlist"),
            playlist_type=playlist_type,
            genre=kwargs.get("genre", "Pop"),
            tags=kwargs.get("tags", "test,playlist"),
            is_public=is_public,
            created_by_id=kwargs.get("created_by_id", test_user.id),
        )
        test_db.add(playlist)
        test_db.commit()
        test_db.refresh(playlist)
        return playlist

    return create_playlist


@pytest.fixture
def playlist_song_factory(test_db):
    """Factory for adding songs to playlists."""
    from app.models.playlist import PlaylistSong

    def add_song_to_playlist(
        playlist_id: str,
        song_id: str,
        position: int = 0,
        **kwargs,
    ) -> PlaylistSong:
        playlist_song = PlaylistSong(
            playlist_id=playlist_id,
            song_id=song_id,
            position=position,
            track_number=kwargs.get("track_number"),
            custom_title=kwargs.get("custom_title"),
        )
        test_db.add(playlist_song)
        test_db.commit()
        test_db.refresh(playlist_song)
        return playlist_song

    return add_song_to_playlist


# =============================================================================
# List Playlists Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestListPlaylists:
    """Test playlist listing functionality."""

    def test_list_playlists_empty(self, client, auth_headers):
        """Test listing playlists when database is empty."""
        response = client.get("/api/v1/playlists", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_playlists_with_data(self, client, auth_headers, playlist_factory):
        """Test listing playlists with existing data."""
        playlist_factory(name="Playlist 1")
        playlist_factory(name="Playlist 2")
        playlist_factory(name="Playlist 3")

        response = client.get("/api/v1/playlists", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["total"] == 3

    def test_list_playlists_filter_by_type(self, client, auth_headers, playlist_factory):
        """Test filtering playlists by type."""
        playlist_factory(name="Album 1", playlist_type="album")
        playlist_factory(name="Playlist 1", playlist_type="playlist")
        playlist_factory(name="Album 2", playlist_type="album")

        response = client.get(
            "/api/v1/playlists",
            params={"playlist_type": "album"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert all(item["playlist_type"] == "album" for item in data["items"])

    def test_list_playlists_filter_by_genre(self, client, auth_headers, playlist_factory):
        """Test filtering playlists by genre."""
        playlist_factory(name="Pop Playlist", genre="Pop")
        playlist_factory(name="Rock Playlist", genre="Rock")
        playlist_factory(name="Another Pop", genre="Pop")

        response = client.get(
            "/api/v1/playlists",
            params={"genre": "Pop"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2

    def test_list_playlists_search(self, client, auth_headers, playlist_factory):
        """Test searching playlists."""
        playlist_factory(name="Summer Hits", description="Hot summer songs")
        playlist_factory(name="Winter Vibes", description="Cold winter tracks")
        playlist_factory(name="Party Mix", description="Best party songs")

        response = client.get(
            "/api/v1/playlists",
            params={"search": "summer"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert "Summer" in data["items"][0]["name"]

    def test_list_playlists_my_playlists(
        self, client, auth_headers, playlist_factory, test_admin
    ):
        """Test filtering for user's own playlists."""
        playlist_factory(name="My Playlist 1")
        playlist_factory(name="My Playlist 2")
        playlist_factory(name="Admin Playlist", created_by_id=test_admin.id)

        response = client.get(
            "/api/v1/playlists",
            params={"my_playlists": True},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2

    def test_list_playlists_pagination(self, client, auth_headers, playlist_factory):
        """Test pagination of playlist listing."""
        for i in range(10):
            playlist_factory(name=f"Playlist {i}")

        response = client.get(
            "/api/v1/playlists",
            params={"page": 1, "per_page": 3},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["total"] == 10
        assert data["page"] == 1
        assert data["per_page"] == 3

    def test_list_playlists_public_visibility(
        self, client, auth_headers, playlist_factory, test_admin
    ):
        """Test that users see public playlists and their own private ones."""
        playlist_factory(name="Public Playlist", is_public=True)
        playlist_factory(name="My Private", is_public=False)
        playlist_factory(name="Other Private", is_public=False, created_by_id=test_admin.id)

        response = client.get("/api/v1/playlists", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        # Should see public + own private, not other's private
        assert len(data["items"]) == 2

    def test_list_playlists_unauthorized(self, client):
        """Test listing playlists without authentication."""
        response = client.get("/api/v1/playlists")
        assert response.status_code == 403


# =============================================================================
# Get Playlist Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestGetPlaylist:
    """Test getting individual playlist details."""

    def test_get_playlist_success(
        self, client, auth_headers, playlist_factory, song_factory, playlist_song_factory
    ):
        """Test successful playlist retrieval with songs."""
        playlist = playlist_factory(name="Test Playlist", playlist_type="album")
        song1 = song_factory(song_id="song-001", title="Song 1")
        song2 = song_factory(song_id="song-002", title="Song 2")

        playlist_song_factory(playlist.id, song1.id, position=0, track_number=1)
        playlist_song_factory(playlist.id, song2.id, position=1, track_number=2)

        response = client.get(f"/api/v1/playlists/{playlist.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == playlist.id
        assert data["name"] == "Test Playlist"
        assert data["playlist_type"] == "album"
        assert data["song_count"] == 2
        assert len(data["songs"]) == 2
        assert data["songs"][0]["title"] == "Song 1"
        assert data["songs"][0]["track_number"] == 1

    def test_get_playlist_empty(self, client, auth_headers, playlist_factory):
        """Test getting playlist with no songs."""
        playlist = playlist_factory(name="Empty Playlist")

        response = client.get(f"/api/v1/playlists/{playlist.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["song_count"] == 0
        assert data["songs"] == []

    def test_get_playlist_not_found(self, client, auth_headers):
        """Test getting non-existent playlist."""
        response = client.get("/api/v1/playlists/nonexistent-id", headers=auth_headers)
        assert response.status_code == 404

    def test_get_playlist_private_not_owner(
        self, client, auth_headers, playlist_factory, test_admin
    ):
        """Test accessing private playlist by non-owner."""
        playlist = playlist_factory(
            name="Private Playlist",
            is_public=False,
            created_by_id=test_admin.id,
        )

        response = client.get(f"/api/v1/playlists/{playlist.id}", headers=auth_headers)
        assert response.status_code == 403


# =============================================================================
# Create Playlist Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestCreatePlaylist:
    """Test playlist creation."""

    def test_create_playlist_success(self, client, auth_headers):
        """Test successful playlist creation."""
        playlist_data = {
            "name": "New Playlist",
            "description": "A great playlist",
            "playlist_type": "playlist",
            "genre": "Pop",
            "tags": ["pop", "favorites"],
        }

        response = client.post(
            "/api/v1/playlists",
            json=playlist_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Playlist"
        assert data["playlist_type"] == "playlist"
        assert data["song_count"] == 0

    def test_create_playlist_album(self, client, auth_headers):
        """Test creating an album."""
        playlist_data = {
            "name": "My Album",
            "playlist_type": "album",
            "genre": "Rock",
        }

        response = client.post(
            "/api/v1/playlists",
            json=playlist_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        assert response.json()["playlist_type"] == "album"

    def test_create_playlist_invalid_type(self, client, auth_headers):
        """Test creating playlist with invalid type."""
        playlist_data = {
            "name": "Test",
            "playlist_type": "invalid",
        }

        response = client.post(
            "/api/v1/playlists",
            json=playlist_data,
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_create_playlist_private(self, client, auth_headers):
        """Test creating private playlist."""
        playlist_data = {
            "name": "Private Playlist",
            "is_public": False,
        }

        response = client.post(
            "/api/v1/playlists",
            json=playlist_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        assert response.json()["is_public"] is False

    def test_create_playlist_unauthorized(self, client):
        """Test creating playlist without authentication."""
        response = client.post(
            "/api/v1/playlists",
            json={"name": "Test"},
        )
        assert response.status_code == 403


# =============================================================================
# Update Playlist Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestUpdatePlaylist:
    """Test playlist update functionality."""

    def test_update_playlist_success(self, client, auth_headers, playlist_factory):
        """Test successful playlist update."""
        playlist = playlist_factory(name="Original Name")

        response = client.put(
            f"/api/v1/playlists/{playlist.id}",
            json={"name": "Updated Name"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

    def test_update_playlist_multiple_fields(self, client, auth_headers, playlist_factory):
        """Test updating multiple playlist fields."""
        playlist = playlist_factory(name="Original", genre="Pop")

        response = client.put(
            f"/api/v1/playlists/{playlist.id}",
            json={
                "name": "Updated",
                "genre": "Rock",
                "playlist_type": "album",
                "tags": ["rock", "updated"],
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated"
        assert data["genre"] == "Rock"
        assert data["playlist_type"] == "album"

    def test_update_playlist_not_owner(
        self, client, auth_headers, playlist_factory, test_admin
    ):
        """Test updating playlist by non-owner."""
        playlist = playlist_factory(name="Admin Playlist", created_by_id=test_admin.id)

        response = client.put(
            f"/api/v1/playlists/{playlist.id}",
            json={"name": "Hacked Name"},
            headers=auth_headers,
        )

        assert response.status_code == 403

    def test_update_playlist_not_found(self, client, auth_headers):
        """Test updating non-existent playlist."""
        response = client.put(
            "/api/v1/playlists/nonexistent-id",
            json={"name": "New Name"},
            headers=auth_headers,
        )
        assert response.status_code == 404


# =============================================================================
# Delete Playlist Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestDeletePlaylist:
    """Test playlist deletion."""

    def test_delete_playlist_success(self, client, auth_headers, playlist_factory):
        """Test successful playlist deletion."""
        playlist = playlist_factory(name="To Delete")

        response = client.delete(
            f"/api/v1/playlists/{playlist.id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify deleted
        get_response = client.get(
            f"/api/v1/playlists/{playlist.id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    def test_delete_playlist_not_owner(
        self, client, auth_headers, playlist_factory, test_admin
    ):
        """Test deleting playlist by non-owner."""
        playlist = playlist_factory(name="Admin Playlist", created_by_id=test_admin.id)

        response = client.delete(
            f"/api/v1/playlists/{playlist.id}",
            headers=auth_headers,
        )

        assert response.status_code == 403

    def test_delete_playlist_not_found(self, client, auth_headers):
        """Test deleting non-existent playlist."""
        response = client.delete("/api/v1/playlists/nonexistent-id", headers=auth_headers)
        assert response.status_code == 404


# =============================================================================
# Add Song to Playlist Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestAddSongToPlaylist:
    """Test adding songs to playlists."""

    def test_add_song_success(
        self, client, auth_headers, playlist_factory, song_factory
    ):
        """Test successfully adding a song to playlist."""
        playlist = playlist_factory(name="My Playlist")
        song = song_factory(song_id="song-001", title="Test Song")

        response = client.post(
            f"/api/v1/playlists/{playlist.id}/songs",
            json={"song_id": song.id},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["song_count"] == 1
        assert len(data["songs"]) == 1
        assert data["songs"][0]["id"] == song.id

    def test_add_song_with_position(
        self, client, auth_headers, playlist_factory, song_factory
    ):
        """Test adding song at specific position."""
        playlist = playlist_factory(name="My Playlist")
        song = song_factory(song_id="song-001", title="Test Song")

        response = client.post(
            f"/api/v1/playlists/{playlist.id}/songs",
            json={"song_id": song.id, "position": 5, "track_number": 1},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["songs"][0]["position"] == 5
        assert data["songs"][0]["track_number"] == 1

    def test_add_song_playlist_not_found(self, client, auth_headers, song_factory):
        """Test adding song to non-existent playlist."""
        song = song_factory(song_id="song-001")

        response = client.post(
            "/api/v1/playlists/nonexistent-id/songs",
            json={"song_id": song.id},
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_add_song_song_not_found(self, client, auth_headers, playlist_factory):
        """Test adding non-existent song to playlist."""
        playlist = playlist_factory(name="My Playlist")

        response = client.post(
            f"/api/v1/playlists/{playlist.id}/songs",
            json={"song_id": "nonexistent-song"},
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_add_song_already_in_playlist(
        self, client, auth_headers, playlist_factory, song_factory, playlist_song_factory
    ):
        """Test adding song that is already in playlist."""
        playlist = playlist_factory(name="My Playlist")
        song = song_factory(song_id="song-001")
        playlist_song_factory(playlist.id, song.id, position=0)

        response = client.post(
            f"/api/v1/playlists/{playlist.id}/songs",
            json={"song_id": song.id},
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "already in playlist" in response.json()["detail"].lower()

    def test_add_song_not_owner(
        self, client, auth_headers, playlist_factory, song_factory, test_admin
    ):
        """Test adding song by non-owner."""
        playlist = playlist_factory(name="Admin Playlist", created_by_id=test_admin.id)
        song = song_factory(song_id="song-001")

        response = client.post(
            f"/api/v1/playlists/{playlist.id}/songs",
            json={"song_id": song.id},
            headers=auth_headers,
        )

        assert response.status_code == 403


# =============================================================================
# Remove Song from Playlist Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestRemoveSongFromPlaylist:
    """Test removing songs from playlists."""

    def test_remove_song_success(
        self, client, auth_headers, playlist_factory, song_factory, playlist_song_factory
    ):
        """Test successfully removing a song from playlist."""
        playlist = playlist_factory(name="My Playlist")
        song = song_factory(song_id="song-001", title="Test Song")
        playlist_song_factory(playlist.id, song.id, position=0)

        response = client.delete(
            f"/api/v1/playlists/{playlist.id}/songs/{song.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["song_count"] == 0
        assert len(data["songs"]) == 0

    def test_remove_song_playlist_not_found(self, client, auth_headers):
        """Test removing song from non-existent playlist."""
        response = client.delete(
            "/api/v1/playlists/nonexistent-id/songs/song-001",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_remove_song_not_in_playlist(
        self, client, auth_headers, playlist_factory, song_factory
    ):
        """Test removing song that is not in playlist."""
        playlist = playlist_factory(name="My Playlist")
        song = song_factory(song_id="song-001")

        response = client.delete(
            f"/api/v1/playlists/{playlist.id}/songs/{song.id}",
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert "not in playlist" in response.json()["detail"].lower()

    def test_remove_song_not_owner(
        self, client, auth_headers, playlist_factory, song_factory, playlist_song_factory, test_admin
    ):
        """Test removing song by non-owner."""
        playlist = playlist_factory(name="Admin Playlist", created_by_id=test_admin.id)
        song = song_factory(song_id="song-001")
        playlist_song_factory(playlist.id, song.id, position=0)

        response = client.delete(
            f"/api/v1/playlists/{playlist.id}/songs/{song.id}",
            headers=auth_headers,
        )

        assert response.status_code == 403


# =============================================================================
# Reorder Playlist Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestReorderPlaylist:
    """Test playlist song reordering."""

    def test_reorder_playlist_success(
        self, client, auth_headers, playlist_factory, song_factory, playlist_song_factory
    ):
        """Test successfully reordering songs in playlist."""
        playlist = playlist_factory(name="My Playlist")
        song1 = song_factory(song_id="song-001", title="Song 1")
        song2 = song_factory(song_id="song-002", title="Song 2")
        song3 = song_factory(song_id="song-003", title="Song 3")

        playlist_song_factory(playlist.id, song1.id, position=0)
        playlist_song_factory(playlist.id, song2.id, position=1)
        playlist_song_factory(playlist.id, song3.id, position=2)

        # Reorder: 3, 1, 2
        response = client.post(
            f"/api/v1/playlists/{playlist.id}/reorder",
            json={"song_ids": [song3.id, song1.id, song2.id]},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["songs"][0]["id"] == song3.id
        assert data["songs"][1]["id"] == song1.id
        assert data["songs"][2]["id"] == song2.id

    def test_reorder_playlist_not_found(self, client, auth_headers):
        """Test reordering non-existent playlist."""
        response = client.post(
            "/api/v1/playlists/nonexistent-id/reorder",
            json={"song_ids": ["song-001", "song-002"]},
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_reorder_playlist_not_owner(
        self, client, auth_headers, playlist_factory, test_admin
    ):
        """Test reordering playlist by non-owner."""
        playlist = playlist_factory(name="Admin Playlist", created_by_id=test_admin.id)

        response = client.post(
            f"/api/v1/playlists/{playlist.id}/reorder",
            json={"song_ids": []},
            headers=auth_headers,
        )

        assert response.status_code == 403


# =============================================================================
# Playlist Types Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestPlaylistTypes:
    """Test different playlist types."""

    def test_create_ep(self, client, auth_headers):
        """Test creating an EP."""
        response = client.post(
            "/api/v1/playlists",
            json={"name": "My EP", "playlist_type": "ep"},
            headers=auth_headers,
        )

        assert response.status_code == 201
        assert response.json()["playlist_type"] == "ep"

    def test_create_single(self, client, auth_headers):
        """Test creating a single."""
        response = client.post(
            "/api/v1/playlists",
            json={"name": "My Single", "playlist_type": "single"},
            headers=auth_headers,
        )

        assert response.status_code == 201
        assert response.json()["playlist_type"] == "single"

    def test_filter_all_types(self, client, auth_headers, playlist_factory):
        """Test filtering by all playlist types."""
        playlist_factory(name="Playlist", playlist_type="playlist")
        playlist_factory(name="Album", playlist_type="album")
        playlist_factory(name="EP", playlist_type="ep")
        playlist_factory(name="Single", playlist_type="single")

        for ptype in ["playlist", "album", "ep", "single"]:
            response = client.get(
                "/api/v1/playlists",
                params={"playlist_type": ptype},
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data["items"]) == 1
            assert data["items"][0]["playlist_type"] == ptype
