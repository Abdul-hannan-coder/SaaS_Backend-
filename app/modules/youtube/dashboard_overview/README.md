# Dashboard Overview API Documentation

This module provides comprehensive dashboard overview functionality for YouTube channel analytics, including both overview metrics and detailed video data.

## API Endpoints

### 1. Dashboard Overview

**Endpoint**: `GET /dashboard-overview/`

Get comprehensive dashboard overview data including channel metrics, monetization progress, content distributions, and performance insights.

### 2. Dashboard Videos

**Endpoint**: `GET /dashboard-overview/videos`

Get all videos for dashboard with detailed analytics and performance metrics.

---

## Dashboard Videos API

### Overview

This endpoint retrieves comprehensive video data for the authenticated user's YouTube channel, including video details, performance metrics, and analytics distributions.

### Endpoint Details

- **URL**: `/dashboard-overview/videos`
- **Method**: `GET`
- **Authentication**: Bearer Token required
- **Content-Type**: `application/json`

### Query Parameters

| Parameter | Type    | Required | Default | Range | Description                                                    |
| --------- | ------- | -------- | ------- | ----- | -------------------------------------------------------------- |
| `refresh` | boolean | No       | `false` | -     | If true, fetch fresh data from YouTube API and update database |
| `limit`   | integer | No       | `50`    | 1-100 | Maximum number of videos to return                             |

### API Logic

- **If `refresh=true`**: Always fetch fresh data from YouTube API and update database
- **If `refresh=false`**: Return cached data from database if exists, otherwise fetch from YouTube API and save to database
- **Limit**: Applied to the final result set (both from database and YouTube API)

---

## cURL Commands

### 1. Get Default Videos (50 videos, cached data)

```bash
curl -X GET "http://localhost:8000/dashboard-overview/videos" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

### 2. Get 10 Videos with Fresh Data

```bash
curl -X GET "http://localhost:8000/dashboard-overview/videos?limit=10&refresh=true" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

### 3. Get 20 Videos from Cache

```bash
curl -X GET "http://localhost:8000/dashboard-overview/videos?limit=20" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

### 4. Get All Videos (100 max) with Refresh

```bash
curl -X GET "http://localhost:8000/dashboard-overview/videos?limit=100&refresh=true" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

---

## Response Structure

### Success Response (200 OK)

```json
{
  "success": true,
  "message": "Dashboard videos retrieved from database successfully. 15 videos found.",
  "data": {
    "videos": [
      {
        "video_id": "9-xRqHRC6dA",
        "title": "Guide to Punjabi Song Lyrics: Translate & Understand Love Verses",
        "description": "Punjabi romantic song new Punjabi music video...",
        "thumbnail_link": "https://i9.ytimg.com/vi/9-xRqHRC6dA/hqdefault.jpg",
        "published_at": "2025-09-30T15:18:55Z",
        "privacy_status": "private",
        "playlist": "UUq15zudCqnnKDvOxnPdDQVw",
        "transcript": null,
        "view_count": 0,
        "like_count": 0,
        "comment_count": 0,
        "watch_time_minutes": 2.6,
        "youtube_video_url": "https://www.youtube.com/watch?v=9-xRqHRC6dA",
        "days_since_published": 3,
        "views_per_day": null,
        "engagement_rate": 0
      }
      // ... more videos
    ],
    "additional_metrics": {
      "total_videos": 15,
      "total_views": 12,
      "total_likes": 2,
      "total_comments": 2,
      "avg_performance": 0.8,
      "performance_distribution": {
        "high_performance": {
          "count": 3,
          "percentage": 20.0
        },
        "medium_performance": {
          "count": 0,
          "percentage": 0.0
        },
        "low_performance": {
          "count": 12,
          "percentage": 80.0
        }
      },
      "engagement_distribution": {
        "high_engagement": {
          "count": 3,
          "percentage": 20.0
        },
        "medium_engagement": {
          "count": 0,
          "percentage": 0.0
        },
        "low_engagement": {
          "count": 12,
          "percentage": 80.0
        }
      }
    }
  },
  "refreshed": false
}
```

### Error Response (500 Internal Server Error)

```json
{
  "detail": "Error retrieving dashboard videos: YouTube API authentication failed"
}
```

---

## Response Field Descriptions

