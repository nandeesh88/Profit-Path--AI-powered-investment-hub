"""
Database Module
MongoDB connection with pooling, index creation, and maintenance helpers.
"""
import logging
from datetime import datetime, timedelta

from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings

logger = logging.getLogger(__name__)

client: AsyncIOMotorClient = None


async def connect_db():
    """Open a pooled connection to MongoDB."""
    global client
    client = AsyncIOMotorClient(
        settings.MONGODB_URL,
        maxPoolSize=settings.MONGODB_POOL_SIZE,
        serverSelectionTimeoutMS=settings.MONGODB_TIMEOUT,
    )
    # Verify the connection is alive
    try:
        await client.admin.command("ping")
        logger.info(f"Connected to MongoDB at {settings.MONGODB_URL} (pool={settings.MONGODB_POOL_SIZE})")
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        raise


async def close_db():
    """Gracefully close the MongoDB connection."""
    global client
    if client:
        client.close()
        logger.info("MongoDB connection closed")


def get_database():
    return client[settings.DATABASE_NAME]


def get_collection(name: str):
    db = get_database()
    return db[name]


# ---------------------------------------------------------------------------
# Index creation
# ---------------------------------------------------------------------------

async def create_indexes():
    """Create MongoDB indexes for optimal query performance."""
    try:
        investments = get_collection("investments")
        await investments.create_index([("user_id", 1), ("created_at", -1)])
        await investments.create_index([("created_at", -1)])
        logger.info("✅ Investment indexes created")

        users = get_collection("users")
        await users.create_index("email", unique=True)
        logger.info("✅ User indexes created")

        expenses = get_collection("expenses")
        await expenses.create_index([("user_id", 1), ("date", -1)])
        await expenses.create_index([("user_id", 1), ("date", 1), ("amount", 1), ("description", 1)])
        logger.info("✅ Expense indexes created")

        expense_documents = get_collection("expense_documents")
        await expense_documents.create_index([("user_id", 1), ("created_at", -1)])
        await expense_documents.create_index([("user_id", 1), ("sha256", 1)])
        logger.info("✅ Expense document indexes created")

        goals = get_collection("goals")
        await goals.create_index([("user_id", 1)])
        logger.info("✅ Goal indexes created")

        incomes = get_collection("incomes")
        await incomes.create_index([("user_id", 1), ("month", -1)])
        await incomes.create_index([("user_id", 1), ("month", 1), ("source", 1)], unique=True)
        logger.info("✅ Income indexes created")
    except Exception as e:
        logger.warning(f"Index creation warning: {e}")


# ---------------------------------------------------------------------------
# Maintenance helpers
# ---------------------------------------------------------------------------

async def cleanup_old_recommendations(days: int = 365):
    """Remove investment recommendations older than *days*."""
    try:
        investments = get_collection("investments")
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = await investments.delete_many({"created_at": {"$lt": cutoff}})
        logger.info(f"Deleted {result.deleted_count} recommendations older than {days} days")
        return result.deleted_count
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
        return 0
