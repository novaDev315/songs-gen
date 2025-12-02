"""Playlist management API endpoints."""

import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.auth import get_current_user
from app.database import get_db
from app.models.playlist import Playlist, PlaylistSong
from app.models.song import Song
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


class PlaylistCreate(BaseModel):
    """Schema for creating a playlist."""
    name: str
    description: Optional[str] = None
    is_public: bool = False


class PlaylistUpdate(BaseModel):
    """Schema for updating a playlist."""
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None


class PlaylistResponse(BaseModel):
    """Schema for playlist response."""
    id: int
    name: str
    description: Optional[str]
    is_public: bool
    song_count: int = 0
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class PlaylistDetailResponse(BaseModel):
    """Schema for playlist with songs."""
    id: int
    name: str
    description: Optional[str]
    is_public: bool
    songs: list[dict]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class PlaylistList(BaseModel):
    """Schema for paginated playlist list."""
    items: list[PlaylistResponse]
    total: int
    skip: int
    limit: int


class AddSongRequest(BaseModel):
    """Schema for adding a song to playlist."""
    song_id: str
    position: Optional[int] = None


@router.get("/playlists", response_model=PlaylistList)
async def list_playlists(
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
) -> PlaylistList:
    """List all playlists."""
    query = select(Playlist).where(
        (Playlist.is_public == True) | (Playlist.created_by_id == current_user.id)
    )

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Playlist.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    playlists = result.scalars().all()

    logger.info(f"User {current_user.username} listed {len(playlists)} playlists")

    items = []
    for playlist in playlists:
        # Count songs in playlist
        count_result = await db.execute(
            select(func.count()).where(PlaylistSong.playlist_id == playlist.id)
        )
        song_count = count_result.scalar() or 0

        items.append(PlaylistResponse(
            id=playlist.id,
            name=playlist.name,
            description=playlist.description,
            is_public=playlist.is_public,
            song_count=song_count,
            created_at=playlist.created_at.isoformat(),
            updated_at=playlist.updated_at.isoformat(),
        ))

    return PlaylistList(
        items=items,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/playlists/{playlist_id}", response_model=PlaylistDetailResponse)
async def get_playlist(
    playlist_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
) -> PlaylistDetailResponse:
    """Get a playlist with its songs."""
    result = await db.execute(
        select(Playlist)
        .where(Playlist.id == playlist_id)
        .options(selectinload(Playlist.playlist_songs).selectinload(PlaylistSong.song))
    )
    playlist = result.scalar_one_or_none()

    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found"
        )

    # Check access
    if not playlist.is_public and playlist.created_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this playlist"
        )

    # Build songs list with positions
    songs = []
    for ps in sorted(playlist.playlist_songs, key=lambda x: x.position):
        if ps.song:
            songs.append({
                "id": ps.song.id,
                "title": ps.song.title,
                "genre": ps.song.genre,
                "position": ps.position,
                "added_at": ps.added_at.isoformat(),
            })

    return PlaylistDetailResponse(
        id=playlist.id,
        name=playlist.name,
        description=playlist.description,
        is_public=playlist.is_public,
        songs=songs,
        created_at=playlist.created_at.isoformat(),
        updated_at=playlist.updated_at.isoformat(),
    )


@router.post("/playlists", response_model=PlaylistResponse, status_code=status.HTTP_201_CREATED)
async def create_playlist(
    playlist_data: PlaylistCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
) -> PlaylistResponse:
    """Create a new playlist."""
    playlist = Playlist(
        name=playlist_data.name,
        description=playlist_data.description,
        is_public=playlist_data.is_public,
        created_by_id=current_user.id,
    )

    db.add(playlist)
    await db.commit()
    await db.refresh(playlist)

    logger.info(f"User {current_user.username} created playlist {playlist.id}")

    return PlaylistResponse(
        id=playlist.id,
        name=playlist.name,
        description=playlist.description,
        is_public=playlist.is_public,
        song_count=0,
        created_at=playlist.created_at.isoformat(),
        updated_at=playlist.updated_at.isoformat(),
    )


