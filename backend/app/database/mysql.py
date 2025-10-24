from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings
from builtins import print

Base = declarative_base()

class Database:
    engine = None
    SessionLocal = None

    @classmethod
    async def connect_to_mysql(cls):
        try:
            if cls.engine is None:
                cls.engine = create_async_engine(
                    settings.MYSQL_URI,
                    echo=settings.DEBUG,
                    pool_pre_ping=True
                )
                cls.SessionLocal = sessionmaker(
                    bind=cls.engine,
                    class_=AsyncSession,
                    expire_on_commit=False
                )
                print("Successfully connected to MySQL")
        except Exception as e:
            print(f"Could not connect to MySQL: {e}")
            await cls.close_mysql_connection()

    @classmethod
    async def close_mysql_connection(cls):
        if cls.engine is not None:
            await cls.engine.dispose()
            cls.engine = None
            cls.SessionLocal = None
            print("MySQL connection closed")

    @classmethod
    def get_session(cls) -> AsyncSession:
        if cls.SessionLocal is None:
            raise ConnectionError("Database not connected")
        return cls.SessionLocal()

# Create a global instance
db = Database()

# Export helper functions
async def connect_to_mysql():
    await db.connect_to_mysql()

async def close_mysql_connection():
    await db.close_mysql_connection()

def get_session():
    return db.get_session()
