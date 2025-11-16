"""Admin user initialization service."""

import logging

from passlib.context import CryptContext
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.user import User

logger = logging.getLogger(__name__)
settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_admin_user() -> None:
    """Create admin user on first run if it doesn't exist."""
    # Use synchronous engine for initialization
    db_url = settings.DATABASE_URL.replace("sqlite+aiosqlite://", "sqlite:///")
    engine = create_engine(db_url, connect_args={"check_same_thread": False})

    with Session(engine) as db:
        try:
            # Check if admin exists
            result = db.execute(select(User).where(User.username == settings.ADMIN_USERNAME))
            admin = result.scalar_one_or_none()

            if not admin:
                admin = User(
                    username=settings.ADMIN_USERNAME,
                    password_hash=pwd_context.hash(settings.ADMIN_PASSWORD),
                    role="admin",
                )
                db.add(admin)
                db.commit()
                logger.warning(
                    f"Admin user '{settings.ADMIN_USERNAME}' created. "
                    "CHANGE PASSWORD IMMEDIATELY!"
                )
            else:
                logger.info("Admin user already exists.")

        except Exception as e:
            logger.error(f"Failed to create admin user: {e}")
            db.rollback()
        finally:
            engine.dispose()
