"""MongoDB database connection and configuration."""

import asyncio
from typing import AsyncGenerator

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import MongoClient
from pymongo.database import Database

from src.config.settings import settings


class MongoDBManager:
    """Manages MongoDB connections for both sync and async operations."""

    def __init__(self):
        self._async_client: AsyncIOMotorClient = None
        self._sync_client: MongoClient = None
        self._async_db: AsyncIOMotorDatabase = None
        self._sync_db: Database = None

    async def connect_async(self) -> None:
        """Initialize async MongoDB connection."""
        if self._async_client is None:
            self._async_client = AsyncIOMotorClient(settings.mongodb_url)
            self._async_db = self._async_client[settings.mongodb_db_name]
            # Test connection
            await self._async_client.admin.command('ping')

    def connect_sync(self) -> None:
        """Initialize sync MongoDB connection."""
        if self._sync_client is None:
            self._sync_client = MongoClient(settings.mongodb_url)
            self._sync_db = self._sync_client[settings.mongodb_db_name]
            # Test connection
            self._sync_client.admin.command('ping')

    async def disconnect_async(self) -> None:
        """Close async MongoDB connection."""
        if self._async_client:
            self._async_client.close()
            self._async_client = None
            self._async_db = None

    def disconnect_sync(self) -> None:
        """Close sync MongoDB connection."""
        if self._sync_client:
            self._sync_client.close()
            self._sync_client = None
            self._sync_db = None

    @property
    def async_db(self) -> AsyncIOMotorDatabase:
        """Get async database instance."""
        if self._async_db is None:
            raise RuntimeError("Async database not connected. Call connect_async() first.")
        return self._async_db

    @property
    def sync_db(self) -> Database:
        """Get sync database instance."""
        if self._sync_db is None:
            raise RuntimeError("Sync database not connected. Call connect_sync() first.")
        return self._sync_db

    async def get_async_collection(self, name: str):
        """Get async collection by name."""
        return self.async_db[name]

    def get_sync_collection(self, name: str):
        """Get sync collection by name."""
        return self.sync_db[name]


# Global database manager instance
db_manager = MongoDBManager()


# Dependency for FastAPI
async def get_database() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """FastAPI dependency to get database connection."""
    if db_manager._async_db is None:
        await db_manager.connect_async()
    yield db_manager.async_db


# Collection names
COLLECTIONS = {
    "users": "users",
    "conversations": "conversations",
    "messages": "messages",
    "context_embeddings": "context_embeddings",
    "moderation_logs": "moderation_logs",
    "feedback": "feedback",
    "analytics": "analytics",
}


async def create_indexes():
    """Create database indexes for optimal performance."""
    db = db_manager.async_db

    # Users collection indexes
    await db[COLLECTIONS["users"]].create_index("user_id", unique=True)
    await db[COLLECTIONS["users"]].create_index("email", unique=True)
    await db[COLLECTIONS["users"]].create_index("behavior_profile.risk_level")

    # Conversations collection indexes
    await db[COLLECTIONS["conversations"]].create_index("conversation_id", unique=True)
    await db[COLLECTIONS["conversations"]].create_index("participants")
    await db[COLLECTIONS["conversations"]].create_index("updated_at")

    # Messages collection indexes
    await db[COLLECTIONS["messages"]].create_index("message_id", unique=True)
    await db[COLLECTIONS["messages"]].create_index("conversation_id")
    await db[COLLECTIONS["messages"]].create_index("user_id")
    await db[COLLECTIONS["messages"]].create_index("timestamp")
    await db[COLLECTIONS["messages"]].create_index([
        ("conversation_id", 1),
        ("timestamp", -1)
    ])

    # Context embeddings collection indexes
    await db[COLLECTIONS["context_embeddings"]].create_index("conversation_id")
    await db[COLLECTIONS["context_embeddings"]].create_index("created_at")

    # Moderation logs collection indexes
    await db[COLLECTIONS["moderation_logs"]].create_index("message_id")
    await db[COLLECTIONS["moderation_logs"]].create_index("user_id")
    await db[COLLECTIONS["moderation_logs"]].create_index("timestamp")

    # Feedback collection indexes
    await db[COLLECTIONS["feedback"]].create_index("message_id")
    await db[COLLECTIONS["feedback"]].create_index("user_id")

    # Analytics collection indexes
    await db[COLLECTIONS["analytics"]].create_index("date")
    await db[COLLECTIONS["analytics"]].create_index("metric_type")