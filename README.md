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