<<<<<<< HEAD
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
=======
# Hate Speech Moderation System

An adaptive hate speech moderation system that uses MongoDB to store user interaction history and context embeddings for increasingly accurate moderation recommendations.

## 🚀 Features

- **Adaptive Moderation**: Learns from user behavior patterns to provide increasingly accurate moderation
- **Context-Aware Analysis**: Uses conversation context and semantic embeddings for better understanding
- **Multi-Label Toxicity Detection**: Detects 6 categories of toxicity using state-of-the-art ML models
- **Real-Time Processing**: Fast API responses with optimized batch processing
- **User Behavior Tracking**: Maintains trust scores and risk levels for personalized moderation
- **Feedback Loop**: Appeals and moderator reviews improve system accuracy over time
- **Comprehensive Analytics**: Detailed insights and reporting capabilities
- **Scalable Architecture**: Docker-based deployment with monitoring

## 🏗️ Architecture

### Core Components

1. **Toxicity Detection Engine** - Detoxify library for multi-label classification
2. **Embedding Service** - Sentence transformers for semantic understanding
3. **Adaptive Moderation Service** - Context-aware scoring with user behavior adaptation
4. **User Behavior Service** - Trust scoring and risk level management
5. **MongoDB Storage** - User history, conversations, and context embeddings
6. **RESTful API** - Complete integration endpoints with webhook support

### MongoDB Schema

- **Users**: Behavior profiles, trust scores, moderation history
- **Conversations**: Thread metadata and context embeddings
- **Messages**: Content with analysis results and moderation actions
- **Context Embeddings**: Pre-computed semantic vectors for efficiency
- **Feedback**: Appeals, moderator reviews, and learning data

## 🛠️ Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- MongoDB (if not using Docker)

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd hate_speech_mongo
   ```

2. **Start the system**
   ```bash
   docker-compose up -d
   ```

3. **Verify installation**
   ```bash
   curl http://localhost:8000/health
   ```

4. **Access API documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start MongoDB**
   ```bash
   docker run -d -p 27017:27017 --name mongodb mongo:7.0
   ```

4. **Run the application**
   ```bash
   python -m src.main
   ```

## 📚 API Usage

### Analyze a Single Message

```python
import httpx

async def analyze_message():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/moderation/analyze",
            json={
                "text": "Hello world! How are you doing today?",
                "conversation_id": "conv_001",
                "user_id": "user_001",
                "context": {
                    "platform": "discord",
                    "message_type": "chat"
                }
            }
        )

        result = response.json()
        print(f"Toxicity Score: {result['overall_score']}")
        print(f"Recommended Action: {result['moderation_action']['action']}")
```

### Batch Analysis

```python
async def batch_analyze():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/moderation/batch",
            json={
                "messages": [
                    {
                        "content": "You're awesome!",
                        "conversation_id": "conv_001",
                        "user_id": "user_001"
                    },
                    {
                        "content": "I hate everyone!",
                        "conversation_id": "conv_001",
                        "user_id": "user_002"
                    }
                ],
                "priority": "normal"
            }
        )

        results = response.json()
        for i, result in enumerate(results['results']):
            print(f"Message {i+1}: {result['overall_score']} -> {result['moderation_action']['action']}")
```

### Create User Profile

```python
async def create_user():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/users/",
            json={
                "username": "alice",
                "email": "alice@example.com",
                "platform": "discord",
                "preferences": {
                    "moderation_sensitivity": "moderate"
                }
            }
        )

        user = response.json()
        print(f"Created user: {user['user_id']}")
```

### Webhook Integration

```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/webhook/message")
async def handle_message(webhook_data: dict):
    # Forward to moderation system
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/moderation/webhook/message-event",
            json={
                "event": "message_created",
                "platform": "discord",
                "data": webhook_data
            }
        )

        moderation_result = response.json()

        # Apply moderation action
        if moderation_result["moderation_action"] == "delete":
            await delete_message(webhook_data["message_id"])
        elif moderation_result["moderation_action"] == "warn":
            await warn_user(webhook_data["author_id"])
```

## 🔧 Configuration

### Environment Variables

```env
# Database
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=hate_speech_mitigation

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_SECRET_KEY=your-secret-key-here

# Model Configuration
DETOXIFY_MODEL=original
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384

# Moderation Settings
DEFAULT_TOXICITY_THRESHOLD=0.5
CONTEXT_WINDOW_SIZE=5
USER_HISTORY_LIMIT=50
BATCH_SIZE=32

