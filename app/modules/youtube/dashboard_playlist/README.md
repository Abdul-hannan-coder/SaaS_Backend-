# Dashboard Playlist API Documentation

This module provides comprehensive playlist functionality for YouTube channel management with analytics, video details, and caching capabilities.

## 🚀 API Endpoints

### 1. Get All Playlists

**URL**: `GET /playlists/`  
**Authentication**: Bearer Token required

### 2. Get Playlist Details (Top 2 Videos + Analytics)

**URL**: `GET /playlists/{playlist_id}`  
**Authentication**: Bearer Token required

### 3. Get All Videos in Playlist

**URL**: `GET /playlists/{playlist_id}/videos`  
**Authentication**: Bearer Token required

---

## 📋 API Documentation

### 1. Get All Playlists

Retrieves all playlists for the authenticated user with optional refresh functionality.

#### Query Parameters

| Parameter | Type    | Required | Default | Description                                                    |
| --------- | ------- | -------- | ------- | -------------------------------------------------------------- |
| `refresh` | boolean | No       | `false` | If true, fetch fresh data from YouTube API and update database |

#### cURL Examples

**Get cached playlists (faster response):**

```bash
curl -X GET "http://localhost:8000/playlists/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

**Get fresh playlists from YouTube API:**

```bash
curl -X GET "http://localhost:8000/playlists/?refresh=true" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

#### Response Structure

```json
{
  "success": true,
  "message": "Playlists retrieved from database successfully. 5 playlists found.",
  "data": {
    "playlists": [
      {
        "playlist_id": "PLrAXtmRdnEQy6nuLMOV8F4w",
        "playlist_name": "My Favorites"
      },
      {
        "playlist_id": "PLrAXtmRdnEQy6nuLMOV8F4x",
        "playlist_name": "Tutorial Series"
      }
    ]
  },
  "refreshed": false
}
```

---

### 2. Get Playlist Details (Top 2 Videos + Analytics)

Retrieves detailed information about a specific playlist including the top 2 performing videos and comprehensive analytics.

#### Path Parameters

| Parameter     | Type   | Required | Description                                                      |
| ------------- | ------ | -------- | ---------------------------------------------------------------- |
| `playlist_id` | string | Yes      | YouTube playlist ID (e.g., "PLrAXtmRdnEQy6nuLMOV8u4fOqR0U4vO3p") |

#### cURL Examples

**Get playlist details with top 2 videos and analytics:**

```bash
curl -X GET "http://localhost:8000/playlists/PLrAXtmRdnEQy6nuLMOV8u4fOqR0U4vO3p" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

#### Response Structure

```json
{
  "success": true,
  "message": "Playlist details retrieved successfully",
  "data": {
    "playlist_id": "PLrAXtmRdnEQy6nuLMOV8u4fOqR0U4vO3p",
    "playlist_name": "My Tutorial Series",
    "description": "A comprehensive tutorial series covering various topics",
    "thumbnail_url": "https://i.ytimg.com/vi/example/maxresdefault.jpg",
    "video_count": 25,
    "published_at": "2023-01-15T10:30:00Z",
    "channel_title": "My Channel",
    "privacy_status": "public",
    "top_videos": [
      {
        "video_id": "dQw4w9WgXcQ",
        "title": "Amazing Tutorial - Part 1",
        "description": "This is the most popular video in the series",
        "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
        "duration": "PT10M30S",
        "published_at": "2023-01-20T14:00:00Z",
        "view_count": 150000,
        "like_count": 8500,
        "comment_count": 450,
        "privacy_status": "public",
        "watch_time_minutes": 8.5,
        "youtube_video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "performance_type": "top_by_views"
      },
      {
        "video_id": "jNQXAC9IVRw",
        "title": "Best Tutorial Ever - Part 5",
        "description": "This video has the highest engagement",
        "thumbnail_url": "https://i.ytimg.com/vi/jNQXAC9IVRw/maxresdefault.jpg",
        "duration": "PT15M45S",
        "published_at": "2023-02-10T16:30:00Z",
        "view_count": 120000,
        "like_count": 12000,
        "comment_count": 800,
        "privacy_status": "public",
        "watch_time_minutes": 12.3,
        "youtube_video_url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
        "performance_type": "top_by_likes"
      }
    ],
    "analytics": {
      "total_views": 2500000,
      "total_likes": 125000,
      "total_comments": 8500,
      "average_engagement_rate": 0.0534,
      "top_video_by_views_id": "dQw4w9WgXcQ",
      "top_video_by_likes_id": "jNQXAC9IVRw",
      "top_video_by_views_title": "Amazing Tutorial - Part 1",
      "top_video_by_likes_title": "Best Tutorial Ever - Part 5",
      "top_video_by_views_count": 150000,
      "top_video_by_likes_count": 12000,
      "last_analytics_update": "2024-01-15T10:30:00Z"
    }
  }
}
```

---

### 3. Get All Videos in Playlist

Retrieves all videos from a specific playlist with detailed information and optional refresh functionality.

#### Path Parameters

| Parameter     | Type   | Required | Description                                                      |
| ------------- | ------ | -------- | ---------------------------------------------------------------- |
| `playlist_id` | string | Yes      | YouTube playlist ID (e.g., "PLrAXtmRdnEQy6nuLMOV8u4fOqR0U4vO3p") |

#### Query Parameters

| Parameter | Type    | Required | Default | Description                                                    |
| --------- | ------- | -------- | ------- | -------------------------------------------------------------- |
| `refresh` | boolean | No       | `false` | If true, fetch fresh data from YouTube API and update database |

#### cURL Examples

**Get all videos (cached data):**

```bash
curl -X GET "http://localhost:8000/playlists/PLrAXtmRdnEQy6nuLMOV8u4fOqR0U4vO3p/videos" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

