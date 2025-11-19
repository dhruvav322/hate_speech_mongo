# 🛡️ Hate Speech Moderation Dashboard

A production-ready, real-time dashboard for hate speech moderation with a **Threat Intelligence / SOC Terminal** aesthetic. Built with Next.js 16, Tailwind CSS, and a FastAPI backend.

## ✨ Features

### 🎯 Core Functionality
- **Real-time Text Analysis**: Analyze text for hate speech and toxicity using ML ensemble models
- **Live Dashboard**: Auto-updating dashboard with real-time statistics and moderation events
- **Analytics & Insights**: Comprehensive analytics with interactive charts and metrics
- **MLOps Feedback Loop**: Submit feedback to improve model accuracy
- **Adaptive Moderation**: Context-aware scoring with user behavior learning

### 🎨 UI/UX Highlights
- **Terminal Aesthetic**: Cyber-themed UI with neon green/red color scheme
- **Fully Responsive**: Optimized for mobile, tablet, and desktop
- **Real-time Updates**: Auto-refreshes every 5 seconds
- **Skeleton Loaders**: Smooth loading states with "AI is Thinking" effects
- **Toxic Word Highlighting**: Visual explainability for moderation decisions
- **Scrollable Tables**: Adaptive height based on content

### 🚀 Performance & Scalability
- **Redis Caching**: Fast response times with intelligent caching
- **Message Queues**: Persistent background task processing
- **Database Optimization**: Connection pooling and optimized indexes
- **Load Balancing Ready**: Docker Compose setup for horizontal scaling
- **Connection Pooling**: MongoDB with 100 max connections

## 🏗️ Tech Stack

### Frontend
- **Next.js 16** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS v4** - Utility-first styling
- **Shadcn/ui** - Reusable UI components
- **Recharts** - Data visualization
- **Sonner** - Toast notifications
- **Framer Motion** - Animations
- **JetBrains Mono** - Terminal-style monospace font

### Backend
- **FastAPI** - High-performance Python web framework
- **MongoDB** - NoSQL database with optimized indexes
- **Redis** - Caching and message queues
- **Detoxify** - ML models for toxicity detection
- **Sentence Transformers** - Embedding generation
- **Motor** - Async MongoDB driver

## 📦 Installation

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- MongoDB (or Docker)
- Redis (optional, for caching/queues)

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend-next

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local

# Edit .env.local with your settings
# NEXT_PUBLIC_API_URL=http://localhost:8001
# NEXT_PUBLIC_API_KEY=your-api-key

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Backend Setup

See the main project README for backend setup instructions.

## 🔧 Configuration

### Environment Variables

Create a `.env.local` file in the `frontend-next` directory:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_API_KEY=your-api-key-here

# Optional: Custom API endpoint
# NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

### API Endpoints

The frontend communicates with these backend endpoints:

- `POST /api/v1/moderation/analyze` - Analyze text for toxicity
- `GET /api/v1/analytics/overview` - Get dashboard statistics
- `GET /api/v1/moderation/statistics` - Get recent moderation events
- `POST /api/v1/feedback/report` - Submit feedback

## 📱 Pages

### Dashboard (`/`)
- **Real-time Statistics**: Total messages, flagged content, feedback count, uptime
- **Recent Events Table**: Live moderation events with adaptive scrolling
- **Model Confidence**: Distribution visualization
- **Auto-refresh**: Updates every 5 seconds

### Analyze (`/analyze`)
- **Text Input**: Terminal-style input with preset samples
- **Real-time Analysis**: Instant toxicity scoring
- **Ensemble Breakdown**: Individual model scores
- **Toxic Word Highlighting**: Visual explainability
- **Report Error**: Quick link to feedback page

### Analytics (`/analytics`)
- **Time Series Charts**: Message volume and flagged content trends
- **Action Distribution**: Visual breakdown of moderation actions
- **Performance Metrics**: Model accuracy, precision, recall

### Feedback (`/feedback`)
- **Auto-filled Message ID**: From analyze page via URL params
- **Verdict Accuracy**: Correct/Incorrect selection
- **Correction Notes**: Optional feedback text
- **MLOps Integration**: Direct backend submission

## 🎨 UI Components

### TerminalCard
The core UI building block with:
- Status indicators (idle, active, danger, success)
- Cyber-themed borders and colors
- Responsive padding and sizing
- Decorative corner brackets

### Color Palette
- **Background**: `#050505` (almost black)
- **Cyber Green**: `#00ff9d` (primary actions, success)
- **Cyber Red**: `#ff0055` (danger, blocked content)
- **Cyber Blue**: `#00e1ff` (info, accents)
- **Zinc Gray**: `#71717a` (secondary text)

