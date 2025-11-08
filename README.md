🛡️ Hate Speech Moderation System

Docker
Docker
 FastAPI
FastAPI
 Python
Python
 MongoDB
MongoDB
 License
License

An adaptive hate speech moderation system that uses AI to detect toxic content in real-time. Built with FastAPI, MongoDB, and advanced machine learning models for context-aware content moderation.

✨ Features

🧠 Real-time Toxicity Detection - AI-powered analysis of text content
🎯 Context-Aware Moderation - Considers conversation history and user behavior
👤 User Behavior Tracking - Adaptive learning from user patterns
📊 Comprehensive Analytics - Detailed moderation statistics and insights
🚀 Fast API - High-performance RESTful API with interactive documentation
🐳 Docker Ready - One-command deployment with containerization
🔄 Feedback Loop - Appeals and moderator review system
📈 Monitoring - Health checks and system metrics
🚀 Quick Start

Prerequisites

Docker (Docker Desktop recommended)
Docker Compose
One-Command Setup

# Clone the repository
git clone https://github.com/dhruvav322/hate_speech_mongo.git
cd hate_speech_mongo

# Start the system
docker-compose up -d

# Verify it's running
curl http://localhost:8000/health
That's it! 🎉 Your hate speech moderation system is now running!

📚 API Documentation

Interactive Documentation

Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc
Core Endpoints

Analyze a Message

curl -X POST "http://localhost:8000/api/v1/moderation/analyze" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Hello world! How are you today?",
       "user_id": "user_123",
       "conversation_id": "conv_456"
     }'
System Health Check

curl http://localhost:8000/health
🧪 Try It Out

Clean Message

{
  "text": "I love this community! Everyone is so helpful and supportive.",
  "user_id": "alice_123",
  "conversation_id": "general_chat"
}
Result: Low toxicity score → Action: "none"

Questionable Content

{
  "text": "I think you're wrong about this topic.",
  "user_id": "bob_456",
  "conversation_id": "debate_room"
}
Result: Low-moderate score → Action: "warn"

Toxic Content

{
  "text": "You're stupid and nobody likes you!",
  "user_id": "toxic_user_789",
  "conversation_id": "main_forum"
}
Result: High toxicity score → Action: "hide" or "delete"

🏗️ Architecture

┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │ FastAPI App │ │ MongoDB │ │ ML Models │ │ │ │ │ │ │ │ • RESTful API │◄──▶│ • User History │◄──▶│ • Toxicity │ │ • Real-time │ │ • Conversations │ │ Detection │ │ • Analytics │ │ • Embeddings │ │ • Text Analysis │ └─────────────────┘ └─────────────────┘ └─────────────────┘
Core Components

🤖 AI Engine: Detoxify model for multi-label toxicity classification
📝 Text Analysis: Real-time content analysis with confidence scoring
👥 User Tracking: Behavior profiles and trust scoring
💬 Context Awareness: Conversation history and semantic embeddings
📊 Analytics Dashboard: Comprehensive moderation statistics
🔄 Feedback System: Appeals and learning loop
📊 Response Format

{
  "message_id": "msg_1698765432",
  "overall_score": 0.125,
  "moderation_action": {
    "recommended_action": "none",
    "confidence": 0.85,
    "reason": "Content appears to be within acceptable limits"
  },
  "processing_time_ms": 45,
  "timestamp": "2024-01-15T10:30:00.000Z"
}
Moderation Actions

Score Range	Action	Description
0.0 - 0.3	none	Content is safe
0.3 - 0.6	warn	User warned
0.6 - 0.8	hide	Content hidden
0.8 - 1.0	delete	Content removed
🛠️ Development

Local Development Setup

# Clone repository
git clone https://github.com/dhruvav322/hate_speech_mongo.git
cd hate_speech_mongo

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Start local services
docker-compose up -d mongo

# Run the application
python -m src.main
Project Structure

hate_speech_mongo/ ├── src/ │ ├── main.py # FastAPI application │ ├── config/ # Configuration management │ ├── models/ # Data models │ ├── services/ # Business logic │ ├── api/routes/ # API endpoints │ └── utils/ # Utilities ├── tests/ # Test suite ├── examples/ # Usage examples ├── scripts/ # Utility scripts ├── docker-compose.yml # Docker configuration ├── Dockerfile # Container definition └── requirements.txt # Python dependencies
🤝 Integration Examples

