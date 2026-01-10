"""Admin user initialization service."""

import logging

from passlib.context import CryptContext
from sqlalchemy import select

from app.config import get_settings
from app.database import get_session_local
from app.models.user import User

logger = logging.getLogger(__name__)
settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_admin_user() -> None:
    """Create admin user on first run if it doesn't exist."""
    session_local = get_session_local()
    async with session_local() as db:
        try:
            # Check if admin exists (by is_admin flag or username)
            result = await db.execute(
                select(User).where(User.is_admin == True)
            )
            admin = result.scalar_one_or_none()

            if not admin:
                admin = User(
                    username=settings.ADMIN_USERNAME,
                    email=f"{settings.ADMIN_USERNAME}@localhost",
                    hashed_password=pwd_context.hash(settings.ADMIN_PASSWORD),
                    is_admin=True,
                    is_active=True,
                    is_verified=True,
                )
                db.add(admin)
                await db.commit()
                logger.warning(
                    f"Admin user '{settings.ADMIN_USERNAME}' created. "
                    "CHANGE PASSWORD IMMEDIATELY!"
                )
            else:
                # Update existing admin password and username if changed
                admin.username = settings.ADMIN_USERNAME
                admin.hashed_password = pwd_context.hash(settings.ADMIN_PASSWORD)
                await db.commit()
                logger.info(f"Admin user updated to '{settings.ADMIN_USERNAME}'.")

        except Exception as e:
            logger.error(f"Failed to create admin user: {e}")
            await db.rollback()
