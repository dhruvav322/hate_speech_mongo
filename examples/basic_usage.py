"""
Basic usage example for the Hate Speech Moderation System.

This example demonstrates:
- Creating user profiles
- Analyzing single messages
- Batch processing
- Handling feedback
- Viewing analytics
"""

import asyncio
import httpx
import json
from datetime import datetime


class ModerationClient:
    """Simple client for interacting with the moderation API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def health_check(self):
        """Check if the API is healthy."""
        response = await self.client.get(f"{self.base_url}/health")
        return response.json()

    async def create_user(self, username: str, email: str, platform: str):
        """Create a new user profile."""
        response = await self.client.post(
            f"{self.base_url}/api/v1/users/",
            json={
                "username": username,
                "email": email,
                "platform": platform,
                "preferences": {
                    "moderation_sensitivity": "moderate"
                }
            }
        )
        return response.json()

    async def analyze_message(self, text: str, user_id: str = None, conversation_id: str = None):
        """Analyze a single message for toxicity."""
        response = await self.client.post(
            f"{self.base_url}/api/v1/moderation/analyze",
            json={
                "text": text,
                "user_id": user_id,
                "conversation_id": conversation_id,
                "context": {
                    "platform": "example",
                    "message_type": "chat"
                }
            }
        )
        return response.json()

    async def batch_analyze(self, messages: list):
        """Analyze multiple messages in batch."""
        response = await self.client.post(
            f"{self.base_url}/api/v1/moderation/batch",
            json={
                "messages": messages,
                "priority": "normal"
            }
        )
        return response.json()

    async def get_user_stats(self, user_id: str, days: int = 30):
        """Get user statistics."""
        response = await self.client.get(
            f"{self.base_url}/api/v1/users/{user_id}/statistics?days={days}"
        )
        return response.json()

    async def get_analytics_dashboard(self, days: int = 7):
        """Get analytics dashboard."""
        response = await self.client.get(
            f"{self.base_url}/api/v1/analytics/dashboard?days={days}"
        )
        return response.json()

    async def submit_appeal(self, message_id: str, original_action: str, reason: str, explanation: str):
        """Submit an appeal for a moderation decision."""
        response = await self.client.post(
            f"{self.base_url}/api/v1/feedback/appeal",
            json={
                "message_id": message_id,
                "original_action": original_action,
                "appeal_reason": reason,
                "user_explanation": explanation
            }
        )
        return response.json()


async def main():
    """Run the example usage scenario."""
    client = ModerationClient()

    try:
        print("🚀 Hate Speech Moderation System - Basic Usage Example")
        print("=" * 60)

        # 1. Health check
        print("\n1. Checking API health...")
        health = await client.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Version: {health['version']}")

        if health['status'] != 'healthy':
            print("❌ API is not healthy. Please start the system first.")
            print("   Run: docker-compose up -d")
            return

        # 2. Create users
        print("\n2. Creating user profiles...")

        alice = await client.create_user("alice", "alice@example.com", "discord")
        print(f"   ✅ Created Alice: {alice['user_id']}")

        bob = await client.create_user("bob", "bob@example.com", "discord")
        print(f"   ✅ Created Bob: {bob['user_id']}")

        charlie = await client.create_user("charlie", "charlie@example.com", "discord")
        print(f"   ✅ Created Charlie: {charlie['user_id']}")

        # 3. Analyze different types of messages
        print("\n3. Analyzing messages...")

        # Clean message
        clean_result = await client.analyze_message(
            "Hello everyone! How are you doing today? 😊",
            user_id=alice['user_id'],
            conversation_id="conv_general_001"
        )
        print(f"   Clean message: {clean_result['overall_score']:.3f} -> {clean_result['moderation_action']['action']}")

        # Borderline message
        borderline_result = await client.analyze_message(
            "I think you're completely wrong about this topic.",
            user_id=bob['user_id'],
            conversation_id="conv_general_001"
        )
        print(f"   Borderline message: {borderline_result['overall_score']:.3f} -> {borderline_result['moderation_action']['action']}")

        # Toxic message
        toxic_result = await client.analyze_message(
            "You're stupid and nobody likes you!",
            user_id=charlie['user_id'],
            conversation_id="conv_general_001"
        )
        print(f"   Toxic message: {toxic_result['overall_score']:.3f} -> {toxic_result['moderation_action']['action']}")

        # 4. Batch processing
        print("\n4. Batch processing multiple messages...")

        batch_messages = [
            {
                "content": "Great job on the presentation! 👏",
                "conversation_id": "conv_work_001",
                "user_id": alice['user_id']
            },
            {
                "content": "This is the worst thing I've ever seen.",
                "conversation_id": "conv_work_001",
                "user_id": bob['user_id']
            },
            {
                "content": "I disagree with your opinion but respect your perspective.",
                "conversation_id": "conv_work_001",
                "user_id": charlie['user_id']
            }
        ]

        batch_result = await client.batch_analyze(batch_messages)
        print(f"   Processed {batch_result['total_processed']} messages in {batch_result['processing_time_ms']}ms")

        for i, result in enumerate(batch_result['results']):
            print(f"   Message {i+1}: {result['overall_score']:.3f} -> {result['moderation_action']['action']}")

        # 5. Get user statistics
        print("\n5. Getting user statistics...")

        alice_stats = await client.get_user_stats(alice['user_id'])
        print(f"   Alice's messages: {alice_stats['message_stats']['total_messages']}")
        print(f"   Alice's avg toxicity: {alice_stats['message_stats']['avg_toxicity']:.3f}")

        # 6. View analytics dashboard
        print("\n6. System analytics...")

        dashboard = await client.get_analytics_dashboard()
        print(f"   Total messages: {dashboard['overview']['total_messages']}")
        print(f"   Flagged rate: {dashboard['overview']['flagged_rate']:.1f}%")
        print(f"   Active users: {dashboard['overview']['active_users']}")

        # 7. Submit an appeal (example)
        if toxic_result['moderation_action']['action'] != 'none':
            print("\n7. Submitting appeal for moderated message...")

            appeal = await client.submit_appeal(
                message_id=toxic_result['message_id'],
                original_action=toxic_result['moderation_action']['action'],
                reason="False positive",
                explanation="This was meant as constructive criticism in a private conversation"
            )
            print(f"   Appeal submitted: {appeal['appeal_id']}")
            print(f"   Status: {appeal['status']}")

        print("\n✅ Example completed successfully!")
        print("\n📚 Next steps:")
        print("   - Visit http://localhost:8000/docs for full API documentation")
        print("   - Check http://localhost:3000 for Grafana monitoring")
        print("   - Review the code in src/ to understand the implementation")

    except httpx.ConnectError:
        print("❌ Cannot connect to the API.")
        print("   Make sure the system is running: docker-compose up -d")
        print("   Check if the service is healthy: curl http://localhost:8000/health")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())