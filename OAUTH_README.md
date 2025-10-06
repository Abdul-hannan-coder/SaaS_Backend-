# OAuth Services Documentation

This project provides OAuth implementations for Instagram and Facebook Pages APIs.

## 🚀 Quick Start

### Option 1: Start Both Services
```bash
python start_oauth_services.py
```

### Option 2: Start Services Individually

#### Instagram OAuth Service
```bash
uvicorn instagram:app --reload --port 8000
```

#### Facebook Pages OAuth Service
```bash
uvicorn facebook_pages:app --reload --port 8001
```

## 📋 Services Overview

### Instagram OAuth Service (Port 8000)
- **Base URL**: `http://127.0.0.1:8000`
- **Documentation**: `http://127.0.0.1:8000/docs`
- **Purpose**: Instagram Business API OAuth flow

### Facebook Pages OAuth Service (Port 8001)
- **Base URL**: `http://127.0.0.1:8001`
- **Documentation**: `http://127.0.0.1:8001/docs`
- **Purpose**: Facebook Pages API OAuth flow

## 🔧 Configuration

### Instagram OAuth
- **Client ID**: `25151268451125305`
- **Client Secret**: Set via environment variable `INSTAGRAM_CLIENT_SECRET`
- **Redirect URI**: `https://6e36fc3a9566.ngrok-free.app/callback`

### Facebook Pages OAuth
- **Client ID**: `1136209781299705`
- **Client Secret**: Set via environment variable `FACEBOOK_CLIENT_SECRET`
- **Redirect URI**: `https://6e36fc3a9566.ngrok-free.app/facebook_callback`

## 📡 API Endpoints

### Common Endpoints (Both Services)
- `GET /` - Root endpoint with service info
- `GET /config` - Current configuration
- `GET /tokens` - View stored tokens
- `GET /clear_tokens` - Clear all stored data
- `POST /update_redirect_uri` - Update redirect URI
- `POST /update_client_secret` - Update client secret
- `GET /debug_urls` - Debug information

### Instagram-Specific Endpoints
- `GET /generate_instagram_url` - Generate OAuth URL
- `GET /callback` - Handle OAuth callback

### Facebook Pages-Specific Endpoints
- `GET /generate_facebook_url` - Generate OAuth URL
- `GET /facebook_callback` - Handle OAuth callback
- `GET /pages/{code}` - Get pages for specific code

## 🧪 Testing

### Instagram OAuth Test
```bash
python test_instagram_oauth.py
```

### Facebook Pages OAuth Test
```bash
python test_facebook_pages_oauth.py
```

## 🔐 OAuth Flow

### 1. Generate OAuth URL
```bash
curl -X GET "http://127.0.0.1:8000/generate_instagram_url"
curl -X GET "http://127.0.0.1:8001/generate_facebook_url"
```

### 2. Complete OAuth in Browser
Open the returned URL in your browser and complete the authorization.

### 3. Check Tokens
```bash
curl -X GET "http://127.0.0.1:8000/tokens"
curl -X GET "http://127.0.0.1:8001/tokens"
```

## 🛠️ Environment Variables

Set these environment variables for production:

```bash
export INSTAGRAM_CLIENT_SECRET="your_instagram_client_secret"
export FACEBOOK_CLIENT_SECRET="your_facebook_client_secret"
```

## 📊 Features

### Instagram OAuth
- ✅ Instagram Business API OAuth flow
- ✅ Access token generation
- ✅ User ID and permissions
- ✅ Enhanced error handling and debugging
- ✅ Token management

### Facebook Pages OAuth
- ✅ Facebook Pages API OAuth flow
- ✅ Access token generation
- ✅ User ID and permissions
- ✅ Pages list retrieval
- ✅ Enhanced error handling and debugging
- ✅ Token and pages management

## 🔍 Debugging

### Check Configuration
```bash
curl -X GET "http://127.0.0.1:8000/config"
curl -X GET "http://127.0.0.1:8001/config"
```

### Update Client Secret
```bash
curl -X POST "http://127.0.0.1:8000/update_client_secret?new_secret=YOUR_SECRET"
curl -X POST "http://127.0.0.1:8001/update_client_secret?new_secret=YOUR_SECRET"
```

### Update Redirect URI
```bash
curl -X POST "http://127.0.0.1:8000/update_redirect_uri?new_uri=https://your-new-url.ngrok-free.app/callback"
curl -X POST "http://127.0.0.1:8001/update_redirect_uri?new_uri=https://your-new-url.ngrok-free.app/facebook_callback"
```

## 🚨 Troubleshooting

### Common Issues
1. **Wrong client secret** - Most common issue
2. **Redirect URI mismatch** - Must match exactly in app settings
3. **ngrok URL changes** - Update redirect URI when ngrok restarts
4. **Expired tokens** - OAuth codes expire quickly

### Solutions
1. Check app settings in Facebook Developer Console
2. Verify redirect URIs match exactly
3. Use the update endpoints to fix configuration
4. Clear tokens and start fresh if needed

## 📝 Notes

- OAuth codes are single-use and expire quickly
- Access tokens are stored in memory (not persistent)
- Both services use the same ngrok URL with different callback paths
- Enhanced logging helps debug OAuth issues
- All endpoints return JSON responses