**Get all videos (fresh data from YouTube):**

```bash
curl -X GET "http://localhost:8000/playlists/PLrAXtmRdnEQy6nuLMOV8u4fOqR0U4vO3p/videos?refresh=true" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

#### Response Structure

```json
{
  "success": true,
  "message": "Retrieved 25 cached videos from database",
  "data": {
    "playlist_id": "PLrAXtmRdnEQy6nuLMOV8u4fOqR0U4vO3p",
    "playlist_name": "My Tutorial Series",
    "total_videos": 25,
    "videos": [
      {
        "video_id": "dQw4w9WgXcQ",
        "title": "Amazing Tutorial - Part 1",
        "description": "This is the first video in the series",
        "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
        "duration": "PT10M30S",
        "published_at": "2023-01-20T14:00:00Z",
        "view_count": 150000,
        "like_count": 8500,
        "comment_count": 450,
        "privacy_status": "public",
        "watch_time_minutes": 8.5,
        "youtube_video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "days_since_published": 360,
        "views_per_day": 416.67
      },
      {
        "video_id": "jNQXAC9IVRw",
        "title": "Best Tutorial Ever - Part 5",
        "description": "This is the fifth video in the series",
        "thumbnail_url": "https://i.ytimg.com/vi/jNQXAC9IVRw/maxresdefault.jpg",
        "duration": "PT15M45S",
        "published_at": "2023-02-10T16:30:00Z",
        "view_count": 120000,
        "like_count": 12000,
        "comment_count": 800,
        "privacy_status": "public",
        "watch_time_minutes": 12.3,
        "youtube_video_url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
        "days_since_published": 340,
        "views_per_day": 352.94
      }
    ]
  }
}
```

---

## 🗄️ Database Schema

### user_playlist Table

Stores playlist information with comprehensive analytics data.

| Field                      | Type     | Description                                    |
| -------------------------- | -------- | ---------------------------------------------- |
| `id`                       | integer  | Primary key                                    |
| `user_id`                  | UUID     | Foreign key to users table                     |
| `playlist_id`              | string   | YouTube playlist ID                            |
| `playlist_name`            | string   | Playlist name                                  |
| `total_views`              | integer  | Total views across all videos                  |
| `total_likes`              | integer  | Total likes across all videos                  |
| `total_comments`           | integer  | Total comments across all videos               |
| `average_engagement_rate`  | float    | Average engagement rate (likes+comments)/views |
| `top_video_by_views_id`    | string   | Video ID with highest views                    |
| `top_video_by_likes_id`    | string   | Video ID with highest likes                    |
| `top_video_by_views_title` | string   | Title of top video by views                    |
| `top_video_by_likes_title` | string   | Title of top video by likes                    |
| `top_video_by_views_count` | integer  | View count of top video                        |
| `top_video_by_likes_count` | integer  | Like count of top video                        |
| `last_analytics_update`    | datetime | Timestamp of last analytics update             |
| `created_at`               | datetime | Record creation timestamp                      |
| `updated_at`               | datetime | Record update timestamp                        |

### single_video_details Table

Stores detailed information for individual videos.

| Field                   | Type     | Description                     |
| ----------------------- | -------- | ------------------------------- |
| `id`                    | integer  | Primary key                     |
| `video_id`              | string   | YouTube video ID                |
| `user_id`               | UUID     | Foreign key to users table      |
| `title`                 | string   | Video title                     |
| `description`           | text     | Video description               |
| `thumbnail_link`        | string   | Video thumbnail URL             |
| `playlist`              | string   | Associated playlist ID          |
| `privacy_status`        | string   | Video privacy status            |
| `transcript`            | text     | Video transcript (if available) |
| `custom_thumbnail_path` | text     | Custom thumbnail file path      |
| `view_count`            | integer  | Total view count                |
| `like_count`            | integer  | Total like count                |
| `comment_count`         | integer  | Total comment count             |
| `watch_time_minutes`    | float    | Estimated watch time in minutes |
| `published_at`          | datetime | Video publication date          |
| `youtube_video_url`     | string   | Direct YouTube video URL        |
| `days_since_published`  | integer  | Days since video was published  |
| `views_per_day`         | float    | Average views per day           |
| `created_at`            | datetime | Record creation timestamp       |
| `updated_at`            | datetime | Record update timestamp         |

---

## 🔧 Features

### ✅ Core Functionality

- **Playlist Management**: Get all playlists with caching
- **Detailed Analytics**: Comprehensive playlist performance metrics
- **Top Video Selection**: Automatically identifies top 2 performing videos
- **Video Storage**: Stores all video details in database
- **Refresh Control**: Choose between cached or fresh data

### ✅ Performance Optimization

- **Database Caching**: Fast retrieval of cached data
- **Selective Fetching**: Only top 2 videos for detailed view
- **Efficient Storage**: Optimized database schema
- **Pagination Support**: Handles large playlists

### ✅ Analytics & Insights

- **Engagement Metrics**: Views, likes, comments tracking
- **Performance Analysis**: Top video identification
- **Trend Analysis**: Views per day calculations
- **Comprehensive Reporting**: Detailed analytics data

### ✅ Error Handling

- **Authentication**: Bearer token validation
- **API Errors**: YouTube API error handling
- **Database Errors**: Transaction rollback support
- **Validation**: Input parameter validation

---

## 🚨 Error Responses

### Authentication Error

```json
{
  "detail": "Not authenticated"
}
```

### Playlist Not Found

```json
{
  "detail": "Error retrieving playlist details: Playlist not found"
}
```

### YouTube API Error

```json
{
  "detail": "Error retrieving playlists: YouTube API authentication failed"
}
```

### Database Error

```json
{
  "detail": "Error retrieving playlist videos: Database connection failed"
}
```

---

## 📝 Usage Examples

### Get Playlist Analytics

```bash
# Get detailed analytics for a specific playlist
curl -X GET "http://localhost:8000/playlists/PLrAXtmRdnEQy6nuLMOV8u4fOqR0U4vO3p" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Build Video Gallery

```bash
# Get all videos for building a gallery
curl -X GET "http://localhost:8000/playlists/PLrAXtmRdnEQy6nuLMOV8u4fOqR0U4vO3p/videos" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Refresh Data

```bash
# Force refresh from YouTube API
curl -X GET "http://localhost:8000/playlists/?refresh=true" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🔐 Authentication

All endpoints require Bearer token authentication. Include your access token in the Authorization header:

```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

---

## 📊 Rate Limits

- YouTube API has rate limits (10,000 units per day)
- Database queries are optimized for performance
- Caching reduces API calls significantly
- Use `refresh=false` for better performance

---

## 🛠️ Development Notes

- All video data is stored in `single_video_details` table
- Analytics are calculated and stored in `user_playlist` table
- Top 2 videos are selected based on views and likes
- Refresh parameter controls data freshness
- Comprehensive error handling and logging
