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


async def disconnect():
    global client
    if client:
        client.close()
        print("✓ MongoDB disconnected")