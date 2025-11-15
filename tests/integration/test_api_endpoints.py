"""Integration tests for API endpoints."""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

from src.main import app


class TestModerationEndpoints:
    """Test cases for moderation API endpoints."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_analyze_message_endpoint_success(self):
        """Test successful message analysis endpoint."""
        with patch('src.services.moderation_service.moderation_service.analyze_message') as mock_analyze:
            mock_analyze.return_value = {
                "message_id": "msg_001",
                "toxicity_scores": {
                    "toxic": 0.1,
                    "severe_toxic": 0.0,
                    "obscene": 0.0,
                    "threat": 0.0,
                    "insult": 0.05,
                    "identity_hate": 0.0
                },
                "overall_score": 0.1,
                "moderation_action": {
                    "action": "none",
                    "confidence": 0.9,
                    "reason": "Content is acceptable",
                    "adjusted_threshold": 0.4
                },
                "context_analysis": {
                    "similarity_to_context": 0.3,
                    "user_risk_level": "medium",
                    "conversation_trend": "neutral"
                },
                "processing_time_ms": 150,
                "timestamp": "2024-01-01T00:00:00"
            }

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/moderation/analyze",
                    json={
                        "text": "Hello world!",
                        "conversation_id": "conv_001",
                        "user_id": "user_001"
                    }
                )

            assert response.status_code == 200
            data = response.json()
            assert "message_id" in data
            assert "toxicity_scores" in data
            assert "overall_score" in data
            assert "moderation_action" in data
            assert data["overall_score"] == 0.1
            assert data["moderation_action"]["action"] == "none"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_analyze_message_endpoint_validation_error(self):
        """Test message analysis endpoint with validation error."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/moderation/analyze",
                json={
                    "text": "",  # Empty text should cause validation error
                    "conversation_id": "conv_001",
                    "user_id": "user_001"
                }
            )

            assert response.status_code == 422  # Validation error

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_batch_analyze_endpoint_success(self):
        """Test successful batch analysis endpoint."""
        with patch('src.services.moderation_service.moderation_service.analyze_batch') as mock_analyze:
            mock_analyze.return_value = [
                {
                    "message_id": "msg_001",
                    "toxicity_scores": {"toxic": 0.1},
                    "overall_score": 0.1,
                    "moderation_action": {"action": "none", "confidence": 0.9},
                    "context_analysis": {},
                    "processing_time_ms": 100,
                    "timestamp": "2024-01-01T00:00:00"
                },
                {
                    "message_id": "msg_002",
                    "toxicity_scores": {"toxic": 0.8},
                    "overall_score": 0.8,
                    "moderation_action": {"action": "hide", "confidence": 0.8},
                    "context_analysis": {},
                    "processing_time_ms": 120,
                    "timestamp": "2024-01-01T00:00:00"
                }
            ]

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/moderation/batch",
                    json={
                        "messages": [
                            {
                                "content": "Hello world!",
                                "conversation_id": "conv_001",
                                "user_id": "user_001"
                            },
                            {
                                "content": "You are stupid!",
                                "conversation_id": "conv_001",
                                "user_id": "user_002"
                            }
                        ],
                        "priority": "normal"
                    }
                )

            assert response.status_code == 200
            data = response.json()
            assert "results" in data
            assert "total_processed" in data
            assert "batch_id" in data
            assert len(data["results"]) == 2
            assert data["total_processed"] == 2

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_batch_analyze_endpoint_too_large(self):
        """Test batch analysis endpoint with too many messages."""
        # Create a batch with more than 100 messages
        messages = [
            {
                "content": f"Message {i}",
                "conversation_id": "conv_001",
                "user_id": "user_001"
            }
            for i in range(101)
        ]

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/moderation/batch",
                json={
                    "messages": messages,
                    "priority": "normal"
                }
            )

            assert response.status_code == 400
            assert "cannot exceed 100 messages" in response.json()["detail"]

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_moderation_statistics_endpoint(self):
        """Test moderation statistics endpoint."""
        with patch('src.services.moderation_service.moderation_service.get_moderation_statistics') as mock_stats:
            mock_stats.return_value = {
                "period_days": 7,
                "total_actions": 1000,
                "action_breakdown": {
                    "none": 800,
                    "warn": 150,
                    "hide": 40,
                    "delete": 10
                }
            }

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/api/v1/moderation/statistics?days=7")

            assert response.status_code == 200
            data = response.json()
            assert "period_days" in data
            assert "total_actions" in data
            assert "action_breakdown" in data
            assert data["period_days"] == 7

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_moderation_statistics_endpoint_invalid_days(self):
        """Test moderation statistics endpoint with invalid days parameter."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/moderation/statistics?days=400")

            assert response.status_code == 400
            assert "between 1 and 365" in response.json()["detail"]

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_message_webhook_endpoint(self):
        """Test message webhook endpoint."""
        with patch('src.services.moderation_service.moderation_service.analyze_message') as mock_analyze:
            mock_analyze.return_value = {
                "message_id": "msg_webhook_001",
                "toxicity_scores": {"toxic": 0.2},
                "overall_score": 0.2,
                "moderation_action": {"action": "none", "confidence": 0.8},
                "context_analysis": {},
                "processing_time_ms": 150,
                "timestamp": "2024-01-01T00:00:00"
            }

            webhook_data = {
                "event": "message_created",
                "platform": "discord",
                "data": {
                    "message_id": "discord_msg_001",
                    "text": "Hello from Discord!",
                    "author_id": "discord_user_001",
                    "channel_id": "discord_channel_001",
                    "timestamp": "2024-01-01T00:00:00Z"
                }
            }

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/moderation/webhook/message-event",
                    json=webhook_data
                )

            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert data["status"] == "processed"
            assert data["moderation_action"] == "none"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_message_webhook_invalid_format(self):
        """Test message webhook endpoint with invalid format."""
        webhook_data = {
            "event": "message_created"
            # Missing required 'data' field
        }

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/moderation/webhook/message-event",
                json=webhook_data
            )

            assert response.status_code == 400
            assert "Invalid webhook format" in response.json()["detail"]

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_health_check_endpoint(self):
        """Test health check endpoint."""
        with patch('src.services.moderation_service.moderation_service.health_check') as mock_health:
            mock_health.return_value = {
                "status": "healthy",
                "components": {
                    "toxicity_detector": {"status": "healthy"},
                    "embedding_service": {"status": "healthy"},
                    "database": {"status": "connected"}
                }
            }

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/api/v1/moderation/health")

            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert "components" in data


class TestUserEndpoints:
    """Test cases for user management API endpoints."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_user_endpoint(self):
        """Test user creation endpoint."""
        with patch('src.services.user_service.user_service.create_user') as mock_create:
            mock_create.return_value = {
                "user_id": "user_001",
                "username": "testuser",
                "email": "test@example.com",
                "created_at": "2024-01-01T00:00:00",
                "behavior_profile": {
                    "average_toxicity_score": 0.0,
                    "risk_level": "medium",
                    "trust_score": 0.5
                }
            }

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/users/",
                    json={
                        "username": "testuser",
                        "email": "test@example.com",
                        "platform": "test"
                    }
                )

            assert response.status_code == 200
            data = response.json()
            assert "user_id" in data
            assert data["username"] == "testuser"
            assert data["email"] == "test@example.com"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_user_endpoint(self):
        """Test get user endpoint."""
        with patch('src.services.user_service.user_service.get_user') as mock_get:
            mock_get.return_value = {
                "user_id": "user_001",
                "username": "testuser",
                "email": "test@example.com",
                "behavior_profile": {"trust_score": 0.8}
            }

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/api/v1/users/user_001")

            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == "user_001"
            assert data["username"] == "testuser"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_user_not_found(self):
        """Test get user endpoint with non-existent user."""
        with patch('src.services.user_service.user_service.get_user') as mock_get:
            mock_get.return_value = None

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/api/v1/users/nonexistent")

            assert response.status_code == 404
            assert "User not found" in response.json()["detail"]

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_user_statistics_endpoint(self):
        """Test user statistics endpoint."""
        with patch('src.services.user_service.user_service.get_user_statistics') as mock_stats:
            mock_stats.return_value = {
                "user_id": "user_001",
                "username": "testuser",
                "period_days": 30,
                "message_stats": {
                    "total_messages": 100,
                    "avg_toxicity": 0.2,
                    "flagged_messages": 5
                },
                "activity_by_hour": [
                    {"hour": 14, "count": 15},
                    {"hour": 15, "count": 12}
                ]
            }

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/api/v1/users/user_001/statistics?days=30")

            assert response.status_code == 200
            data = response.json()
            assert "user_id" in data
            assert "message_stats" in data
            assert "activity_by_hour" in data
            assert data["message_stats"]["total_messages"] == 100

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_adjust_user_trust_endpoint(self):
        """Test user trust adjustment endpoint."""
        with patch('src.services.user_service.user_service.adjust_user_trust') as mock_adjust:
            mock_adjust.return_value = {
                "user_id": "user_001",
                "username": "testuser",
                "behavior_profile": {
                    "trust_score": 0.7,  # Increased from default
                    "risk_level": "low"
                }
            }

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/users/user_001/trust-adjustment",
                    json={
                        "adjustment_amount": 0.2,
                        "reason": "Good behavior improvement",
                        "moderator_notes": "User has been consistently positive"
                    }
                )

            assert response.status_code == 200
            data = response.json()
            assert "user_id" in data
            assert data["behavior_profile"]["trust_score"] == 0.7


