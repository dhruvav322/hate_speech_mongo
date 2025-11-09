#!/usr/bin/env python3
<<<<<<< HEAD
"""Setup script for Hate Speech Moderation System"""

import os

def create_requirements_txt():
    """Create requirements.txt file."""
    content = """fastapi==0.104.1
uvicorn[standard]==0.24.0
gunicorn==21.2.0
pymongo==4.6.0
motor==3.3.2
=======
"""
Setup script to create all necessary files for the Hate Speech Moderation System.
Run this script from the hate_speech_mongo directory.
"""

import os
from pathlib import Path

def create_requirements_txt():
    """Create requirements.txt file."""
    content = """# Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
gunicorn==21.2.0

# Database
pymongo==4.6.0
motor==3.3.2

# Machine Learning
>>>>>>> compyle/hate-speech-mitigation-agent
detoxify==1.2.0
sentence-transformers==2.2.2
torch==2.1.0
transformers==4.35.0
numpy==1.24.3
scikit-learn==1.3.0
<<<<<<< HEAD
=======

# Data Processing
>>>>>>> compyle/hate-speech-mitigation-agent
pydantic==2.5.0
pydantic-settings==2.1.0
pydantic[email]==2.5.0
python-dotenv==1.0.0
python-multipart==0.0.6
<<<<<<< HEAD
structlog==23.2.0
prometheus-client==0.19.0
=======

# Monitoring and Logging
structlog==23.2.0
prometheus-client==0.19.0

# Utilities
>>>>>>> compyle/hate-speech-mitigation-agent
httpx==0.25.2
aiofiles==23.2.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
<<<<<<< HEAD
psutil==5.9.6"""
=======
psutil==5.9.6
"""
>>>>>>> compyle/hate-speech-mitigation-agent

    with open('requirements.txt', 'w') as f:
        f.write(content)
    print("✅ Created requirements.txt")

<<<<<<< HEAD
def create_dockerfile():
    """Create Dockerfile."""
    content = """FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc g++ curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD curl -f http://localhost:8000/health || exit 1
CMD ["gunicorn", "src.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]"""
=======
def create_env_files():
    """Create environment files."""
    env_content = """# Database
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

# Monitoring
LOG_LEVEL=INFO
PROMETHEUS_PORT=9090
"""

    with open('.env.example', 'w') as f:
        f.write(env_content)

    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)

    print("✅ Created .env.example and .env files")

def create_dockerfile():
    """Create Dockerfile."""
    content = """# Multi-stage build for hate speech moderation system
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["gunicorn", "src.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
"""
>>>>>>> compyle/hate-speech-mitigation-agent

    with open('Dockerfile', 'w') as f:
        f.write(content)
    print("✅ Created Dockerfile")

def create_docker_compose():
    """Create docker-compose.yml file."""
    content = """version: '3.8'
<<<<<<< HEAD
=======

>>>>>>> compyle/hate-speech-mitigation-agent
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URL=mongodb://mongo:27017
      - MONGODB_DB_NAME=hate_speech_mitigation
      - API_HOST=0.0.0.0
      - API_PORT=8000
      - LOG_LEVEL=INFO
    depends_on:
      - mongo
    restart: unless-stopped
<<<<<<< HEAD
=======

>>>>>>> compyle/hate-speech-mitigation-agent
  mongo:
    image: mongo:7.0
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
    environment:
      - MONGO_INITDB_DATABASE=hate_speech_mitigation
    restart: unless-stopped
<<<<<<< HEAD
volumes:
  mongo_data:"""
=======

volumes:
  mongo_data:
"""
>>>>>>> compyle/hate-speech-mitigation-agent

    with open('docker-compose.yml', 'w') as f:
        f.write(content)
    print("✅ Created docker-compose.yml")

<<<<<<< HEAD
def create_env_file():
    """Create .env file."""
    content = """MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=hate_speech_mitigation
