from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncAttrs
from dotenv import load_dotenv
import os

load_dotenv()

ENGINE = os.getenv("POSTGRES_ENGINE")

engine = create_async_engine(url=ENGINE, echo=True)

async_session = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def get_db():
    async with async_session() as db:
        yield db


class Base(AsyncAttrs, DeclarativeBase):
    pass