@router.put("/playlists/{playlist_id}", response_model=PlaylistResponse)
async def update_playlist(
    playlist_id: int,
    playlist_data: PlaylistUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
) -> PlaylistResponse:
    """Update a playlist."""
    result = await db.execute(
        select(Playlist).where(Playlist.id == playlist_id)
    )
    playlist = result.scalar_one_or_none()

    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found"
        )

    if playlist.created_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this playlist"
        )

    update_data = playlist_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(playlist, field, value)

    await db.commit()
    await db.refresh(playlist)

    # Count songs
    count_result = await db.execute(
        select(func.count()).where(PlaylistSong.playlist_id == playlist.id)
    )
    song_count = count_result.scalar() or 0

    logger.info(f"User {current_user.username} updated playlist {playlist_id}")

    return PlaylistResponse(
        id=playlist.id,
        name=playlist.name,
        description=playlist.description,
        is_public=playlist.is_public,
        song_count=song_count,
        created_at=playlist.created_at.isoformat(),
        updated_at=playlist.updated_at.isoformat(),
    )


@router.delete("/playlists/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_playlist(
    playlist_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
) -> None:
    """Delete a playlist."""
    result = await db.execute(
        select(Playlist).where(Playlist.id == playlist_id)
    )
    playlist = result.scalar_one_or_none()

    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found"
        )

    if playlist.created_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this playlist"
        )

    await db.delete(playlist)
    await db.commit()

    logger.info(f"User {current_user.username} deleted playlist {playlist_id}")


@router.post("/playlists/{playlist_id}/songs", response_model=PlaylistDetailResponse)
async def add_song_to_playlist(
    playlist_id: int,
    request: AddSongRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
) -> PlaylistDetailResponse:
    """Add a song to a playlist."""
    # Get playlist
    result = await db.execute(
        select(Playlist).where(Playlist.id == playlist_id)
    )
    playlist = result.scalar_one_or_none()

    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found"
        )

    if playlist.created_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this playlist"
        )

    # Verify song exists
    song_result = await db.execute(
        select(Song).where(Song.id == request.song_id)
    )
    song = song_result.scalar_one_or_none()

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )

    # Check if song already in playlist
    existing = await db.execute(
        select(PlaylistSong).where(
            PlaylistSong.playlist_id == playlist_id,
            PlaylistSong.song_id == request.song_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Song already in playlist"
        )

    # Determine position
    if request.position is not None:
        position = request.position
    else:
        max_pos_result = await db.execute(
            select(func.max(PlaylistSong.position)).where(
                PlaylistSong.playlist_id == playlist_id
            )
        )
        max_pos = max_pos_result.scalar() or -1
        position = max_pos + 1

    # Add song
    playlist_song = PlaylistSong(
        playlist_id=playlist_id,
        song_id=request.song_id,
        position=position,
    )
    db.add(playlist_song)
    await db.commit()

    logger.info(f"User {current_user.username} added song {request.song_id} to playlist {playlist_id}")

    # Return updated playlist
    return await get_playlist(playlist_id, current_user, db)


@router.delete("/playlists/{playlist_id}/songs/{song_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_song_from_playlist(
    playlist_id: int,
    song_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
) -> None:
    """Remove a song from a playlist."""
    # Get playlist
    result = await db.execute(
        select(Playlist).where(Playlist.id == playlist_id)
    )
    playlist = result.scalar_one_or_none()

    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found"
        )

    if playlist.created_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this playlist"
        )

    # Find and delete song
    ps_result = await db.execute(
        select(PlaylistSong).where(
            PlaylistSong.playlist_id == playlist_id,
            PlaylistSong.song_id == song_id
        )
    )
    playlist_song = ps_result.scalar_one_or_none()

    if not playlist_song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found in playlist"
        )

    await db.delete(playlist_song)
    await db.commit()

    logger.info(f"User {current_user.username} removed song {song_id} from playlist {playlist_id}")