# Performance
MAX_CONCURRENT_REQUESTS=100
REDIS_URL=redis://localhost:6379
```

### Moderation Thresholds

- **Score < 0.3**: Allow message
- **Score 0.3-0.6**: Issue warning
- **Score 0.6-0.8**: Hide message
- **Score 0.8-0.95**: Delete message
- **Score > 0.95**: Ban user

## 📊 Monitoring

### Health Checks

```bash
# Main health endpoint
curl http://localhost:8000/health

# Service-specific health
curl http://localhost:8000/api/v1/moderation/health
```

### Analytics Dashboard

```bash
# Get system overview
curl http://localhost:8000/api/v1/analytics/dashboard

# User statistics
curl http://localhost:8000/api/v1/users/system/statistics

# Moderation trends
curl http://localhost:8000/api/v1/analytics/moderation-trends
```

### Grafana Dashboard

Access Grafana at http://localhost:3000 (admin/admin)

## 🧪 Testing

### Run All Tests

```bash
pytest --cov=src tests/
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Tests requiring ML models
pytest -m ml

# Fast tests (exclude slow ones)
pytest -m "not slow"
```

### Test Coverage

```bash
pytest --cov=src --cov-report=html tests/
open htmlcov/index.html
```

## 🔒 Security

### API Authentication

```python
# Using API Key
headers = {"X-API-Key": "your-api-key"}
response = httpx.get("http://localhost:8000/api/v1/users/", headers=headers)

# Using JWT Token
headers = {"Authorization": "Bearer your-jwt-token"}
response = httpx.get("http://localhost:8000/api/v1/users/", headers=headers)
```

### Rate Limiting

- Default: 1000 requests per minute per API key
- Custom limits configurable per client
- Exponential backoff for rate limit violations

## 📈 Performance

### Optimization Features

- **Model Caching**: ML models pre-loaded and cached
- **Batch Processing**: Efficient handling of multiple messages
- **Async Operations**: Non-blocking I/O throughout
- **Database Indexing**: Optimized queries for large datasets
- **Embedding Cache**: Redis caching for frequent embeddings

### Benchmarks

- **Single message analysis**: ~50-150ms
- **Batch processing (32 messages)**: ~200-500ms
- **Memory usage**: ~500MB base + ~200MB models
- **Concurrent requests**: 100+ simultaneous

## 🚀 Deployment

### Production Docker

```bash
# Build and deploy
docker-compose -f docker-compose.yml up -d

# Scale application
docker-compose up -d --scale app=3
```

### Environment Configuration

```yaml
# docker-compose.prod.yml
services:
  app:
    image: hatespeech-moderation:latest
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
    environment:
      - LOG_LEVEL=INFO
      - WORKERS=4
```

### CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: pytest --cov=src tests/

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          docker build -t hatespeech-moderation .
          docker push ${{ secrets.REGISTRY_URL }}/hatespeech-moderation
```

## 🔄 Feedback Loop

### Submit Appeal

```python
async def submit_appeal():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/feedback/appeal",
            json={
                "message_id": "msg_001",
                "original_action": "warn",
                "appeal_reason": "False positive",
                "user_explanation": "This was clearly a joke among friends"
            }
        )
```

### Moderator Review

```python
async def review_decision():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/feedback/moderator-review",
            json={
                "message_id": "msg_001",
                "reviewer_id": "moderator_001",
                "original_action": "warn",
                "final_action": "none",
                "review_notes": "Context shows this is acceptable banter",
                "confidence_score": 0.9
            }
        )
```

## 🛠️ Development

### Code Structure

```
src/
├── config/          # Configuration management
├── models/          # Data models and schemas
├── services/        # Business logic services
├── api/            # FastAPI routes and middleware
└── utils/          # Utility functions

tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
└── conftest.py     # Test configuration
```

### Adding New Features

1. **Add data models** in `src/models/`
2. **Implement business logic** in `src/services/`
3. **Create API endpoints** in `src/api/routes/`
4. **Write tests** in `tests/`
5. **Update documentation**

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/

# Security scan
bandit -r src/
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Issues**: Create an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions

## 🗺️ Roadmap

- [ ] Real-time streaming moderation
- [ ] Multi-language support
- [ ] Custom model training pipeline
- [ ] Advanced analytics dashboard
- [ ] Mobile SDK
- [ ] GraphQL API
- [ ] Edge deployment options

---

**Built with ❤️ for safer online communities**
>>>>>>> compyle/hate-speech-mitigation-agent
