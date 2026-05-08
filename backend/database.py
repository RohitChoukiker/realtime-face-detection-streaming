import logging

from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from config import settings

logger = logging.getLogger(__name__)

_url = make_url(settings.DATABASE_URL)

query = dict(_url.query) if _url.query else {}

_sslmode = query.pop("sslmode", None)
_channel_binding = query.pop("channel_binding", None)

_ssl_flag = query.pop("ssl", None)
should_use_ssl = False
if _sslmode is not None:
    should_use_ssl = str(_sslmode).lower() in {"require", "true", "1", "yes"}
if _ssl_flag is not None:
    should_use_ssl = str(_ssl_flag).lower() in {"true", "1", "require", "yes"}

connect_args = {"ssl": True} if should_use_ssl else {}


engine = create_async_engine(
    _url.set(query=query),
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args=connect_args,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


async def init_db():

    from models.session import Session  
    from models.frame import Frame  
    from models.roi import ROIDetection  
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("All database tables created / verified.")


async def get_db() -> AsyncSession:
    """Dependency — yields an async DB session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()