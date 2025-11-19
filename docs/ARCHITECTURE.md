# 🏗️ System Architecture

## Overview

The Hate Speech Moderation System is a full-stack application with a Next.js frontend and FastAPI backend, designed for scalability and production use.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Dashboard │  │ Analyze  │  │Analytics │  │ Feedback │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    Nginx (Load Balancer)                     │
│              (Production - Optional)                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
┌────────▼──┐  ┌───────▼────┐  ┌────▼──────┐
│ API Inst 1│  │ API Inst 2 │  │ API Inst N│
│ (FastAPI) │  │ (FastAPI)  │  │ (FastAPI) │
└─────┬─────┘  └──────┬─────┘  └─────┬─────┘
      │               │              │
      └───────────────┼──────────────┘
                     │
      ┌──────────────┼──────────────┐
      │              │              │
┌─────▼─────┐  ┌─────▼─────┐  ┌───▼────┐
│  MongoDB  │  │   Redis   │  │  ML     │
│ (Primary) │  │ (Cache/Q) │  │ Models  │
└───────────┘  └───────────┘  └─────────┘
```

## Component Details

### Frontend (Next.js)
- **Framework**: Next.js 16 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **State Management**: React Hooks
- **Real-time Updates**: Polling (5-second intervals)

### Backend (FastAPI)
- **Framework**: FastAPI (Python 3.11+)
- **API Style**: RESTful
- **Authentication**: API Key (X-API-Key header)
- **Rate Limiting**: SlowAPI with Redis support
- **CORS**: Configurable origins

### Database
- **Primary**: MongoDB (Motor async driver)
- **Connection Pooling**: 100 max connections
- **Indexes**: Optimized compound indexes

### Caching & Queues
- **Redis**: Optional caching and message queues
- **Fallback**: In-memory if Redis unavailable
- **TTL**: Configurable per cache type

### ML Models
- **Detoxify**: Multiple models (original, multilingual, unbiased)
- **Sentence Transformers**: Embedding generation
- **Ensemble**: Weighted voting system

## Data Flow

1. **Text Analysis Request**
   ```
   Frontend → API → Cache Check → ML Models → Response → Cache Store
   ```

2. **Background Processing**
   ```
   API → Queue → Worker → MongoDB
   ```

3. **Real-time Dashboard**
   ```
   Frontend → Poll API → Display Stats
   ```

## Scalability

- **Horizontal Scaling**: Multiple API instances behind Nginx
- **Database**: Connection pooling and read replicas (optional)
- **Caching**: Redis for frequently accessed data
- **Background Jobs**: Queue-based processing

## Security

- **API Key Authentication**: Required for all endpoints
- **CORS**: Restricted origins
- **Input Sanitization**: All user inputs validated
- **Rate Limiting**: Per API key
- **Security Headers**: HSTS, CSP, etc.