class TestConversationEndpoints:
    """Test cases for conversation management API endpoints."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_conversation_endpoint(self):
        """Test conversation creation endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/conversations/",
                json={
                    "participants": ["user_001", "user_002"],
                    "metadata": {
                        "platform": "discord",
                        "topic": "General discussion",
                        "language": "en",
                        "moderation_level": "basic"
                    }
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert "conversation_id" in data
            assert "participants" in data
            assert len(data["participants"]) == 2

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_conversation_context_endpoint(self):
        """Test get conversation context endpoint."""
        with patch('src.services.embedding_service.embedding_service.calculate_context_embedding') as mock_embedding:
            mock_embedding.return_value = [0.1] * 384

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/api/v1/conversations/conv_001/context?window_size=5")

            # Should return 404 for non-existent conversation in our test setup
            # But the endpoint structure should be correct
            assert response.status_code in [200, 404]

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_search_conversations_endpoint(self):
        """Test conversation search endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/conversations/?platform=discord&page=1&page_size=20"
            )

            assert response.status_code == 200
            data = response.json()
            assert "conversations" in data
            assert "total_count" in data
            assert "page" in data
            assert "page_size" in data


class TestAnalyticsEndpoints:
    """Test cases for analytics API endpoints."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_analytics_dashboard_endpoint(self):
        """Test analytics dashboard endpoint."""
        with patch.multiple(
            'src.api.routes.analytics',
            get_analytics_overview=AsyncMock(return_value={
                "total_messages": 1000,
                "messages_last_24h": 50,
                "flagged_rate": 5.0
            }),
            get_toxicity_category_stats=AsyncMock(return_value=[]),
            get_user_risk_distribution=AsyncMock(return_value={"low": 100, "medium": 50, "high": 10}),
            get_performance_metrics=AsyncMock(return_value={
                "avg_processing_time_ms": 150.0,
                "api_uptime": 99.9
            }),
            get_recent_trends=AsyncMock(return_value={"daily_messages": []})
        ):
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/api/v1/analytics/dashboard?days=7")

            assert response.status_code == 200
            data = response.json()
            assert "overview" in data
            assert "top_toxicity_categories" in data
            assert "user_risk_distribution" in data
            assert "performance_metrics" in data
            assert "recent_trends" in data

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_system_health_endpoint(self):
        """Test system health endpoint."""
        with patch('src.api.routes.analytics.get_system_health') as mock_health:
            mock_health.return_value = {
                "status": "healthy",
                "version": "1.0.0",
                "models_loaded": ["detoxify", "sentence-transformers"],
                "database_connection": "healthy",
                "memory_usage_mb": 512.0
            }

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/api/v1/analytics/system-health")

            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert "version" in data
            assert "models_loaded" in data
            assert data["status"] == "healthy"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_export_analytics_data_endpoint(self):
        """Test analytics data export endpoint."""
        with patch('src.api.routes.analytics.get_system_health') as mock_health:
            mock_health.return_value = {
                "status": "healthy",
                "database_connection": "healthy"
            }

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/api/v1/analytics/export?format=json&days=30")

            assert response.status_code == 200
            data = response.json()
            assert "format" in data
            assert "data" in data
            assert "record_count" in data
            assert "period_days" in data
            assert data["format"] == "json"


class TestFeedbackEndpoints:
    """Test cases for feedback API endpoints."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_submit_appeal_endpoint(self):
        """Test appeal submission endpoint."""
        with patch('src.config.database.get_database') as mock_db:
            # Mock database operations
            mock_db.return_value = {
                "messages": AsyncMock(),
                "feedback": AsyncMock()
            }
            # Mock message exists
            mock_db.return_value["messages"].find_one.return_value = {
                "message_id": "msg_001",
                "user_id": "user_001"
            }

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/feedback/appeal",
                    json={
                        "message_id": "msg_001",
                        "original_action": "warn",
                        "appeal_reason": "False positive",
                        "user_explanation": "This message was not harmful"
                    }
                )

            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert "appeal_id" in data
            assert data["status"] == "submitted"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_submit_moderator_review_endpoint(self):
        """Test moderator review submission endpoint."""
        with patch('src.config.database.get_database') as mock_db:
            # Mock database operations
            mock_db.return_value = {
                "messages": AsyncMock(),
                "feedback": AsyncMock()
            }
            # Mock message exists
            mock_db.return_value["messages"].find_one.return_value = {
                "message_id": "msg_001",
                "user_id": "user_001"
            }

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/feedback/moderator-review",
                    json={
                        "message_id": "msg_001",
                        "reviewer_id": "moderator_001",
                        "original_action": "warn",
                        "final_action": "none",
                        "review_notes": "Upon review, this message is acceptable",
                        "confidence_score": 0.9
                    }
                )

            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert "review_id" in data
            assert data["status"] == "submitted"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_feedback_statistics_endpoint(self):
        """Test feedback statistics endpoint."""
        with patch('src.api.routes.feedback.get_feedback_statistics') as mock_stats:
            mock_stats.return_value = {
                "period_days": 30,
                "appeals": {
                    "total": 50,
                    "breakdown": {"pending": 10, "approved": 30, "rejected": 10},
                    "approval_rate": 60.0
                },
                "reviews": {
                    "total": 100,
                    "overturned_actions": 20,
                    "avg_confidence": 0.85,
                    "overturn_rate": 20.0
                }
            }

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/api/v1/feedback/statistics?days=30")

            assert response.status_code == 200
            data = response.json()
            assert "period_days" in data
            assert "appeals" in data
            assert "reviews" in data
            assert data["appeals"]["total"] == 50
            assert data["reviews"]["total"] == 100


class TestMainEndpoints:
    """Test cases for main application endpoints."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_root_endpoint(self):
        """Test root endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/")

            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "version" in data
            assert "status" in data
            assert "docs" in data

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """Test main health endpoint."""
        with patch('src.services.moderation_service.moderation_service.health_check') as mock_health:
            mock_health.return_value = {
                "status": "healthy",
                "components": {
                    "toxicity_detector": {"status": "healthy"},
                    "embedding_service": {"status": "healthy"},
                    "database": {"status": "connected"}
                }
            }

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert "version" in data
            assert "components" in data
            assert data["status"] == "healthy"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_models_info_endpoint(self):
        """Test models info endpoint."""
        with patch('src.services.toxicity_detector.toxicity_detector.get_model_info') as mock_toxicity:
            with patch('src.services.embedding_service.embedding_service.get_model_info') as mock_embedding:
                mock_toxicity.return_value = {
                    "model_name": "original",
                    "is_loaded": True,
                    "categories": ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]
                }
                mock_embedding.return_value = {
                    "model_name": "all-MiniLM-L6-v2",
                    "is_loaded": True,
                    "embedding_dimension": 384
                }

                async with AsyncClient(app=app, base_url="http://test") as client:
                    response = await client.get("/api/v1/models/info")

                assert response.status_code == 200
                data = response.json()
                assert "toxicity_detector" in data
                assert "embedding_service" in data
                assert "configuration" in data
                assert data["toxicity_detector"]["model_name"] == "original"
                assert data["embedding_service"]["model_name"] == "all-MiniLM-L6-v2"