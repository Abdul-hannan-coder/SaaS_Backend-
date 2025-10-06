# SaaS YouTube Management Platform - Backend

A comprehensive FastAPI backend for the YouTube content management platform. This backend provides robust APIs for video management, AI-powered content optimization, user authentication, and YouTube integration.

## 🚀 Features

### Core Functionality
- **User Authentication**: JWT-based authentication with secure password hashing
- **YouTube Integration**: Complete YouTube API integration with OAuth 2.0
- **Video Management**: Upload, process, and manage video content
- **AI-Powered Tools**: Gemini AI integration for content generation
- **Database Management**: SQLModel with MySQL for reliable data storage
- **Background Tasks**: Asynchronous video processing and cleanup

### Key Capabilities
- Video upload and processing with multiple format support
- AI-generated titles, descriptions, and timestamps
- Thumbnail generation and management
- YouTube OAuth authentication and token management
- Playlist creation and management
- Comment management system
- Analytics and dashboard data
- Real-time video transcription

## 🏗️ Project Structure

```
app/
├── config/                       # Configuration files
│   ├── database.py              # Database configuration
│   └── my_settings.py           # Application settings
├── modules/                     # Feature modules
│   ├── google_login/            # Google OAuth authentication
│   │   ├── controllers/         # Authentication controllers
│   │   ├── models/              # User models
│   │   ├── routes/              # Auth routes
│   │   └── services/            # OAuth services
│   ├── login_logout/            # User management
│   │   ├── controllers/         # User controllers
│   │   ├── models/              # User models
│   │   ├── routes/              # User routes
│   │   └── services/            # User services
│   └── youtube/                 # YouTube functionality
│       ├── all_in_one/          # Combined operations
│       ├── comment/             # Comment management
│       ├── dashboard_overview/  # Dashboard analytics
│       ├── dashboard_playlist/  # Playlist dashboard
│       ├── dashboard_single_video/ # Video details
│       ├── discription_generator/ # AI description generation
│       ├── gemini/              # Gemini AI integration
│       ├── helpers/             # Utility functions
│       ├── playlist/            # Playlist management
│       ├── privacy_status/      # Video privacy settings
│       ├── schedule/            # Video scheduling
│       ├── thumbnail_generator/ # Thumbnail creation
│       ├── timestamps_generator/ # AI timestamp generation
│       ├── title_generator/     # AI title generation
│       ├── video/               # Video operations
│       ├── video_upload/        # Video upload handling
│       ├── youtube_creds/       # YouTube credentials
│       └── youtube_token/       # Token management
├── utils/                       # Utility functions
│   ├── database_dependency.py  # Database dependencies
│   └── my_logger.py            # Logging utilities
├── views/                       # HTML templates
│   ├── error.html              # Error pages
│   └── oauth_success.html      # OAuth success page
├── app.py                      # Main FastAPI application
└── youtube_routes.py           # YouTube route registration
```

## 🛠️ Technology Stack

### Backend Framework
- **FastAPI**: Modern, fast web framework for building APIs
- **Python 3.11+**: Latest Python with type hints
- **SQLModel**: SQL databases with Python objects
- **MySQL**: Reliable relational database
- **Uvicorn**: ASGI server for production

### Authentication & Security
- **JWT**: JSON Web Tokens for secure authentication
- **OAuth 2.0**: Google OAuth integration
- **Passlib**: Password hashing with bcrypt
- **CORS**: Cross-origin resource sharing

### AI & External Services
- **Google Gemini AI**: Advanced AI for content generation
- **YouTube Data API v3**: Complete YouTube integration
- **YouTube Transcript API**: Video transcription
- **FFmpeg**: Video processing and manipulation

### Development Tools
- **uv**: Fast Python package manager
- **Sentry**: Error tracking and monitoring
- **Jinja2**: Template engine for HTML responses
- **Python Multipart**: File upload handling

## 📦 Installation

### Prerequisites
- Python 3.11+
- MySQL database
- FFmpeg
- uv package manager

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/Abdul-hannan-coder/SaaS_Backend-.git
   cd SaaS_Backend-
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Environment Setup**
   Create a `.env` file in the root directory:
   ```env
   DATABASE_URL="mysql+pymysql://username:password@host:port/database"
   PORT=8000
   GEMINI_API_KEY="your_gemini_api_key"
   GOOGLE_CLIENT_ID="your_google_client_id"
   GOOGLE_CLIENT_SECRET="your_google_client_secret"
   GOOGLE_REDIRECT_URI="http://localhost:8000/auth/google/callback"
   ```

4. **Database Setup**
   ```bash
   # The application will automatically create tables on startup
   uv run python run.py
   ```

5. **Run the development server**
   ```bash
   uv run python run.py
   ```

6. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## 🔧 Configuration