## 🔄 Real-time Features

### Auto-refresh
- Dashboard updates every 5 seconds
- Live status indicator with pulsing dot
- Last update timestamp
- No manual refresh needed

### Live Data
- Statistics from `/api/v1/analytics/overview`
- Recent events from `/api/v1/moderation/statistics`
- Real-time moderation results
- Background task processing

## 📊 Responsive Design

### Breakpoints
- **Mobile**: `< 640px` - Compact layout, hidden navigation
- **Tablet**: `640px - 1024px` - 2-column grids, visible navigation
- **Desktop**: `> 1024px` - Full layout, all features visible

### Adaptive Components
- **Text Sizes**: Responsive from `text-sm` to `text-3xl`
- **Button Heights**: `h-12` (mobile) to `h-16` (desktop)
- **Card Padding**: `p-4` (mobile) to `p-6` (desktop)
- **Table Heights**: Adaptive based on content (1-5 rows grow, 6+ scroll)

## 🚀 Production Deployment

### Build for Production

```bash
# Build the application
npm run build

# Start production server
npm start
```

### Docker Deployment

See the main project's `docker-compose.scalable.yml` for production deployment with:
- Load balancing (Nginx)
- Multiple API instances
- Redis caching
- MongoDB with connection pooling

## 🔒 Security

- **API Key Authentication**: All requests require valid API key
- **CORS Configuration**: Restricted to allowed origins
- **Input Sanitization**: All user inputs are sanitized
- **Rate Limiting**: Backend enforces rate limits
- **Secure Headers**: Security headers middleware

## 📈 Performance

### Optimizations
- **Client-side Rendering**: Fast initial load
- **Code Splitting**: Automatic route-based splitting
- **Image Optimization**: Next.js Image component
- **Caching**: Redis for API responses
- **Connection Pooling**: Optimized database connections

### Metrics
- **Initial Load**: < 2s
- **API Response**: < 200ms (with caching)
- **Real-time Updates**: 5-second intervals
- **Cache Hit Rate**: 40-60% (with Redis)

## 🐛 Troubleshooting

### Common Issues

**Hydration Errors**
- Fixed: Time display only renders client-side
- Shows "Connecting..." during SSR

**CORS Errors**
- Ensure backend allows `http://localhost:3000`
- Check `NEXT_PUBLIC_API_URL` in `.env.local`

**API Connection Failed**
- Verify backend is running on port 8001
- Check API key in `.env.local`
- Review browser console for errors

**Table Not Scrolling**
- Table height adapts to content
- Scrolls automatically when > 5 rows
- Check browser console for layout issues

## 🧪 Development

### Available Scripts

```bash
# Development server
npm run dev

# Production build
npm run build

# Start production server
npm start

# Lint code
npm run lint

# Type checking
npm run type-check
```

### Project Structure

```
frontend-next/
├── src/
│   ├── app/
│   │   ├── (dashboard)/
│   │   │   ├── page.tsx          # Dashboard home
│   │   │   ├── analyze/
│   │   │   │   └── page.tsx      # Text analysis
│   │   │   ├── analytics/
│   │   │   │   └── page.tsx      # Analytics charts
│   │   │   └── feedback/
│   │   │       └── page.tsx      # Feedback form
│   │   ├── layout.tsx            # Root layout
│   │   └── globals.css           # Global styles
│   ├── components/
│   │   └── ui/
│   │       └── terminal-card.tsx # Core UI component
│   └── lib/
│       └── api.ts                # API client
├── .env.local                    # Environment variables
└── package.json
```

## 📝 Features Implemented

### ✅ Completed
- [x] Real-time dashboard with auto-refresh
- [x] Text analysis with ML ensemble
- [x] Toxic word highlighting
- [x] Analytics with interactive charts
- [x] Feedback submission with auto-fill
- [x] Responsive design (mobile/tablet/desktop)
- [x] Terminal aesthetic UI
- [x] Skeleton loaders
- [x] Error handling and toast notifications
- [x] Adaptive table heights
- [x] Hydration error fixes
- [x] Scrollable tables
- [x] Real-time statistics

### 🔄 Backend Integration
- [x] API client with error handling
- [x] Environment variable configuration
- [x] CORS support
- [x] Rate limiting support
- [x] Authentication headers

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

See the main project LICENSE file.

## 🙏 Acknowledgments

- **Detoxify** - ML models for toxicity detection
- **Next.js Team** - Amazing React framework
- **Tailwind CSS** - Utility-first CSS framework
- **Shadcn** - Beautiful UI components

---

**Built with ❤️ for safer online communities**
