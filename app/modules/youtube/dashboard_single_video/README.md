# Single Video API Documentation

Complete API documentation for YouTube single video management with analytics, thumbnails, and transcripts.

---

## 📋 Table of Contents

1. [GET Video Details API](#1-📖-get-video-details-api)
2. [UPDATE Video Details API](#2-✏️-update-video-details-api)
3. [DELETE Video API](#3-🗑️-delete-video-api)
4. [Upload Custom Thumbnail API](#4-🖼️-upload-custom-thumbnail-api)
5. [Select Generated Thumbnail API](#5-🎨-select-generated-thumbnail-api)
6. [Common Response Fields](#6-📊-common-response-fields)
7. [Error Handling](#7-❌-error-handling)

---

## 1. 📖 GET Video Details API

Retrieve comprehensive video details including analytics, thumbnails, and transcripts.

### 1.1 Curl Commands

#### 1.1.1 Get from Database Cache

```bash
curl -X GET "http://localhost:8000/single-video/ngYXsg4z8K8?refresh=false" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

#### 1.1.2 Get Fresh from YouTube (with Analytics)

```bash
curl -X GET "http://localhost:8000/single-video/ngYXsg4z8K8?refresh=true" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

### 1.2 Success Response

```json
{
  "success": true,
  "message": "Video details fetched from YouTube and saved to database",
  "data": {
    "success": true,
    "message": "Video details fetched from YouTube and saved to database",
    "video_details": {
      "video_id": "ngYXsg4z8K8",
      "title": "Final Test: Infinix Hot 60 Pro Plus Review",
      "description": "This is a test description updated via API...",
      "thumbnail_link": "https://i.ytimg.com/vi/ngYXsg4z8K8/hqdefault.jpg",
      "playlist": null,
      "privacy_status": "public",
      "custom_thumbnail_path": "/path/to/custom/thumbnail.png",

      // 🆕 ANALYTICS FIELDS
      "view_count": 15420,
      "like_count": 892,
      "comment_count": 156,
      "watch_time_minutes": 8.75,
      "published_at": "2023-10-15T14:30:00+00:00",
      "youtube_video_url": "https://www.youtube.com/watch?v=ngYXsg4z8K8",
      "days_since_published": 45,
      "views_per_day": 342.67,

      // TRANSCRIPT FIELDS
      "transcript": "{\"segments\": [{\"timestamp\": \"00:00\", \"text\": \"यह मोबाइल फोन\"}], \"source\": \"youtube\", \"language\": \"hi\"}",
      "transcript_available": true,
      "transcript_source": "database"
    },
    "refreshed": false
  }
}
```

### 1.3 Query Parameters

| Parameter | Type      | Default | Description                                                                              |
| --------- | --------- | ------- | ---------------------------------------------------------------------------------------- |
| `refresh` | `boolean` | `false` | `true` = fetch fresh data from YouTube with analytics, `false` = get from database cache |

---

## 2. ✏️ UPDATE Video Details API

Update video metadata on YouTube and sync with database.

### 2.1 Curl Commands

#### 2.1.1 Update Title Only

```bash
curl -X PUT "http://localhost:8000/single-video/ngYXsg4z8K8" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "New Video Title"}'
```

#### 2.1.2 Update Multiple Fields

```bash
curl -X PUT "http://localhost:8000/single-video/ngYXsg4z8K8" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Video Title",
    "description": "New video description with detailed content",
    "privacy_status": "public",
    "playlist_id": "PLrAXtmRdnEQy8Kjw-6vwAOq5-g2s0o4_"
  }'
```

#### 2.1.3 Remove from Current Playlist

```bash
curl -X PUT "http://localhost:8000/single-video/ngYXsg4z8K8" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"playlist_id": ""}'
```

### 2.2 Request Schema

```json
{
  "title": "string (optional) - Video title",
  "description": "string (optional) - Video description",
  "privacy_status": "public|private|unlisted (optional) - Video privacy",
  "playlist_id": "string (optional) - Playlist ID to add video to, empty string to remove"
}
```

### 2.3 Success Response

```json
{
  "success": true,
  "message": "Successfully updated video fields: title, privacy_status",
  "updated_fields": ["title", "privacy_status"],
  "video_details": {
    "video_id": "ngYXsg4z8K8",
    "title": "New Video Title",
    "description": "Updated description...",
    "thumbnail_link": "https://i.ytimg.com/vi/ngYXsg4z8K8/hqdefault.jpg",
    "privacy_status": "public",
    "view_count": 15420,
    "like_count": 892,
    "comment_count": 156,
    "custom_thumbnail_path": "/path/to/custom/thumbnail.png"
  }
}
```

---

## 3. 🗑️ DELETE Video API

Permanently delete video from YouTube and remove from database.

### 3.1 Curl Command

```bash
curl -X DELETE "http://localhost:8000/single-video/ngYXsg4z8K8" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

### 3.2 Success Response

```json
{
  "success": true,
  "message": "Video deleted successfully from YouTube and removed from database",
  "deleted_video_id": "ngYXsg4z8K8"
}
```

### 3.3 ⚠️ Critical Warnings

- **🚨 PERMANENT**: This action cannot be undone
- **🚨 IRREVERSIBLE**: Video is permanently deleted from YouTube
- **🚨 LOSES EVERYTHING**: Views, comments, likes, analytics - all gone forever
- **🚨 BROKEN LINKS**: All existing links will return 404
- **🚨 OWNER ONLY**: Can only delete videos you own

---

## 4. 🖼️ Upload Custom Thumbnail API

Upload a custom thumbnail image for your video.

### 4.1 Curl Command

```bash
curl -X POST "http://localhost:8000/single-video/ngYXsg4z8K8/upload-custom-thumbnail?dir_path=thumbnails" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@/path/to/your/thumbnail.png"
```

### 4.2 Request Parameters

| Parameter  | Type     | Required | Description                                         |
| ---------- | -------- | -------- | --------------------------------------------------- |
| `file`     | `File`   | ✅       | Image file (PNG, JPG, JPEG, GIF, WEBP)              |
| `dir_path` | `string` | ❌       | Directory to save thumbnail (default: "thumbnails") |

### 4.3 Success Response

```json
{
  "success": true,
  "message": "Custom thumbnail uploaded successfully",
  "video_id": "ngYXsg4z8K8",
  "thumbnail_url": "/thumbnails/ngYXsg4z8K8.png",
  "method_used": "custom_upload"
}
```

### 4.4 File Requirements

- **Supported formats**: PNG, JPG, JPEG, GIF, WEBP
- **Max file size**: 10MB (configurable)
- **Recommended size**: 1280x720 pixels (16:9 aspect ratio)
- **Filename**: Automatically renamed to `{video_id}.png`

---

## 5. 🎨 Select Generated Thumbnail API

Download and apply a generated thumbnail from an external URL.

### 5.1 Curl Command

```bash
curl -X POST "http://localhost:8000/single-video/ngYXsg4z8K8/select-generated-thumbnail?url=https://image.pollinations.ai/prompt/HYPER-REALISTIC%20close-up%20of%20the%20Infinix%20Hot%2060%20Pro%20Plus&dir_path=thumbnails" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

### 5.2 Query Parameters

| Parameter  | Type     | Required | Description                                         |
| ---------- | -------- | -------- | --------------------------------------------------- |
| `url`      | `string` | ✅       | URL of the generated thumbnail image                |
| `dir_path` | `string` | ❌       | Directory to save thumbnail (default: "thumbnails") |

### 5.3 Success Response

```json
{
  "success": true,
  "message": "Image downloaded successfully to /thumbnails/ngYXsg4z8K8.png",
  "video_id": "ngYXsg4z8K8",
  "thumbnail_url": "/thumbnails/ngYXsg4z8K8.png",
  "method_used": "generated_thumbnail"
}
```

### 5.4 Features

- **Auto-download**: Downloads image from provided URL
- **Database update**: Updates `custom_thumbnail_path` field
- **YouTube sync**: Automatically uploads to YouTube
- **Error handling**: Graceful failure if YouTube upload fails

---

## 6. 📊 Common Response Fields

### 6.1 Video Details Object

All video detail responses include these fields:

#### Basic Information

```json
{
  "video_id": "string - YouTube video ID",
  "title": "string - Video title",
  "description": "string - Video description",
  "privacy_status": "public|private|unlisted - Video privacy setting"
}
```

#### Thumbnail Information

```json
{
  "thumbnail_link": "string - Original YouTube thumbnail URL",
  "custom_thumbnail_path": "string - Path to custom uploaded thumbnail"
}
```

#### 🆕 Analytics Information

```json
{
  "view_count": "integer - Total number of views",
  "like_count": "integer - Number of likes",
  "comment_count": "integer - Number of comments",
  "watch_time_minutes": "float - Video duration in minutes",
  "published_at": "datetime - When video was published",
  "youtube_video_url": "string - Direct YouTube watch URL",
  "days_since_published": "integer - Days since publication",
  "views_per_day": "float - Average views per day"
}
```

#### Transcript Information

```json
{
  "transcript": "string - JSON formatted transcript with segments",
  "transcript_available": "boolean - Whether transcript exists",
  "transcript_source": "database|youtube|null - Where transcript came from"
}
```

### 6.2 Transcript Format

Transcripts are stored as JSON strings with this structure:

```json
{
  "segments": [
    {
      "timestamp": "00:00",
      "text": "यह मोबाइल फोन यह मोबाइल फोन दुनिया का"
    },
    {
      "timestamp": "00:03",
      "text": "सबसे पतला मोबाइल फोन है जो कि कर्व्ड"
    }
  ],
  "source": "youtube",
  "language": "hi",
  "fetched_at": "2025-09-29T16:46:12.664251"
}
```

---

## 7. ❌ Error Handling

### 7.1 Common Error Responses

#### Authentication Error

```json
{
  "success": false,
  "message": "Failed to authenticate with YouTube API. Please ensure you have set up YouTube credentials and OAuth tokens.",
  "error_type": "authentication_failed"
}
```

#### Video Not Found

```json
{
  "success": false,
  "message": "Video not found in database for the current user",
  "error_type": "video_not_found",
  "field": "video_id",
  "value": "ngYXsg4z8K8"
}
```

#### File Upload Error

```json
{
  "success": false,
  "message": "File must be an image (jpg, jpeg, png, gif, webp)",
  "error_type": "invalid_file_type",
  "field": "file"
}
```

#### YouTube API Error

```json
{
  "success": false,
  "message": "Error fetching from YouTube API: Video not found",
  "error_type": "youtube_api_error"
}
```

### 7.2 HTTP Status Codes

| Status Code | Description                    |
| ----------- | ------------------------------ |
| `200`       | Success                        |
| `400`       | Bad Request (validation error) |
| `401`       | Unauthorized (invalid token)   |
| `404`       | Not Found (video not found)    |
| `500`       | Internal Server Error          |

### 7.3 Error Types

- `authentication_failed` - YouTube API authentication issues
- `video_not_found` - Video doesn't exist for user
- `invalid_file_type` - Unsupported file format
- `file_too_large` - File exceeds size limit
- `youtube_api_error` - YouTube API returned an error
- `database_error` - Database operation failed
- `validation_error` - Input validation failed

---

## 📝 Notes

### Analytics Data

- Analytics are fetched fresh from YouTube when `refresh=true`
- `views_per_day` is automatically calculated as `total_views / days_since_published`
- `watch_time_minutes` is parsed from YouTube's duration format (PT4M13S)
- All analytics fields are optional and may be `null` if not available

### Thumbnails

- Custom thumbnails are stored separately from YouTube's original thumbnail
- Both `thumbnail_link` (YouTube) and `custom_thumbnail_path` (custom) are available
- Custom thumbnails are automatically uploaded to YouTube when possible

### Transcripts

- Transcripts are fetched automatically when available
- Stored with readable Unicode text (not escaped)
- Support for multiple languages
- Include timestamps and source information

### Rate Limits

- YouTube API has quotas and rate limits
- Use `refresh=false` for cached data to avoid hitting limits
- Fresh data (`refresh=true`) should be used sparingly

---

_Last updated: September 29, 2025_