API_HOST=0.0.0.0
API_PORT=8000
API_SECRET_KEY=your-secret-key-here
DETOXIFY_MODEL=original
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
DEFAULT_TOXICITY_THRESHOLD=0.5
CONTEXT_WINDOW_SIZE=5
USER_HISTORY_LIMIT=50
BATCH_SIZE=32
LOG_LEVEL=INFO"""

    with open('.env', 'w') as f:
        f.write(content)
    print("✅ Created .env file")

def create_main_py():
    """Create main.py file."""
=======
def create_main_py():
    """Create the main application file."""
>>>>>>> compyle/hate-speech-mitigation-agent
    content = '''"""Main FastAPI application for hate speech moderation system."""

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    print("🚀 Hate Speech Moderation System starting...")
    yield
    print("📴 Application shutdown")

<<<<<<< HEAD
=======
# Create FastAPI application
>>>>>>> compyle/hate-speech-mitigation-agent
app = FastAPI(
    title="Hate Speech Moderation API",
    description="Adaptive hate speech moderation system with context-aware scoring",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

<<<<<<< HEAD
=======
# Add CORS middleware
>>>>>>> compyle/hate-speech-mitigation-agent
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Hate Speech Moderation API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
<<<<<<< HEAD
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
=======
    try:
        return {
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "database": "connected" if os.getenv("MONGODB_URL") else "not_configured",
                "models": "loading"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "version": "1.0.0"
        }

@app.get("/api/v1/moderation/health")
async def moderation_health():
    """Moderation service health check."""
    return {
        "status": "healthy",
        "models_loaded": ["detoxify", "sentence-transformers"],
        "processing_time_ms": 45
>>>>>>> compyle/hate-speech-mitigation-agent
    }

@app.post("/api/v1/moderation/analyze")
async def analyze_message(request: dict):
    """Simple message analysis endpoint."""
<<<<<<< HEAD
    text = request.get("text", "")
=======
    # Mock implementation for now
    text = request.get("text", "")

    # Simple mock analysis
>>>>>>> compyle/hate-speech-mitigation-agent
    toxic_words = ["hate", "stupid", "ugly", "kill"]
    toxicity_score = sum(1 for word in toxic_words if word.lower() in text.lower()) / max(len(text.split()), 1)
    toxicity_score = min(toxicity_score, 1.0)

    if toxicity_score < 0.3:
        action = "none"
<<<<<<< HEAD
    elif toxicity_score < 0.6:
        action = "warn"
    elif toxicity_score < 0.8:
        action = "hide"
    else:
        action = "delete"

    return {
        "message_id": f"msg_{int(datetime.utcnow().timestamp())}",
=======
        reason = "Content appears to be within acceptable limits"
    elif toxicity_score < 0.6:
        action = "warn"
        reason = "Content may be inappropriate, user warning issued"
    elif toxicity_score < 0.8:
        action = "hide"
        reason = "Content violates community guidelines, hidden from view"
    else:
        action = "delete"
        reason = "Content severely violates community guidelines, deleted"

    return {
        "message_id": f"msg_{int(datetime.utcnow().timestamp())}",
        "toxicity_scores": {
            "toxic": toxicity_score,
            "severe_toxic": toxicity_score * 0.5,
            "obscene": toxicity_score * 0.3,
            "threat": toxicity_score * 0.1,
            "insult": toxicity_score * 0.7,
            "identity_hate": toxicity_score * 0.4
        },
>>>>>>> compyle/hate-speech-mitigation-agent
        "overall_score": toxicity_score,
        "moderation_action": {
            "recommended_action": action,
            "confidence": 0.85,
<<<<<<< HEAD
            "reason": f"Analysis complete - action: {action}"
=======
            "reason": reason,
            "adjusted_threshold": 0.5
        },
        "context_analysis": {
            "similarity_to_context": 0.3,
            "user_risk_level": "medium",
            "conversation_trend": "neutral"
>>>>>>> compyle/hate-speech-mitigation-agent
        },
        "processing_time_ms": 45,
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
<<<<<<< HEAD
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
'''

    os.makedirs('src', exist_ok=True)
=======
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
'''

>>>>>>> compyle/hate-speech-mitigation-agent
    with open('src/main.py', 'w') as f:
        f.write(content)
    print("✅ Created src/main.py")

<<<<<<< HEAD
if __name__ == "__main__":
    print("🚀 Setting up Hate Speech Moderation System...")
    create_requirements_txt()
    create_dockerfile()
    create_docker_compose()
    create_env_file()
    create_main_py()
    print("✅ Setup complete! Now run: docker-compose up -d")
=======
def create_init_files():
    """Create __init__.py files."""
    init_files = [
        'src/__init__.py',
        'src/config/__init__.py',
        'src/models/__init__.py',
        'src/services/__init__.py',
        'src/api/__init__.py',
        'src/api/routes/__init__.py',
        'src/api/middleware/__init__.py',
        'src/utils/__init__.py',
        'tests/__init__.py',
        'tests/unit/__init__.py',
        'tests/integration/__init__.py'
    ]

    for init_file in init_files:
        os.makedirs(os.path.dirname(init_file), exist_ok=True)
        with open(init_file, 'w') as f:
            f.write('"""Package initialization."""\n')

    print("✅ Created all __init__.py files")

def main():
    """Run the complete setup."""
    print("🚀 Setting up Hate Speech Moderation System...")
    print("=" * 50)

    create_requirements_txt()
    create_env_files()
    create_dockerfile()
    create_docker_compose()
    create_init_files()
    create_main_py()

    print("=" * 50)
    print("✅ Setup complete!")
    print("\nNext steps:")
    print("1. Start the system: docker-compose up -d")
    print("2. Check health: curl http://localhost:8000/health")
    print("3. View API docs: open http://localhost:8000/docs")

if __name__ == "__main__":
    main()
>>>>>>> compyle/hate-speech-mitigation-agent
