# 🛡️ Hate Speech Moderation System

[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0-green.svg)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An adaptive hate speech moderation system that uses AI to detect toxic content in real-time. Built with FastAPI, MongoDB, and advanced machine learning models for context-aware content moderation.

## ✨ Features

- 🧠 **Real-time Toxicity Detection** - AI-powered analysis of text content
- 🎯 **Context-Aware Moderation** - Considers conversation history and user behavior
- 👤 **User Behavior Tracking** - Adaptive learning from user patterns
- 📊 **Comprehensive Analytics** - Detailed moderation statistics and insights
- 🚀 **Fast API** - High-performance RESTful API with interactive documentation
- 🐳 **Docker Ready** - One-command deployment with containerization
- 🔄 **Feedback Loop** - Appeals and moderator review system
- 📈 **Monitoring** - Health checks and system metrics

## 🚀 Quick Start

### Prerequisites

- [Docker](https://www.docker.com/) (Docker Desktop recommended)
- [Docker Compose](https://docs.docker.com/compose/install/)

### One-Command Setup

```bash
# Clone the repository
git clone https://github.com/dhruvav322/hate_speech_mongo.git
cd hate_speech_mongo

# Start the system
docker-compose up -d

# Verify it's running
curl http://localhost:8000/health
```

That's it! 🎉 Your hate speech moderation system is now running!

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Core Endpoints

#### Analyze a Message
```bash
curl -X POST "http://localhost:8000/api/v1/moderation/analyze" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Hello world! How are you today?",
       "user_id": "user_123",
       "conversation_id": "conv_456"
     }'
```

#### System Health Check
```bash
curl http://localhost:8000/health
```

## 🧪 Try It Out

### Clean Message
```json
{
  "text": "I love this community! Everyone is so helpful and supportive.",
  "user_id": "alice_123",
  "conversation_id": "general_chat"
}
```
**Result**: Low toxicity score → Action: "none"

### Questionable Content
```json
{
  "text": "I think you're wrong about this topic.",
  "user_id": "bob_456",
  "conversation_id": "debate_room"
}
```
**Result**: Low-moderate score → Action: "warn"

### Toxic Content
```json
{
  "text": "You're stupid and nobody likes you!",
  "user_id": "toxic_user_789",
  "conversation_id": "main_forum"
}
```
**Result**: High toxicity score → Action: "hide" or "delete"

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │    MongoDB     │    │   ML Models    │
│                 │    │                 │    │                 │
│ • RESTful API   │◄──▶│ • User History  │◄──▶│ • Toxicity      │
│ • Real-time     │    │ • Conversations │    │   Detection     │
│ • Analytics     │    │ • Embeddings    │    │ • Text Analysis │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Core Components

- **🤖 AI Engine**: Detoxify model for multi-label toxicity classification
- **📝 Text Analysis**: Real-time content analysis with confidence scoring
- **👥 User Tracking**: Behavior profiles and trust scoring
- **💬 Context Awareness**: Conversation history and semantic embeddings
- **📊 Analytics Dashboard**: Comprehensive moderation statistics
- **🔄 Feedback System**: Appeals and learning loop

## 📊 Response Format

```json
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
```

### Moderation Actions

| Score Range | Action | Description |
|-------------|--------|-------------|
| 0.0 - 0.3   | `none` | Content is safe |
| 0.3 - 0.6   | `warn` | User warned |
| 0.6 - 0.8   | `hide` | Content hidden |
| 0.8 - 1.0   | `delete` | Content removed |

## 🛠️ Development

### Local Development Setup

```bash
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
```

### Project Structure
```
hate_speech_mongo/
├── src/
│   ├── main.py              # FastAPI application
│   ├── config/              # Configuration management
│   ├── models/              # Data models
│   ├── services/            # Business logic
│   ├── api/routes/          # API endpoints
│   └── utils/               # Utilities
├── tests/                   # Test suite
├── examples/                # Usage examples
├── scripts/                 # Utility scripts
├── docker-compose.yml       # Docker configuration
├── Dockerfile              # Container definition
└── requirements.txt        # Python dependencies
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test categories
pytest tests/unit/           # Unit tests
pytest tests/integration/    # Integration tests
```

## 📈 Monitoring & Metrics

### Health Checks
- **API Health**: http://localhost:8000/health
- **Service Status**: http://localhost:8000/api/v1/moderation/health

### Monitoring
- **Response Time**: Average processing time per message
- **Accuracy Rate**: Model confidence and prediction accuracy
- **System Health**: Database connections, model loading status
- **Usage Statistics**: Number of messages processed, actions taken

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

### Customization Options

- **Sensitivity Levels**: Adjust toxicity thresholds for different communities
- **Context Window**: Configure how much conversation history to consider
- **User Behavior**: Tune trust scoring and risk assessment
- **Model Selection**: Choose different AI models for specific use cases

## 🤝 Integration Examples

### Python SDK Example
```python
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
```

### JavaScript SDK Example
```javascript
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
```

### Discord Bot Integration
```python
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
```

## 📊 Analytics Dashboard

### Key Metrics
- **Total Messages Processed**: Number of messages analyzed
- **Flagged Rate**: Percentage of messages requiring moderation
- **False Positive Rate**: Accuracy of moderation decisions
- **Processing Speed**: Average analysis time per message
- **User Risk Distribution**: Breakdown of user behavior patterns

### Example Dashboard
```bash
# Get analytics overview
curl http://localhost:8000/api/v1/analytics/dashboard

# Get user statistics
curl http://localhost:8000/api/v1/users/system/statistics

# Get moderation trends
curl http://localhost:8000/api/v1/analytics/moderation-trends
```

## 🔒 Security Features

- **API Authentication**: Support for API keys and JWT tokens
- **Rate Limiting**: Configurable request limits per client
- **Input Validation**: Comprehensive input sanitization and validation
- **Error Handling**: Secure error responses without information leakage
- **CORS Configuration**: Configurable cross-origin resource sharing

## 🌐 Deployment Options

### Docker Production Deployment
```bash
# Production configuration
docker-compose -f docker-compose.prod.yml up -d

# Scale horizontally
docker-compose up -d --scale app=3
```

### Cloud Deployment
- **AWS ECS/EKS**: Container orchestration on AWS
- **Google Cloud Run**: Serverless container deployment
- **Azure Container Instances**: Managed container hosting
- **DigitalOcean App Platform**: Simplified container deployment

### Environment Variables
```yaml
# docker-compose.prod.yml
services:
  app:
    image: dhruvav322/hate-speech-moderation:latest
    environment:
      - LOG_LEVEL=INFO
      - WORKERS=4
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
```

## 🎯 Use Cases

### Social Media Platforms
- **Comment Moderation**: Automatic filtering of user comments
- **Post Review**: Pre-moderation of user-generated content
- **Direct Message Filtering**: Real-time chat monitoring

### Gaming Communities
- **In-Game Chat**: Filter toxic language in multiplayer games
- **Player Reports**: Automated review of player reports
- **Forum Moderation**: Community forum content management

### Educational Platforms
- **Assignment Review**: Check for inappropriate content in submissions
- **Discussion Forums**: Maintain constructive learning environments
- **Student Communication**: Monitor classroom messaging systems

### Customer Support
- **Support Tickets**: Flag abusive customer interactions
- **Chat Support**: Filter toxic language in customer service
- **Review Systems**: Moderate product and service reviews

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
   ```bash
   git clone https://github.com/dhruvav322/hate_speech_mongo.git
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make your changes**
   - Add your feature or fix
   - Write tests for your changes
   - Update documentation

4. **Run tests**
   ```bash
   pytest --cov=src
   ```

5. **Commit and push**
   ```bash
   git commit -m "Add amazing feature"
   git push origin feature/amazing-feature
   ```

6. **Create a Pull Request**

### Development Guidelines
- **Code Style**: Follow PEP 8, use black for formatting
- **Testing**: Maintain 90%+ test coverage
- **Documentation**: Update README and API docs for new features
- **Security**: Consider security implications of all changes

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[Detoxify](https://github.com/unitaryai/detoxify)** - Toxicity classification models
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern Python web framework
- **[MongoDB](https://www.mongodb.com/)** - NoSQL database
- **[Sentence Transformers](https://www.sbert.net/)** - Text embedding models

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/dhruvav322/hate_speech_mongo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/dhruvav322/hate_speech_mongo/discussions)
- **Email**: dhruvav@example.com

## 🗺️ Roadmap

- [ ] **Real-time Streaming** - WebSocket support for live moderation
- [ ] **Multi-language Support** - Support for non-English content
- [ ] **Custom Model Training** - Train models on your data
- [ ] **Advanced Analytics** - Enhanced reporting and insights
- [ ] **Mobile SDK** - Native iOS and Android SDKs
- [ ] **GraphQL API** - GraphQL endpoint support
- [ ] **Edge Deployment** - Cloudflare Workers deployment

---

<div align="center">

**🛡️ Built with ❤️ for safer online communities**

[⭐ Star this repo](https://github.com/dhruvav322/hate_speech_mongo) | [🐛 Report a Bug](https://github.com/dhruvav322/hate_speech_mongo/issues) | [📖 Documentation](https://github.com/dhruvav322/hate_speech_mongo/wiki)

</div>