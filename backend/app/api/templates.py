"""Style Templates API endpoints for managing reusable song templates."""

import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.database import get_db
from app.models.style_template import StyleTemplate
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


class TemplateCreate(BaseModel):
    """Schema for creating a template."""
    name: str
    description: Optional[str] = None
    style_prompt: str
    genre: str
    sub_genre: Optional[str] = None
    mood: Optional[str] = None
    energy: Optional[str] = None
    tags: Optional[str] = None
    is_public: bool = True


class TemplateUpdate(BaseModel):
    """Schema for updating a template."""
    name: Optional[str] = None
    description: Optional[str] = None
    style_prompt: Optional[str] = None
    genre: Optional[str] = None
    sub_genre: Optional[str] = None
    mood: Optional[str] = None
    energy: Optional[str] = None
    tags: Optional[str] = None
    is_public: Optional[bool] = None
    is_featured: Optional[bool] = None


class TemplateResponse(BaseModel):
    """Schema for template response."""
    id: int
    name: str
    description: Optional[str]
    style_prompt: str
    genre: str
    sub_genre: Optional[str]
    mood: Optional[str]
    energy: Optional[str]
    tags: Optional[str]
    is_public: bool
    is_featured: bool
    usage_count: int

    class Config:
        from_attributes = True


class TemplateList(BaseModel):
    """Schema for paginated template list."""
    items: list[TemplateResponse]
    total: int
    skip: int
    limit: int


@router.get("/templates", response_model=TemplateList)
async def list_templates(
    current_user: Annotated[User, Depends(get_current_user)],
    genre: Optional[str] = None,
    mood: Optional[str] = None,
    is_featured: Optional[bool] = None,
    search: Optional[str] = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
) -> TemplateList:
    """List style templates with filtering and pagination."""
    query = select(StyleTemplate).where(StyleTemplate.is_public == True)

    if genre:
        query = query.where(StyleTemplate.genre == genre)
    if mood:
        query = query.where(StyleTemplate.mood == mood)
    if is_featured is not None:
        query = query.where(StyleTemplate.is_featured == is_featured)
    if search:
        search_term = f"%{search}%"
        query = query.where(
            (StyleTemplate.name.ilike(search_term)) |
            (StyleTemplate.description.ilike(search_term)) |
            (StyleTemplate.tags.ilike(search_term))
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    query = query.order_by(StyleTemplate.usage_count.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    templates = result.scalars().all()

    return TemplateList(
        items=[TemplateResponse.model_validate(t) for t in templates],
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/templates/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
) -> TemplateResponse:
    """Get a specific template by ID."""
    result = await db.execute(
        select(StyleTemplate).where(StyleTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    return TemplateResponse.model_validate(template)


@router.post("/templates", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: TemplateCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
) -> TemplateResponse:
    """Create a new style template."""
    template = StyleTemplate(
        name=template_data.name,
        description=template_data.description,
        style_prompt=template_data.style_prompt,
        genre=template_data.genre,
        sub_genre=template_data.sub_genre,
        mood=template_data.mood,
        energy=template_data.energy,
        tags=template_data.tags,
        is_public=template_data.is_public,
        created_by_id=current_user.id
    )

    db.add(template)
    await db.commit()
    await db.refresh(template)

    logger.info(f"Created template: {template.id} - {template.name}")
    return TemplateResponse.model_validate(template)


@router.put("/templates/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    template_data: TemplateUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
) -> TemplateResponse:
    """Update an existing template."""
    result = await db.execute(
        select(StyleTemplate).where(StyleTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    # Check ownership (allow admin or creator)
    if template.created_by_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this template"
        )

    # Update fields
    update_data = template_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)

    await db.commit()
    await db.refresh(template)

    logger.info(f"Updated template: {template.id}")
    return TemplateResponse.model_validate(template)


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
) -> None:
    """Delete a template."""
    result = await db.execute(
        select(StyleTemplate).where(StyleTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    # Check ownership
    if template.created_by_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this template"
        )

    await db.delete(template)
    await db.commit()

    logger.info(f"Deleted template: {template_id}")


@router.post("/templates/{template_id}/use", response_model=TemplateResponse)
async def use_template(
    template_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
) -> TemplateResponse:
    """Record usage of a template (increments usage count)."""
    result = await db.execute(
        select(StyleTemplate).where(StyleTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    template.increment_usage()
    await db.commit()
    await db.refresh(template)

    return TemplateResponse.model_validate(template)


@router.get("/templates/genres/list", response_model=list[str])
async def list_genres(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
) -> list[str]:
    """Get list of unique genres from templates."""
    result = await db.execute(
        select(StyleTemplate.genre)
        .distinct()
        .where(StyleTemplate.is_public == True)
        .order_by(StyleTemplate.genre)
    )
    genres = result.scalars().all()
    return [g for g in genres if g]