### Database Configuration
The application uses MySQL with SQLModel. Configure your database connection in the `.env` file:

```env
DATABASE_URL="mysql+pymysql://username:password@host:port/database_name"
```

### YouTube API Setup
1. Create a project in Google Cloud Console
2. Enable YouTube Data API v3
3. Create OAuth 2.0 credentials
4. Add authorized redirect URIs
5. Configure consent screen

### Gemini AI Setup
1. Get API key from Google AI Studio
2. Add to environment variables
3. Configure AI model parameters

## 📚 API Documentation

### Authentication Endpoints
- `POST /auth/signup` - Register new user
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user profile
- `POST /auth/google/login` - Google OAuth login
- `GET /auth/google/callback` - OAuth callback

### YouTube Integration
- `POST /youtube/credentials` - Save YouTube credentials
- `GET /youtube/auth` - YouTube OAuth authorization
- `POST /youtube/token` - Exchange authorization code for tokens

### Video Management
- `POST /video/upload` - Upload video file
- `GET /video/my-videos` - Get user's videos
- `GET /video/{video_id}` - Get specific video details
- `PUT /video/{video_id}` - Update video metadata
- `DELETE /video/{video_id}` - Delete video

### AI Content Generation
- `POST /title-generator/{video_id}/generate` - Generate AI titles
- `POST /description-generator/{video_id}/generate` - Generate descriptions
- `POST /timestamps-generator/{video_id}/generate` - Generate timestamps
- `POST /thumbnail-generator/{video_id}/generate` - Generate thumbnails

### Playlist Management
- `GET /playlist/my-playlists` - Get user's playlists
- `POST /playlist/create` - Create new playlist
- `PUT /playlist/{playlist_id}` - Update playlist
- `DELETE /playlist/{playlist_id}` - Delete playlist

### Dashboard Analytics
- `GET /dashboard/overview` - Get dashboard overview data
- `GET /dashboard/analytics` - Get detailed analytics
- `GET /dashboard/videos` - Get video performance data

## 🎯 Usage Examples

### Upload and Process Video
```python
import requests

# Upload video
files = {'file': open('video.mp4', 'rb')}
response = requests.post('http://localhost:8000/video/upload', files=files)
video_id = response.json()['video_id']

# Generate AI title
response = requests.post(f'http://localhost:8000/title-generator/{video_id}/generate')
titles = response.json()['titles']
```

### YouTube Integration
```python
# Authenticate with YouTube
response = requests.get('http://localhost:8000/youtube/auth')
auth_url = response.json()['auth_url']

# After user authorization, exchange code for tokens
data = {'code': 'authorization_code'}
response = requests.post('http://localhost:8000/youtube/token', json=data)
```

## 🔒 Security Features

- JWT-based authentication with secure token handling
- Password hashing using bcrypt
- OAuth 2.0 integration with Google
- CORS configuration for cross-origin requests
- Input validation and sanitization
- Error handling and logging
- File upload validation and cleanup

## 🚀 Deployment

### Production Setup
1. **Environment Variables**
   ```bash
   export DATABASE_URL="your_production_database_url"
   export GEMINI_API_KEY="your_production_gemini_key"
   export GOOGLE_CLIENT_ID="your_production_client_id"
   export GOOGLE_CLIENT_SECRET="your_production_client_secret"
   ```

2. **Database Migration**
   ```bash
   # Tables are created automatically on startup
   uv run python run.py
   ```

3. **Production Server**
   ```bash
   uv run uvicorn app.app:app --host 0.0.0.0 --port 8000 --workers 4
   ```

### Docker Deployment
```bash
# Build image
docker build -t saas-youtube-backend .

# Run container
docker run -p 8000:8000 --env-file .env saas-youtube-backend
```

### Docker Compose
```bash
docker-compose up -d
```

## 🧪 Testing

### Run Tests
```bash
# Run specific test files
uv run python test_title_generator.py
uv run python test_transcript_api.py
uv run python test_playlist_details_api.py
```

### API Testing
Use the interactive API documentation at `/docs` to test endpoints directly.

## 📊 Monitoring

### Logging
- Application logs are stored in the `logs/` directory
- Structured logging with different log levels
- Error tracking with Sentry integration

### Health Checks
- `/health` endpoint for application health monitoring
- Database connection validation
- External service availability checks

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🔗 Links

- **Frontend Repository**: [SaaS_Frontend_final](https://github.com/Abdul-hannan-coder/SaaS_Frontend_final)
- **API Documentation**: Available at `/docs` when running
- **Live Demo**: [Coming Soon]

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the logs in the `logs/` directory

## 🙏 Acknowledgments

- FastAPI team for the excellent framework
- Google for YouTube API and Gemini AI
- SQLModel for the database ORM
- The open-source community

---

**Built with ❤️ by Abdul Hannan**
