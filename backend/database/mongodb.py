from motor.motor_asyncio import AsyncIOMotorClient
from config import get_settings

settings = get_settings()

# Single client instance — motor manages the connection pool internally
client: AsyncIOMotorClient = None


def get_client() -> AsyncIOMotorClient:
    return client


def get_db():
    return client[settings.mongo_db]


async def connect():
    global client
    client = AsyncIOMotorClient(settings.mongo_url)
    # Verify connection on startup
    await client.admin.command("ping")
    print("✓ MongoDB connected")
    # Ensure indexes exist — idempotent, safe to run every startup
    await _create_indexes()


async def _create_indexes():
    db = client[settings.mongo_db]
    # Unique email index — enforced at DB level, not just application level
    await db["users"].create_index("email", unique=True)
    # Session lookups by userId and status
    await db["sessions"].create_index("userId")
    await db["sessions"].create_index([("userId", 1), ("status", 1)])
    # Event lookups by sessionId
    await db["events"].create_index("sessionId")
    print("✓ MongoDB indexes ensured")


async def disconnect():
    global client
    if client:
        client.close()
        print("✓ MongoDB disconnected")