Python SDK Example

import requests

def analyze_message(text, user_id, conversation_id):
    response = requests.post(
        "http://localhost:8000/api/v1/moderation/analyze",
        json={
            "text": text,
            "user_id": user_id,
            "conversation_id": conversation_id
        }
    )
    return response.json()

# Usage
result = analyze_message("Hello world!", "user_123", "conv_456")
action = result["moderation_action"]["recommended_action"]
print(f"Recommended action: {action}")
JavaScript SDK Example

async function moderateContent(text, userId, conversationId) {
    const response = await fetch('http://localhost:8000/api/v1/moderation/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            text: text,
            user_id: userId,
            conversation_id: conversationId
        })
    });
    return await response.json();
}
Discord Bot Integration

import discord
import requests

client = discord.Client()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Check message content
    result = requests.post(
        "http://localhost:8000/api/v1/moderation/analyze",
        json={
            "text": message.content,
            "user_id": str(message.author.id),
            "conversation_id": str(message.channel.id)
        }
    ).json()

    action = result["moderation_action"]["recommended_action"]

    # Apply moderation action
    if action == "delete":
        await message.delete()
    elif action == "warn":
        await message.channel.send(f"⚠️ Warning: Please keep conversation civil, {message.author.mention}")
📊 Analytics Dashboard

Key Metrics

Total Messages Processed: Number of messages analyzed
Flagged Rate: Percentage of messages requiring moderation
False Positive Rate: Accuracy of moderation decisions
Processing Speed: Average analysis time per message
User Risk Distribution: Breakdown of user behavior patterns
Example Dashboard

# Get analytics overview
curl http://localhost:8000/api/v1/analytics/dashboard

# Get user statistics
curl http://localhost:8000/api/v1/users/system/statistics

# Get moderation trends
curl http://localhost:8000/api/v1/analytics/moderation-trends
🔒 Security Features

API Authentication: Support for API keys and JWT tokens
Rate Limiting: Configurable request limits per client
Input Validation: Comprehensive input sanitization and validation
Error Handling: Secure error responses without information leakage
CORS Configuration: Configurable cross-origin resource sharing
🌐 Deployment Options

Docker Production Deployment

# Production configuration
docker-compose -f docker-compose.prod.yml up -d

# Scale horizontally
docker-compose up -d --scale app=3
Cloud Deployment

AWS ECS/EKS: Container orchestration on AWS
Google Cloud Run: Serverless container deployment
Azure Container Instances: Managed container hosting
DigitalOcean App Platform: Simplified container deployment
🎯 Use Cases

Social Media Platforms

Comment Moderation: Automatic filtering of user comments
Post Review: Pre-moderation of user-generated content
Direct Message Filtering: Real-time chat monitoring
Gaming Communities

In-Game Chat: Filter toxic language in multiplayer games
Player Reports: Automated review of player reports
Forum Moderation: Community forum content management
Educational Platforms

Assignment Review: Check for inappropriate content in submissions
Discussion Forums: Maintain constructive learning environments
Student Communication: Monitor classroom messaging systems
🤝 Contributing

We welcome contributions! Here's how to get started:

Fork the repository
Create a feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m "Add amazing feature")
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request
Development Guidelines

Code Style: Follow PEP 8, use black for formatting
Testing: Maintain 90%+ test coverage
Documentation: Update README and API docs for new features
Security: Consider security implications of all changes
📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments

Detoxify - Toxicity classification models
FastAPI - Modern Python web framework
MongoDB - NoSQL database
Sentence Transformers - Text embedding models
📞 Support

Issues: GitHub Issues
Discussions: GitHub Discussions
🗺️ Roadmap

 Real-time Streaming - WebSocket support for live moderation
 Multi-language Support - Support for non-English content
 Custom Model Training - Train models on your data
 Advanced Analytics - Enhanced reporting and insights
 Mobile SDK - Native iOS and Android SDKs
 GraphQL API - GraphQL endpoint support
<div align="center">
🛡️ Built with ❤️ for safer online communities

⭐ Star this repo | 🐛 Report a Bug | 📖 Documentation
</div>
