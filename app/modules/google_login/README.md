# 🔐 Google OAuth Module

A complete Google OAuth 2.0 authentication implementation using a functional approach for FastAPI applications.

## 📋 Table of Contents

- [Overview](#overview)
- [Backend Setup](#backend-setup)
- [API Endpoints](#api-endpoints)
- [Frontend Integration](#frontend-integration)
- [Examples](#examples)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This module provides "Continue with Google" functionality for your application. It handles:

- ✅ Google OAuth 2.0 flow
- ✅ User creation/login
- ✅ JWT token generation
- ✅ Automatic username generation
- ✅ Profile picture handling
- ✅ Functional programming approach

## 🛠 Backend Setup

### 1. Environment Variables

Add these to your `.env` file:

```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id-from-console
GOOGLE_CLIENT_SECRET=your-google-client-secret-from-console
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
```

### 2. Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing one
3. Go to **APIs & Services** → **Credentials**
4. Click **Create Credentials** → **OAuth 2.0 Client ID**
5. Choose **Web application**
6. Add authorized redirect URIs:
   - `http://localhost:8000/auth/google/callback` (development)
   - `https://yourdomain.com/auth/google/callback` (production)

### 3. Dependencies

Required packages (already included in `pyproject.toml`):

```toml
"authlib>=1.3.0"
"httpx>=0.25.0"
```

## 🚀 API Endpoints

### Authentication Endpoints

| Method | Endpoint                | Description                  |
| ------ | ----------------------- | ---------------------------- |
| `GET`  | `/auth/google/login`    | Initiate Google OAuth flow   |
| `GET`  | `/auth/google/callback` | Handle Google OAuth callback |
| `GET`  | `/auth/google/status`   | Check OAuth configuration    |

### Usage Flow

1. **Start OAuth**: Redirect user to `/auth/google/login`
2. **Google handles auth**: User signs in with Google
3. **Callback processed**: Google redirects to `/auth/google/callback`
4. **Token returned**: User gets JWT token for API access

## 🌐 Frontend Integration

### Method 1: Simple HTML/JavaScript

```html
<!DOCTYPE html>
<html>
  <head>
    <title>Login with Google</title>
    <style>
      .google-btn {
        background-color: #4285f4;
        color: white;
        padding: 12px 24px;
        border: none;
        border-radius: 4px;
        font-size: 16px;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 10px;
      }
      .google-btn:hover {
        background-color: #3367d6;
      }
    </style>
  </head>
  <body>
    <div class="login-container">
      <h2>Welcome! Please sign in</h2>

      <!-- Google OAuth Button -->
      <button class="google-btn" onclick="signInWithGoogle()">
        🚀 Continue with Google
      </button>
    </div>

    <script>
      function signInWithGoogle() {
          // Redirect to your backend OAuth endpoint
          window.location.href = 'http://localhost:8000/auth/google/login';
      }

      // Check for token when page loads
      window.addEventListener('load', function() {
          const token = localStorage.getItem('access_token');
          const user = localStorage.getItem('user');

          if (token && user) {
              showDashboard(JSON.parse(user), token);
          }
      });

      function showDashboard(user, token) {
          document.body.innerHTML = \`
              <div class="dashboard">
                  <h2>Welcome, \${user.full_name}!</h2>
                  <p>Email: \${user.email}</p>
                  <p>Username: \${user.username}</p>
                  <button onclick="logout()">Logout</button>
                  <button onclick="testAPI('\${token}')">Test API</button>
              </div>
          \`;
      }

      function logout() {
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          location.reload();
      }

      async function testAPI(token) {
          try {
              const response = await fetch('http://localhost:8000/auth/me', {
                  headers: {
                      'Authorization': \`Bearer \${token}\`
                  }
              });
              const data = await response.json();
              alert('API Response: ' + JSON.stringify(data, null, 2));
          } catch (error) {
              alert('Error: ' + error.message);
          }
      }
    </script>
  </body>
</html>
```

### Method 2: React Implementation

```jsx
import React, { useState, useEffect } from 'react';

const GoogleAuth = () => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(null);

    useEffect(() => {
        // Check for existing authentication
        const savedToken = localStorage.getItem('access_token');
        const savedUser = localStorage.getItem('user');

        if (savedToken && savedUser) {
            setToken(savedToken);
            setUser(JSON.parse(savedUser));
        }
    }, []);

    const handleGoogleLogin = () => {
        window.location.href = 'http://localhost:8000/auth/google/login';
    };

    const handleLogout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        setUser(null);
        setToken(null);
    };

    const testAPI = async () => {
        try {
            const response = await fetch('http://localhost:8000/auth/me', {
                headers: {
                    'Authorization': \`Bearer \${token}\`
                }
            });
            const data = await response.json();
            console.log('User data:', data);
        } catch (error) {
            console.error('API Error:', error);
        }
    };

    if (user) {
        return (
            <div className="dashboard">
                <h2>Welcome, {user.full_name}!</h2>
                <p>Email: {user.email}</p>
                <button onClick={handleLogout}>Logout</button>
                <button onClick={testAPI}>Test API</button>
            </div>
        );
    }

    return (
        <div className="login-container">
            <h2>Sign In</h2>
            <button
                className="google-btn"
                onClick={handleGoogleLogin}
            >
                Continue with Google
            </button>
        </div>
    );
};

export default GoogleAuth;
```

### Method 3: Vue.js Implementation

```vue
<template>
  <div class="auth-container">
    <div v-if="!user" class="login">
      <h2>Sign In</h2>
      <button @click="signInWithGoogle" class="google-btn">
        Continue with Google
      </button>
    </div>

    <div v-else class="dashboard">
      <h2>Welcome, {{ user.full_name }}!</h2>
      <p>Email: {{ user.email }}</p>
      <button @click="logout">Logout</button>
      <button @click="testAPI">Test API</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'GoogleAuth',
  data() {
    return {
      user: null,
      token: null
    }
  },
  mounted() {
    this.checkAuth();
  },
  methods: {
    checkAuth() {
      const savedToken = localStorage.getItem('access_token');
      const savedUser = localStorage.getItem('user');

      if (savedToken && savedUser) {
        this.token = savedToken;
        this.user = JSON.parse(savedUser);
      }
    },
    signInWithGoogle() {
      window.location.href = 'http://localhost:8000/auth/google/login';
    },
    logout() {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      this.user = null;
      this.token = null;
    },
    async testAPI() {
      try {
        const response = await fetch('http://localhost:8000/auth/me', {
          headers: {
            'Authorization': \`Bearer \${this.token}\`
          }
        });
        const data = await response.json();
        console.log('User data:', data);
      } catch (error) {
        console.error('API Error:', error);
      }
    }
  }
}
</script>
```

## 📱 Mobile App Integration

### React Native

```javascript
import { Linking } from "react-native";

const GoogleAuth = () => {
  const handleGoogleLogin = () => {
    // Open OAuth URL in browser
    Linking.openURL("http://localhost:8000/auth/google/login");
  };

  // Handle deep link callback
  useEffect(() => {
    const handleDeepLink = (url) => {
      if (url.includes("access_token=")) {
        const token = url.split("access_token=")[1].split("&")[0];
        // Store token and redirect to app
        AsyncStorage.setItem("access_token", token);
      }
    };

    Linking.addEventListener("url", handleDeepLink);
    return () => Linking.removeEventListener("url", handleDeepLink);
  }, []);

  return (
    <TouchableOpacity onPress={handleGoogleLogin}>
      <Text>Continue with Google</Text>
    </TouchableOpacity>
  );
};
```

## 🧪 Testing

### 1. Test Configuration

```bash
curl http://localhost:8000/auth/google/status
```

Expected response:

```json
{
  "google_oauth_configured": true,
  "redirect_uri": "http://localhost:8000/auth/google/callback",
  "login_url": "/auth/google/login"
}
```

### 2. Test OAuth Flow

1. Open browser: `http://localhost:8000/auth/google/login`
2. Sign in with Google
3. Should redirect to callback with success page
4. Token should be stored in localStorage

### 3. Test API with Token

```javascript
fetch("http://localhost:8000/auth/me", {
  headers: {
    Authorization: "Bearer YOUR_JWT_TOKEN_HERE",
  },
})
  .then((response) => response.json())
  .then((data) => console.log(data));
```

## 🎨 CSS Styling

```css
.google-btn {
  background-color: #4285f4;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  transition: background-color 0.3s ease;
}

.google-btn:hover {
  background-color: #3367d6;
}

.google-btn:active {
  background-color: #2d5aa0;
}

.login-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  text-align: center;
}

.dashboard {
  max-width: 600px;
  margin: 50px auto;
  padding: 20px;
  text-align: center;
}
```

## 🔧 Troubleshooting

### Common Issues

1. **"Failed to fetch" in Swagger**

   - ✅ **Normal behavior** - OAuth requires browser redirects
   - ✅ **Solution**: Test in browser, not Swagger UI

2. **CORS Errors**

   - ✅ **Check**: CORS middleware is configured in FastAPI
   - ✅ **Check**: Frontend and backend URLs match

3. **Invalid Client Error**

   - ✅ **Check**: `GOOGLE_CLIENT_ID` is correct
   - ✅ **Check**: Redirect URI matches Google Console

4. **Token Not Working**
   - ✅ **Check**: Token is stored correctly in localStorage
   - ✅ **Check**: Authorization header format: `Bearer <token>`

### Debug Mode

Enable debug logging in your backend:

```python
import logging
logging.getLogger("GOOGLE_OAUTH").setLevel(logging.DEBUG)
```

## 📚 API Reference

### Response Models

**GoogleAuthResponse:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "uuid-string",
    "email": "user@gmail.com",
    "username": "username",
    "full_name": "User Name",
    "profile_picture": "https://lh3.googleusercontent.com/..."
  }
}
```

**Error Response:**

```json
{
  "detail": "Error message"
}
```

## 🚀 Production Deployment

### Environment Variables

```env
# Production settings
GOOGLE_CLIENT_ID=your-production-client-id
GOOGLE_CLIENT_SECRET=your-production-client-secret
GOOGLE_REDIRECT_URI=https://yourdomain.com/auth/google/callback
```

### Security Considerations

- ✅ Use HTTPS in production
- ✅ Set secure redirect URIs
- ✅ Validate JWT tokens properly
- ✅ Store secrets securely
- ✅ Implement rate limiting

## 📞 Support

For issues or questions:

1. Check the troubleshooting section
2. Verify Google Cloud Console configuration
3. Test with the provided examples
4. Check server logs for detailed error messages

---

**Built with ❤️ using FastAPI and functional programming principles**