### Main Response Fields

| Field       | Type    | Description                                      |
| ----------- | ------- | ------------------------------------------------ |
| `success`   | boolean | Indicates if the request was successful          |
| `message`   | string  | Human-readable message about the operation       |
| `data`      | object  | Contains the videos and analytics data           |
| `refreshed` | boolean | Indicates if data was refreshed from YouTube API |

### Video Object Fields

| Field                  | Type         | Description                                      |
| ---------------------- | ------------ | ------------------------------------------------ |
| `video_id`             | string       | YouTube video ID                                 |
| `title`                | string       | Video title                                      |
| `description`          | string       | Video description                                |
| `thumbnail_link`       | string       | URL to video thumbnail                           |
| `published_at`         | string       | ISO 8601 timestamp of publication                |
| `privacy_status`       | string       | Video privacy status (public, private, unlisted) |
| `playlist`             | string       | Uploads playlist ID                              |
| `transcript`           | string\|null | JSON string of transcript data or null           |
| `view_count`           | integer      | Number of views                                  |
| `like_count`           | integer      | Number of likes                                  |
| `comment_count`        | integer      | Number of comments                               |
| `watch_time_minutes`   | float        | Average watch time in minutes                    |
| `youtube_video_url`    | string       | Direct YouTube video URL                         |
| `days_since_published` | integer      | Days since video was published                   |
| `views_per_day`        | float\|null  | Average views per day                            |
| `engagement_rate`      | float        | Calculated engagement rate percentage            |

### Additional Metrics Fields

| Field                      | Type    | Description                           |
| -------------------------- | ------- | ------------------------------------- |
| `total_videos`             | integer | Total number of videos returned       |
| `total_views`              | integer | Sum of all video views                |
| `total_likes`              | integer | Sum of all video likes                |
| `total_comments`           | integer | Sum of all video comments             |
| `avg_performance`          | float   | Average views per video               |
| `performance_distribution` | object  | Distribution of videos by performance |
| `engagement_distribution`  | object  | Distribution of videos by engagement  |

### Performance Distribution

| Field                | Type   | Description             |
| -------------------- | ------ | ----------------------- |
| `high_performance`   | object | Videos with 80+ views   |
| `medium_performance` | object | Videos with 40-79 views |
| `low_performance`    | object | Videos with 0-39 views  |

Each performance level contains:

- `count`: Number of videos in this category
- `percentage`: Percentage of total videos

### Engagement Distribution

| Field               | Type   | Description                      |
| ------------------- | ------ | -------------------------------- |
| `high_engagement`   | object | Videos with 10%+ engagement rate |
| `medium_engagement` | object | Videos with 2-9% engagement rate |
| `low_engagement`    | object | Videos with 0-1% engagement rate |

Each engagement level contains:

- `count`: Number of videos in this category
- `percentage`: Percentage of total videos

---

## Performance Categories

### Performance Distribution

- **High Performance**: 80+ views
- **Medium Performance**: 40-79 views
- **Low Performance**: 0-39 views

### Engagement Distribution

- **High Engagement**: 10%+ engagement rate
- **Medium Engagement**: 2-9% engagement rate
- **Low Engagement**: 0-1% engagement rate

_Engagement rate = ((likes + comments) / views) × 100_

---

## Error Handling

### Common Error Scenarios

1. **Authentication Failed**

   ```json
   {
     "detail": "Error retrieving dashboard videos: YouTube API authentication failed"
   }
   ```

2. **No Channel Found**

   ```json
   {
     "detail": "Error retrieving dashboard videos: No channel found for the authenticated user"
   }
   ```

3. **Invalid Limit Parameter**
   ```json
   {
     "detail": "1 validation error for get_dashboard_videos\nlimit\n  ensure this value is greater than or equal to 1"
   }
   ```

---

## Rate Limits

- **YouTube API**: Subject to YouTube Data API v3 quotas
- **Database**: No specific limits
- **Request Limit**: 1-100 videos per request

---

## Notes

- Videos are returned in the order they appear in the YouTube uploads playlist
- Transcript data is fetched using a fallback system (third-party API → official YouTube API)
- All timestamps are in UTC
- The API automatically handles pagination for large video collections
- Cached data is used when `refresh=false` for faster response times
