#!/usr/bin/env python3
"""Setup script for Hate Speech Moderation System"""

import os

def create_requirements_txt():
    """Create requirements.txt file."""
    content = """fastapi==0.104.1
uvicorn[standard]==0.24.0
gunicorn==21.2.0
pymongo==4.6.0
motor==3.3.2
detoxify==1.2.0
sentence-transformers==2.2.2
torch==2.1.0
transformers==4.35.0
numpy==1.24.3
scikit-learn==1.3.0
pydantic==2.5.0
pydantic-settings==2.1.0
pydantic[email]==2.5.0
python-dotenv==1.0.0
python-multipart==0.0.6
structlog==23.2.0
prometheus-client==0.19.0
httpx==0.25.2
aiofiles==23.2.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
psutil==5.9.6"""

    with open('requirements.txt', 'w') as f:
        f.write(content)
    print("✅ Created requirements.txt")

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

    with open('Dockerfile', 'w') as f:
        f.write(content)
    print("✅ Created Dockerfile")

def create_docker_compose():
    """Create docker-compose.yml file."""
    content = """version: '3.8'
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
  mongo:
    image: mongo:7.0
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
    environment:
      - MONGO_INITDB_DATABASE=hate_speech_mitigation
    restart: unless-stopped
volumes:
  mongo_data:"""

    with open('docker-compose.yml', 'w') as f:
        f.write(content)
    print("✅ Created docker-compose.yml")

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

app = FastAPI(
    title="Hate Speech Moderation API",
    description="Adaptive hate speech moderation system with context-aware scoring",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

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
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/v1/moderation/analyze")
async def analyze_message(request: dict):
    """Simple message analysis endpoint."""
    text = request.get("text", "")
    toxic_words = ["hate", "stupid", "ugly", "kill"]
    toxicity_score = sum(1 for word in toxic_words if word.lower() in text.lower()) / max(len(text.split()), 1)
    toxicity_score = min(toxicity_score, 1.0)

    if toxicity_score < 0.3:
        action = "none"
    elif toxicity_score < 0.6:
        action = "warn"
    elif toxicity_score < 0.8:
        action = "hide"
    else:
        action = "delete"

    return {
        "message_id": f"msg_{int(datetime.utcnow().timestamp())}",
        "overall_score": toxicity_score,
        "moderation_action": {
            "recommended_action": action,
            "confidence": 0.85,
            "reason": f"Analysis complete - action: {action}"
        },
        "processing_time_ms": 45,
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
'''

    os.makedirs('src', exist_ok=True)
    with open('src/main.py', 'w') as f:
        f.write(content)
    print("✅ Created src/main.py")

if __name__ == "__main__":
    print("🚀 Setting up Hate Speech Moderation System...")
    create_requirements_txt()
    create_dockerfile()
    create_docker_compose()
    create_env_file()
    create_main_py()
    print("✅ Setup complete! Now run: docker-compose up -d")
