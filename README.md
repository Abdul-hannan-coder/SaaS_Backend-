# VideoTitle AI - AI-Powered Video Title Generator

A complete SaaS application that uses AI to generate compelling, SEO-optimized titles for videos. Upload your videos and let our advanced AI analyze the content to create titles that boost engagement and drive more views.

## 🚀 Features

### Backend (FastAPI)

- **User Authentication** - JWT-based authentication with secure password hashing
- **Video Upload & Processing** - Support for multiple video formats with automatic cleanup
- **AI Title Generation** - Advanced AI models that analyze video content and transcripts
- **Database Management** - SQLModel with PostgreSQL for reliable data storage
- **Background Tasks** - Asynchronous video processing and cleanup
- **RESTful API** - Clean, well-documented API endpoints

### Frontend (Next.js)

- **Beautiful Landing Page** - Modern, responsive design with gradient backgrounds
- **User Dashboard** - Intuitive interface for video management
- **Real-time Upload** - Drag & drop file upload with progress tracking
- **Title Management** - Generate, save, and copy AI-generated titles
- **Responsive Design** - Works perfectly on all devices
- **Form Validation** - Client-side validation with error handling

## 🛠 Tech Stack

### Backend

- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Database**: PostgreSQL with SQLModel
- **Authentication**: JWT with Passlib
- **File Processing**: FFmpeg, Whisper
- **AI/ML**: OpenAI GPT models
- **Task Queue**: Background tasks with FastAPI
- **Package Manager**: uv

### Frontend

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Forms**: React Hook Form with Zod validation
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Package Manager**: npm

## 📦 Installation

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL
- FFmpeg
- uv (Python package manager)

### Quick Start

1. **Clone the repository**

```bash
git clone <repository-url>
cd saas-project-backend
```

2. **Install dependencies**

```bash
# Install Python dependencies
uv sync

# Install Node.js dependencies
npm run install:all
```

3. **Set up environment variables**

```bash
# Backend
cp app/config/my_settings.py.example app/config/my_settings.py
# Edit the settings file with your database and API keys

# Frontend
cd frontend
cp .env.example .env.local
# Set NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. **Set up the database**

```bash
# Create database tables
uv run python -c "from app.config.database import create_tables; create_tables()"
```

5. **Start the application**

```bash
# Start both backend and frontend
npm run dev
```

The application will be available at:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 🏗 Project Structure

```
saas-project-backend/
├── app/                          # Backend application
│   ├── config/                   # Configuration files
│   ├── controllers/              # Business logic
│   ├── models/                   # Database models
│   ├── routes/                   # API routes
│   ├── services/                 # External services
│   └── utils/                    # Utility functions
├── frontend/                     # Next.js frontend
│   ├── src/
│   │   ├── app/                  # Next.js app router
│   │   ├── lib/                  # Utilities and API client
│   │   └── middleware.ts         # Authentication middleware
│   └── package.json
├── videos/                       # Video storage
├── logs/                         # Application logs
├── pyproject.toml               # Python dependencies
├── package.json                 # Node.js dependencies
└── README.md
```

## 🔧 Configuration

### Backend Configuration (`app/config/my_settings.py`)

```python
# Database
DATABASE_URL = "postgresql://user:password@localhost/videotitle_db"

# JWT Settings
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OpenAI API
OPENAI_API_KEY = "your-openai-api-key"

# File Storage
VIDEO_STORAGE_PATH = "./videos"
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
```

### Frontend Configuration (`.env.local`)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📚 API Documentation

### Authentication Endpoints

- `POST /auth/signup` - Register new user
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user

### Video Endpoints

- `POST /videos/upload` - Upload video file
- `POST /videos/download` - Download video from URL
- `GET /videos/my-videos` - Get user's videos
- `GET /videos/{id}` - Get specific video

### Title Generation Endpoints

- `POST /title-generator/{id}/generate` - Generate AI titles
- `POST /title-generator/{id}/save` - Save generated title
- `POST /title-generator/{id}/regenerate-with-requirements` - Regenerate with requirements

## 🎯 Usage

### For Users

1. **Sign up** for an account
2. **Upload videos** via file upload or URL
3. **Generate titles** using AI analysis
4. **Save and copy** the best titles
5. **Manage** your video library

### For Developers

1. **Backend Development**

   ```bash
   uv run python run.py
   ```

2. **Frontend Development**

   ```bash
   cd frontend
   npm run dev
   ```

3. **Database Migrations**
   ```bash
   uv run python fix_scope_column.py
   ```

## 🔒 Security Features

- JWT-based authentication
- Password hashing with bcrypt
- CORS configuration
- File upload validation
- Rate limiting (can be added)
- Input sanitization

## 🚀 Deployment

### Backend Deployment

1. Set up PostgreSQL database
2. Configure environment variables
3. Install dependencies with `uv sync`
4. Run with production ASGI server (uvicorn/gunicorn)

### Frontend Deployment

1. Build the application: `npm run build`
2. Deploy to Vercel, Netlify, or any static hosting
3. Configure environment variables

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:

- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the logs in the `logs/` directory

## 🔮 Roadmap

- [ ] User subscription plans
- [ ] Advanced analytics
- [ ] Bulk video processing
- [ ] Custom AI models
- [ ] Mobile app
- [ ] API rate limiting
- [ ] Video thumbnail generation
- [ ] Social media integration
