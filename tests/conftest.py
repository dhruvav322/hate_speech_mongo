"""Pytest configuration and fixtures for hate speech moderation tests."""

import asyncio
import pytest
import pytest_asyncio
from datetime import datetime
from typing import AsyncGenerator, Generator

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

from src.config.database import db_manager
from src.config.settings import settings
from src.services.toxicity_detector import toxicity_detector
from src.services.embedding_service import embedding_service
from src.services.moderation_service import moderation_service
from src.services.user_service import user_service


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_db():
    """Setup test database connection."""
    # Use test database
    test_db_name = f"{settings.mongodb_db_name}_test"

    # Update settings for test
    original_db_name = settings.mongodb_db_name
    settings.mongodb_db_name = test_db_name

    # Connect to test database
    test_client = AsyncIOMotorClient(settings.mongodb_url)
    test_db = test_client[test_db_name]

    # Clean up before tests
    await test_db.drop_collection("users")
    await test_db.drop_collection("conversations")
    await test_db.drop_collection("messages")
    await test_db.drop_collection("context_embeddings")
    await test_db.drop_collection("moderation_logs")
    await test_db.drop_collection("feedback")

    yield test_db

    # Cleanup after tests
    await test_client.drop_database(test_db_name)
    test_client.close()

    # Restore original settings
    settings.mongodb_db_name = original_db_name


@pytest.fixture(scope="session")
def sync_test_db():
    """Setup sync test database for tests that need sync operations."""
    test_db_name = f"{settings.mongodb_db_name}_test_sync"

    # Connect to test database
    sync_client = MongoClient(settings.mongodb_url)
    test_db = sync_client[test_db_name]

    yield test_db

    # Cleanup
    sync_client.drop_database(test_db_name)
    sync_client.close()


@pytest_asyncio.fixture
async def test_user(test_db):
    """Create a test user."""
    from src.models.user import UserCreate

    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        platform="test"
    )

    user = await user_service.create_user(user_data)
    yield user

    # Cleanup
    await test_db["users"].delete_one({"user_id": user.user_id})


@pytest_asyncio.fixture
async def test_conversation(test_db):
    """Create a test conversation."""
    from src.models.conversation import ConversationCreate, ConversationMetadata

    conv_data = ConversationCreate(
        participants=["user_test001"],
        metadata=ConversationMetadata(
            platform="test",
            topic="test conversation"
        )
    )

    import uuid
    conversation_id = f"conv_{uuid.uuid4().hex[:8]}"

    conversation = {
        "conversation_id": conversation_id,
        "participants": conv_data.participants,
        "metadata": conv_data.metadata.dict(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "status": "active"
    }

    await test_db["conversations"].insert_one(conversation)
    yield conversation

    # Cleanup
    await test_db["conversations"].delete_one({"conversation_id": conversation_id})


@pytest_asyncio.fixture
async def setup_services():
    """Setup ML services for testing."""
    try:
        # Pre-load models
        await toxicity_detector.health_check()
        await embedding_service.health_check()
    except Exception as e:
        pytest.skip(f"Could not load ML models: {e}")


@pytest.fixture
def sample_messages():
    """Sample messages for testing."""
    return [
        {
            "text": "Hello everyone! How are you doing today?",
            "expected_toxicity": 0.0,
            "expected_action": "none"
        },
        {
            "text": "I think you're wrong about this topic.",
            "expected_toxicity": 0.1,
            "expected_action": "none"
        },
        {
            "text": "You're stupid and nobody likes you!",
            "expected_toxicity": 0.7,
            "expected_action": "warn"
        },
        {
            "text": "I hate all people from that country and they should leave!",
            "expected_toxicity": 0.9,
            "expected_action": "delete"
        }
    ]


@pytest.fixture
def sample_toxicity_predictions():
    """Sample toxicity predictions for testing."""
    return {
        "toxic": 0.1,
        "severe_toxic": 0.0,
        "obscene": 0.0,
        "threat": 0.0,
        "insult": 0.05,
        "identity_hate": 0.0
    }


# Mock data fixtures
@pytest.fixture
def mock_user_profile():
    """Mock user profile for testing."""
    from src.models.user import BehaviorProfile

    return BehaviorProfile(
        average_toxicity_score=0.2,
        message_frequency=10,
        risk_level="medium",
        trust_score=0.7
    )


@pytest.fixture
def mock_context_info():
    """Mock context information for testing."""
    return {
        "similarity_to_context": 0.3,
        "user_risk_level": "medium",
        "conversation_trend": "neutral",
        "context_available": True
    }


# Test utilities
@pytest.fixture
def create_test_message():
    """Factory function to create test messages."""
    async def _create_message(test_db, **kwargs):
        import uuid
        from datetime import datetime

        message_id = kwargs.get("message_id", f"msg_{uuid.uuid4().hex[:8]}")

        message = {
            "message_id": message_id,
            "conversation_id": kwargs.get("conversation_id", "conv_test001"),
            "user_id": kwargs.get("user_id", "user_test001"),
            "content": kwargs.get("content", "Test message"),
            "timestamp": kwargs.get("timestamp", datetime.utcnow()),
            "toxicity_analysis": kwargs.get("toxicity_analysis", {
                "overall_score": 0.1,
                "predictions": {
                    "toxic": 0.1,
                    "severe_toxic": 0.0,
                    "obscene": 0.0,
                    "threat": 0.0,
                    "insult": 0.0,
                    "identity_hate": 0.0
                },
                "confidence": 0.9,
                "processing_time_ms": 50
            }),
            "moderation_action": kwargs.get("moderation_action", {
                "action": "none",
                "confidence": 0.9,
                "reason": "Content is acceptable",
                "adjusted_threshold": 0.5,
                "applied_at": datetime.utcnow(),
                "applied_by": "system"
            }),
            "feedback": kwargs.get("feedback", {
                "user_reported": False,
                "community_flags": 0,
                "appeal_status": "none"
            })
        }

        await test_db["messages"].insert_one(message)
        return message

    return _create_message


@pytest.fixture
def create_test_user():
    """Factory function to create test users."""
    async def _create_user(test_db, **kwargs):
        import uuid
        from datetime import datetime

        user_id = kwargs.get("user_id", f"user_{uuid.uuid4().hex[:8]}")

        user = {
            "user_id": user_id,
            "username": kwargs.get("username", "testuser"),
            "email": kwargs.get("email", f"test{uuid.uuid4().hex[:8]}@example.com"),
            "created_at": kwargs.get("created_at", datetime.utcnow()),
            "last_active": kwargs.get("last_active", datetime.utcnow()),
            "behavior_profile": kwargs.get("behavior_profile", {
                "average_toxicity_score": 0.1,
                "message_frequency": 5,
                "moderation_history": {
                    "total_messages": 10,
                    "flagged_messages": 1,
                    "false_positives": 0,
                    "corrected_moderations": 0
                },
                "risk_level": "low",
                "trust_score": 0.8
            }),
            "preferences": kwargs.get("preferences", {
                "moderation_sensitivity": "moderate",
                "notification_settings": {
                    "email_notifications": True,
                    "moderation_warnings": True,
                    "account_status_changes": True
                }
            })
        }

        await test_db["users"].insert_one(user)
        return user

    return _create_user


# Test markers
pytest_plugins = []

# Custom markers for test categorization
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: Mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: Mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: Mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "ml: Mark test as requiring ML models"
    )
    config.addinivalue_line(
        "markers", "db: Mark test as requiring database"
    )