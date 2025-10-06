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
│   ├── login_logout/            # User management
│   └── youtube/                 # YouTube functionality (20 modules)
├── utils/                       # Utility functions
├── views/                       # HTML templates
├── app.py                      # Main FastAPI application
└── youtube_routes.py           # YouTube route registration
```

## 📁 Modules Architecture

The application follows a modular architecture with three main module categories:

### 🔐 Authentication Modules

#### `google_login/`
- **Purpose**: Google OAuth 2.0 authentication integration
- **Structure**: MVC pattern with controllers, models, routes, services
- **Key Files**:
  - `controllers/google_auth_controller.py` - OAuth flow management
  - `models/google_user_model.py` - Google user data models
  - `routes/google_auth_routes.py` - OAuth endpoints
  - `services/google_oauth_service.py` - OAuth service logic

#### `login_logout/`
- **Purpose**: Traditional user authentication and management
- **Structure**: Complete user management system
- **Key Files**:
  - `controllers/user_controller.py` - User operations
  - `models/user_model.py` - User database models
  - `models/error_models.py` - Error handling models
  - `routes/user_routes.py` - User endpoints
  - `services/user_service.py` - User business logic
  - `services/auth_service.py` - Authentication services

### 🎥 YouTube Module Ecosystem

The YouTube module contains 20 specialized sub-modules, each following a consistent MVC architecture:

#### Core Video Management

##### `video/`
- **Purpose**: Core video operations and metadata management
- **Use Cases**: 
  - Video CRUD operations
  - Metadata updates
  - Video status management
- **Key Features**: Video model, service layer, error handling
- **API Endpoints**: `/video/*`

##### `video_upload/`
- **Purpose**: Handle video file uploads and processing
- **Use Cases**:
  - File upload validation
  - Video format conversion
  - Upload progress tracking
- **Key Features**: Multipart file handling, background processing
- **API Endpoints**: `/video-upload/*`

#### AI-Powered Content Generation

##### `title_generator/`
- **Purpose**: AI-powered YouTube title generation
- **Use Cases**:
  - Generate engaging titles using AI
  - SEO-optimized title suggestions
  - Multiple title variations
- **Key Features**: Gemini AI integration, context analysis
- **API Endpoints**: `/title-generator/*`

##### `discription_generator/`
- **Purpose**: AI-powered video description generation
- **Use Cases**:
  - Generate comprehensive descriptions
  - SEO optimization
  - Hashtag suggestions
- **Key Features**: Content analysis, keyword extraction
- **API Endpoints**: `/description-generator/*`

##### `timestamps_generator/`
- **Purpose**: Automatic timestamp generation from video content
- **Use Cases**:
  - Extract key moments
  - Chapter generation
  - Content segmentation
- **Key Features**: Video analysis, AI-powered segmentation
- **API Endpoints**: `/timestamps-generator/*`

##### `thumbnail_generator/`
- **Purpose**: AI-powered thumbnail creation and optimization
- **Use Cases**:
  - Generate custom thumbnails
  - A/B testing thumbnails
  - Brand-consistent designs
- **Key Features**: Image generation, template system
- **API Endpoints**: `/thumbnail-generator/*`

#### Dashboard and Analytics

##### `dashboard_overview/`
- **Purpose**: Comprehensive dashboard analytics and insights
- **Use Cases**:
  - Channel performance metrics
  - Growth analytics
  - Revenue insights
- **Key Features**: Real-time data, visualization support
- **API Endpoints**: `/dashboard/overview/*`

##### `dashboard_playlist/`
- **Purpose**: Playlist-specific dashboard and analytics
- **Use Cases**:
  - Playlist performance tracking
  - Video organization insights
  - Engagement metrics
- **Key Features**: Playlist analytics, optimization suggestions
- **API Endpoints**: `/dashboard/playlist/*`

##### `dashboard_single_video/`
- **Purpose**: Individual video detailed analytics
- **Use Cases**:
  - Video performance deep-dive
  - Engagement analysis
  - Optimization recommendations
- **Key Features**: Detailed metrics, trend analysis
- **API Endpoints**: `/dashboard/video/*`

#### Content Management

##### `playlist/`
- **Purpose**: YouTube playlist management
- **Use Cases**:
  - Create and manage playlists
  - Video organization
  - Playlist optimization
- **Key Features**: CRUD operations, bulk management
- **API Endpoints**: `/playlist/*`

##### `comment/`
- **Purpose**: YouTube comment management and moderation
- **Use Cases**:
  - Comment retrieval and caching
  - Comment moderation
  - Reply management
  - Bulk operations
- **Key Features**: Caching system, moderation tools
- **API Endpoints**: `/comments/*`

##### `privacy_status/`
- **Purpose**: Video privacy and visibility management
- **Use Cases**:
  - Set video privacy levels
  - Scheduled publishing
  - Visibility controls
- **Key Features**: Privacy management, scheduling
- **API Endpoints**: `/privacy-status/*`

##### `schedule/`
- **Purpose**: Video scheduling and publishing automation
- **Use Cases**:
  - Schedule video releases
  - Automated publishing
  - Content calendar management
- **Key Features**: Cron-like scheduling, automation
- **API Endpoints**: `/schedule/*`

#### Integration and Utilities

##### `youtube_creds/`
- **Purpose**: YouTube API credentials management
- **Use Cases**:
  - Store and manage API credentials
  - Credential validation
  - Multi-account support
- **Key Features**: Secure storage, validation
- **API Endpoints**: `/youtube-creds/*`

##### `youtube_token/`
- **Purpose**: YouTube OAuth token management
- **Use Cases**:
  - Token refresh and validation
  - Session management
  - Multi-user token handling
- **Key Features**: Automatic refresh, secure storage
- **API Endpoints**: `/youtube-token/*`

##### `gemini/`
- **Purpose**: Google Gemini AI integration
- **Use Cases**:
  - AI model interactions
  - Content analysis
  - Smart suggestions
- **Key Features**: AI model management, prompt optimization
- **API Endpoints**: `/gemini/*`

##### `all_in_one/`
- **Purpose**: Comprehensive video processing in single request
- **Use Cases**:
  - Generate all content types at once
  - Batch processing
  - Streamlined workflow
- **Key Features**: Parallel processing, comprehensive results
- **API Endpoints**: `/all-in-one/*`

##### `helpers/`
- **Purpose**: Shared utility functions and services
- **Key Files**:
  - `auth_utils.py` - Authentication utilities
  - `error_handlers.py` - Global error handling
  - `ffmpeg_finder.py` - Video processing utilities
  - `thumbnail_generation.py` - Image processing
  - `transcript_dependency.py` - Video transcription
  - `video_cleanup_utility.py` - File management
  - `video_transcript_generator.py` - Transcript generation
  - `youtube_client.py` - YouTube API client
  - `download_image_from_url.py` - Image utilities
  - `image_upload.py` - Image handling

## 🔄 Module Architecture Pattern

Each YouTube module follows a consistent MVC architecture:

```
module_name/
├── controller.py      # Business logic controller
├── model.py          # Data models and schemas
├── route.py          # FastAPI route definitions
├── service.py        # Core business logic
├── error_models.py   # Error handling models
└── README.md         # Module documentation
```

### Key Benefits:
- **Modularity**: Each feature is self-contained
- **Scalability**: Easy to add new modules
- **Maintainability**: Clear separation of concerns
- **Testability**: Individual module testing
- **Consistency**: Uniform architecture across modules

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

### Comment Management
- `GET /comments/{video_id}` - Get video comments
- `POST /comments/{comment_id}/reply` - Reply to comment
- `DELETE /comments/{comment_id}` - Delete comment
- `POST /comments/bulk-reply` - Reply to multiple comments

### All-in-One Processing
- `POST /all-in-one/{video_id}/process` - Generate all content types

### Privacy & Scheduling
- `PUT /privacy-status/{video_id}` - Update video privacy
- `POST /schedule/{video_id}` - Schedule video publication
- `GET /schedule/my-scheduled` - Get scheduled videos

### Gemini AI Integration
- `POST /gemini/analyze` - Analyze content with AI
- `POST /gemini/generate` - Generate content with AI
- `GET /gemini/models` - Get available AI models

## 🎯 Module Use Cases & Workflows

### 📹 Content Creation Workflow

1. **Video Upload** (`video_upload/`)
   - User uploads video file
   - System validates format and size
   - Background processing begins
   - Video metadata extracted

2. **AI Content Generation** (Multiple modules)
   - `title_generator/` - Creates engaging titles
   - `discription_generator/` - Generates SEO descriptions
   - `timestamps_generator/` - Extracts key moments
   - `thumbnail_generator/` - Creates custom thumbnails

3. **Content Optimization** (`all_in_one/`)
   - Single API call for all AI features
   - Parallel processing for efficiency
   - Comprehensive content package

### 📊 Analytics & Dashboard Workflow

1. **Overview Dashboard** (`dashboard_overview/`)
   - Channel performance metrics
   - Growth trends and insights
   - Revenue analytics

2. **Video Analytics** (`dashboard_single_video/`)
   - Individual video performance
   - Engagement metrics
   - Optimization suggestions

3. **Playlist Analytics** (`dashboard_playlist/`)
   - Playlist performance tracking
   - Video organization insights

### 🎛️ Content Management Workflow

1. **Playlist Management** (`playlist/`)
   - Create and organize playlists
   - Bulk video operations
   - Playlist optimization

2. **Comment Management** (`comment/`)
   - Retrieve and cache comments
   - Moderate discussions
   - Bulk reply operations

3. **Privacy & Scheduling** (`privacy_status/`, `schedule/`)
   - Set video visibility
   - Schedule publications
   - Automated content calendar

### 🔧 Technical Integration Workflow

1. **Authentication** (`youtube_creds/`, `youtube_token/`)
   - Secure credential storage
   - Token refresh automation
   - Multi-account support

2. **AI Integration** (`gemini/`)
   - Smart content analysis
   - Context-aware suggestions
   - Model optimization

### 💡 Key Module Interactions

```
User Request → Authentication → YouTube API → AI Processing → Database → Response

Example Flow:
1. User uploads video (video_upload/)
2. System authenticates (youtube_token/)
3. AI analyzes content (gemini/)
4. Generates titles/descriptions (title_generator/, description_generator/)
5. Creates thumbnails (thumbnail_generator/)
6. Stores results (database)
7. Returns comprehensive response (all_in_one/)
```

### 🚀 Advanced Use Cases

#### Bulk Content Processing
- Process multiple videos simultaneously
- Batch AI generation for efficiency
- Automated content optimization

#### Multi-Channel Management
- Handle multiple YouTube channels
- Channel-specific analytics
- Cross-channel insights

#### Content Strategy Optimization
- AI-powered content suggestions
- Performance-based recommendations
- Trend analysis and adaptation

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
