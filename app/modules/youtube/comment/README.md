# Video Comments API Documentation

Complete API documentation for YouTube video comments management with caching and refresh functionality.

---

## 📋 Table of Contents

1. [GET Video Comments API](#1-📖-get-video-comments-api)
2. [DELETE Comment API](#2-🗑️-delete-comment-api)
3. [REPLY to Comment API](#3-💬-reply-to-comment-api)
4. [REPLY to Multiple Comments API](#4-💬-reply-to-multiple-comments-api)
5. [Common Response Fields](#5-📊-common-response-fields)
6. [Error Handling](#6-❌-error-handling)

---

## 1. 📖 GET Video Comments API

Retrieve comments for a specific video with caching and limit functionality.

### 1.1 Curl Commands

#### 1.1.1 Get from Database Cache (Default)

```bash
curl -X GET "http://localhost:8000/comments/ngYXsg4z8K8?limit=20&refresh=false&include_replies=true" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

#### 1.1.2 Get Fresh from YouTube (with Refresh)

```bash
curl -X GET "http://localhost:8000/comments/ngYXsg4z8K8?limit=10&refresh=true&include_replies=false" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

#### 1.1.3 Get Top-Level Comments Only

```bash
curl -X GET "http://localhost:8000/comments/ngYXsg4z8K8?limit=15&include_replies=false" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

### 1.2 Success Response

```json
{
  "success": true,
  "message": "Comments fetched from YouTube and saved to database",
  "data": {
    "video_id": "ngYXsg4z8K8",
    "total_comments": 15,
    "limit": 20,
    "refresh": false,
    "comments_source": "youtube",
    "comments": [
      {
        "comment_id": "UgzX-2qKm3eR7g",
        "parent_comment_id": null,
        "author_display_name": "Tech Reviewer",
        "author_channel_id": "UC1234567890abcdef",
        "author_profile_image_url": "https://yt3.ggpht.com/photo.jpg",
        "text_display": "Great video! <a href=\"https://example.com\">Check this out</a>",
        "text_original": "Great video! Check this out",
        "like_count": 25,
        "published_at": "2023-10-15T14:30:00+00:00",
        "updated_at": "2023-10-15T14:30:00+00:00",
        "is_reply": false,
        "reply_count": 3
      },
      {
        "comment_id": "UgzX-2qKm3eR7g_reply_1",
        "parent_comment_id": "UgzX-2qKm3eR7g",
        "author_display_name": "Viewer123",
        "author_channel_id": "UC0987654321fedcba",
        "author_profile_image_url": "https://yt3.ggpht.com/photo2.jpg",
        "text_display": "I agree! Very informative",
        "text_original": "I agree! Very informative",
        "like_count": 5,
        "published_at": "2023-10-15T15:45:00+00:00",
        "updated_at": "2023-10-15T15:45:00+00:00",
        "is_reply": true,
        "reply_count": 0
      }
    ]
  }
}
```

### 1.3 Query Parameters

| Parameter         | Type      | Default | Description                                                                   |
| ----------------- | --------- | ------- | ----------------------------------------------------------------------------- |
| `limit`           | `integer` | `20`    | Number of comments to retrieve (1-100)                                        |
| `refresh`         | `boolean` | `false` | `true` = fetch fresh data from YouTube API, `false` = get from database cache |
| `include_replies` | `boolean` | `true`  | Include comment replies in the response                                       |

### 1.4 Features

- **Smart Caching**: Comments are cached in database for faster subsequent requests
- **Refresh Functionality**: Force fetch fresh data from YouTube API
- **Limit Control**: Control number of comments returned (1-100)
- **Reply Support**: Include/exclude comment replies
- **Author Information**: Full author details with profile images
- **Like Counts**: Track comment engagement
- **Timestamps**: Publication and update timestamps

---

## 2. 🗑️ DELETE Comment API

Permanently delete a comment from YouTube and remove from database.

### 2.1 Curl Command

```bash
curl -X DELETE "http://localhost:8000/comments/UgzX-2qKm3eR7g" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

### 2.2 Success Response

```json
{
  "success": true,
  "message": "Comment deleted successfully from YouTube and removed from database",
  "deleted_comment_id": "UgzX-2qKm3eR7g"
}
```

### 2.3 Error Responses

#### Comment Not Found

```json
{
  "success": false,
  "message": "Comment not found in database for the current user",
  "deleted_comment_id": null
}
```

#### Permission Denied

```json
{
  "success": false,
  "message": "Comment not found on YouTube or you don't have permission to delete it",
  "deleted_comment_id": null
}
```

### 2.4 ⚠️ Critical Warnings

- **🚨 PERMANENT**: This action cannot be undone
- **🚨 IRREVERSIBLE**: Comment is permanently deleted from YouTube
- **🚨 OWNER ONLY**: Can only delete comments you posted
- **🚨 LOSES EVERYTHING**: Comment text, likes, replies - all gone forever
- **🚨 AUTHENTICATION REQUIRED**: Must have valid YouTube OAuth tokens

### 2.5 Requirements

- Comment must exist in your database (user verification)
- Comment must be posted by the authenticated user
- Valid YouTube API credentials and OAuth tokens required
- YouTube API delete permissions

---

## 3. 💬 REPLY to Comment API

Reply to a single comment on YouTube.

### 3.1 Curl Command

```bash
curl -X POST "http://localhost:8000/comments/reply" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "parent_comment_id": "UgzX-2qKm3eR7g",
    "reply_text": "Thanks for your comment! I appreciate your feedback."
  }'
```

### 3.2 Request Schema

```json
{
  "parent_comment_id": "string - YouTube comment ID to reply to",
  "reply_text": "string - Reply text content (1-5000 characters)"
}
```

### 3.3 Success Response

```json
{
  "parent_comment_id": "UgzX-2qKm3eR7g",
  "reply_comment_id": "UgzX-2qKm3eR7g_reply_123",
  "reply_text": "Thanks for your comment! I appreciate your feedback.",
  "success": true,
  "message": "Reply posted successfully to YouTube and saved to database"
}
```

### 3.4 Error Responses

#### Parent Comment Not Found

```json
{
  "parent_comment_id": "UgzX-2qKm3eR7g",
  "reply_comment_id": null,
  "reply_text": "Thanks for your comment!",
  "success": false,
  "message": "Parent comment not found on YouTube"
}
```

#### ⚠️ YouTube API Limitation - Cannot Reply to Replies

```json
{
  "parent_comment_id": "UgzWBKmY5Wv_RQvpGNZ4AaABAg.ANhjYVvoFGxANhj_ZsqFn5",
  "reply_comment_id": null,
  "reply_text": "Thanks for your comment!",
  "success": false,
  "message": "YouTube API does not support replying to replies. You can only reply to top-level comments."
}
```

#### Authentication Failed

```json
{
  "parent_comment_id": "UgzX-2qKm3eR7g",
  "reply_comment_id": null,
  "reply_text": "Thanks for your comment!",
  "success": false,
  "message": "Failed to authenticate with YouTube API. Please ensure you have set up YouTube credentials and OAuth tokens."
}
```

### 3.5 ⚠️ Important Limitations

- **Top-Level Comments Only**: You can only reply to original comments, not to replies
- **YouTube API Restriction**: This is a limitation of the YouTube Data API, not our implementation
- **Comment ID Format**:
  - Original comments: `UgzWBKmY5Wv_RQvpGNZ4AaABAg` ✅
  - Replies: `UgzWBKmY5Wv_RQvpGNZ4AaABAg.ANhjYVvoFGxANhj_ZsqFn5` ❌

## 4. 🤖 AI Reply Generation API

### 4.1 Generate AI Replies for Comments

**Endpoint**: `POST /api/youtube/comments/generate-ai-replies`

Generate intelligent, context-aware replies to video comments using AI. The system uses the video transcript as context to create personalized, engaging responses.

**Request Body**:

```json
{
  "comments": [
    {
      "comment_id": "UgzWBKmY5Wv_RQvpGNZ4AaABAg",
      "comment_text": "Great video! Thanks for sharing."
    },
    {
      "comment_id": "UgzWBKmY5Wv_RQvpGNZ4AaABAg2",
      "comment_text": "Could you explain more about this topic?"
    }
  ]
}
```

**Parameters**:

- `comments` (required): List of comment objects with ID and text (1-10 comments)
  - `comment_id` (required): Comment ID
  - `comment_text` (required): Comment text content

**Response**:

```json
{
  "success": true,
  "message": "Generated 2 AI replies successfully",
  "generated_replies": [
    {
      "comment_id": "UgzWBKmY5Wv_RQvpGNZ4AaABAg",
      "comment_text": "Great video! Thanks for sharing.",
      "author_name": "Anonymous",
      "generated_reply": "Thank you so much! I'm really glad you found it helpful. If you enjoyed this content, make sure to subscribe for more tutorials like this! 🎓✨",
      "confidence": 0.85
    },
    {
      "comment_id": "UgzWBKmY5Wv_RQvpGNZ4AaABAg2",
      "comment_text": "Could you explain more about this topic?",
      "author_name": "Anonymous",
      "generated_reply": "Absolutely! That's a great question. I actually have another video coming up next week that dives deeper into the advanced concepts. In the meantime, feel free to ask any specific questions in the comments - I love helping you all learn! 📚",
      "confidence": 0.92
    }
  ],
  "total_generated": 2
}
```

**cURL Example**:

```bash
curl -X POST "http://localhost:8000/api/youtube/comments/generate-ai-replies" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "comments": [
      {
        "comment_id": "UgzWBKmY5Wv_RQvpGNZ4AaABAg",
        "comment_text": "Great video! Thanks for sharing."
      }
    ]
  }'
```

### 4.2 AI Agent Features

- **Multiple Model Fallbacks**: Tries different AI models for reliability
- **Personalized Replies**: Addresses specific points in each comment
- **Engagement Optimization**: Encourages likes, subscriptions, and further comments
- **Friendly Tone**: Uses warm, conversational tone by default

### 4.3 Workflow Example

1. **Generate Replies**: Use this API to get AI-generated replies
2. **Review & Edit**: Check the generated replies in your UI
3. **Post Replies**: Use the reply posting APIs to actually post the replies to YouTube

```javascript
// Frontend workflow example
const generateReplies = async (comments) => {
  // Step 1: Generate AI replies
  const response = await fetch("/api/youtube/comments/generate-ai-replies", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      comments: comments,
    }),
  });

  const aiReplies = await response.json();

  // Step 2: Show generated replies to user for review
  showReplyPreview(aiReplies.generated_replies);

  // Step 3: User clicks "Post Reply" button
  // Step 4: Use the reply posting API to actually post to YouTube
  const postReply = async (commentId, replyText) => {
    await fetch("/api/youtube/comments/reply", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        parent_comment_id: commentId,
        reply_text: replyText,
      }),
    });
  };
};
```

---

## 4. 💬 REPLY to Multiple Comments API

Reply to multiple comments on YouTube (1-10 replies at once).

### 4.1 Curl Command

```bash
curl -X POST "http://localhost:8000/comments/reply-multiple" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "replies": [
      {
        "parent_comment_id": "UgzX-2qKm3eR7g",
        "reply_text": "Thanks for your comment!"
      },
      {
        "parent_comment_id": "UgzX-2qKm3eR7h",
        "reply_text": "Great question! Let me explain..."
      },
      {
        "parent_comment_id": "UgzX-2qKm3eR7i",
        "reply_text": "I appreciate your feedback!"
      }
    ]
  }'
```

### 4.2 Request Schema

```json
{
  "replies": [
    {
      "parent_comment_id": "string - YouTube comment ID to reply to",
      "reply_text": "string - Reply text content (1-5000 characters)"
    }
  ]
}
```

### 4.3 Success Response (All Successful)

```json
{
  "success": true,
  "message": "All 3 replies posted successfully",
  "total_replies_attempted": 3,
  "successful_replies": 3,
  "failed_replies": 0,
  "replies": [
    {
      "parent_comment_id": "UgzX-2qKm3eR7g",
      "reply_comment_id": "UgzX-2qKm3eR7g_reply_123",
      "reply_text": "Thanks for your comment!",
      "success": true,
      "message": "Reply posted successfully to YouTube and saved to database"
    },
    {
      "parent_comment_id": "UgzX-2qKm3eR7h",
      "reply_comment_id": "UgzX-2qKm3eR7h_reply_124",
      "reply_text": "Great question! Let me explain...",
      "success": true,
      "message": "Reply posted successfully to YouTube and saved to database"
    },
    {
      "parent_comment_id": "UgzX-2qKm3eR7i",
      "reply_comment_id": "UgzX-2qKm3eR7i_reply_125",
      "reply_text": "I appreciate your feedback!",
      "success": true,
      "message": "Reply posted successfully to YouTube and saved to database"
    }
  ]
}
```

### 4.4 Partial Success Response

```json
{
  "success": false,
  "message": "2 replies successful, 1 failed",
  "total_replies_attempted": 3,
  "successful_replies": 2,
  "failed_replies": 1,
  "replies": [
    {
      "parent_comment_id": "UgzX-2qKm3eR7g",
      "reply_comment_id": "UgzX-2qKm3eR7g_reply_123",
      "reply_text": "Thanks for your comment!",
      "success": true,
      "message": "Reply posted successfully to YouTube and saved to database"
    },
    {
      "parent_comment_id": "UgzX-2qKm3eR7h",
      "reply_comment_id": null,
      "reply_text": "Great question! Let me explain...",
      "success": false,
      "message": "Parent comment not found on YouTube"
    },
    {
      "parent_comment_id": "UgzX-2qKm3eR7i",
      "reply_comment_id": "UgzX-2qKm3eR7i_reply_125",
      "reply_text": "I appreciate your feedback!",
      "success": true,
      "message": "Reply posted successfully to YouTube and saved to database"
    }
  ]
}
```

### 4.5 Features

- **Batch Processing**: Reply to 1-10 comments at once
- **Individual Status**: Each reply has its own success/failure status
- **Partial Success**: Some replies can succeed while others fail
- **Detailed Results**: Complete breakdown of successful vs failed replies
- **Error Isolation**: One failed reply doesn't stop others from processing

---

## 5. 📊 Common Response Fields

### 5.1 Comments List Object

```json
{
  "video_id": "string - YouTube video ID",
  "total_comments": "integer - Number of comments returned",
  "limit": "integer - Maximum comments requested",
  "refresh": "boolean - Whether data was refreshed from YouTube",
  "comments_source": "string - 'database' or 'youtube'"
}
```

### 5.2 Individual Comment Object

```json
{
  "comment_id": "string - YouTube comment ID",
  "parent_comment_id": "string|null - Parent comment ID for replies",
  "author_display_name": "string - Comment author's display name",
  "author_channel_id": "string - Author's YouTube channel ID",
  "author_profile_image_url": "string - Author's profile image URL",
  "text_display": "string - Formatted comment text with HTML",
  "text_original": "string - Plain text comment",
  "like_count": "integer - Number of likes on comment",
  "published_at": "datetime - When comment was published",
  "updated_at": "datetime - When comment was last updated",
  "is_reply": "boolean - Whether this is a reply to another comment",
  "reply_count": "integer - Number of replies to this comment"
}
```

---

## 6. ❌ Error Handling

### 6.1 Common Error Responses

#### Authentication Error

```json
{
  "success": false,
  "message": "Failed to authenticate with YouTube API. Please ensure you have set up YouTube credentials and OAuth tokens.",
  "data": null
}
```

#### Video Not Found

```json
{
  "success": false,
  "message": "Error fetching comments from YouTube API: Video not found",
  "data": null
}
```

#### Comments Disabled

```json
{
  "success": true,
  "message": "Comments retrieved from database successfully",
  "data": {
    "video_id": "ngYXsg4z8K8",
    "total_comments": 0,
    "limit": 20,
    "refresh": false,
    "comments_source": "database",
    "comments": []
  }
}
```

#### Invalid Parameters

```json
{
  "detail": [
    {
      "loc": ["query", "limit"],
      "msg": "ensure this value is greater than or equal to 1",
      "type": "value_error.number.not_ge",
      "ctx": { "limit_value": 1 }
    }
  ]
}
```

### 6.2 HTTP Status Codes

| Status Code | Description                    |
| ----------- | ------------------------------ |
| `200`       | Success                        |
| `400`       | Bad Request (validation error) |
| `401`       | Unauthorized (invalid token)   |
| `404`       | Not Found (video not found)    |
| `500`       | Internal Server Error          |

### 6.3 Error Types

- `authentication_failed` - YouTube API authentication issues
- `video_not_found` - Video doesn't exist or comments disabled
- `youtube_api_error` - YouTube API returned an error
- `database_error` - Database operation failed
- `validation_error` - Input validation failed

---

## 📝 Notes

### Caching Strategy

- **Database Cache**: Comments are stored in database for faster access
- **Refresh Option**: Use `refresh=true` to get latest comments from YouTube
- **Smart Updates**: Existing comments are updated, new ones are added

### YouTube API Limits

- YouTube API has quotas and rate limits
- Use `refresh=false` for cached data to avoid hitting limits
- Fresh data (`refresh=true`) should be used sparingly
- Comments API has lower quotas than other YouTube APIs

### Comment Processing

- **HTML Processing**: `text_display` contains formatted HTML, `text_original` is plain text
- **Reply Handling**: Replies are linked to parent comments via `parent_comment_id`
- **Author Info**: Full author details including profile images
- **Engagement**: Like counts and reply counts are tracked

### Rate Limiting

- YouTube Comments API: 10,000 quota units per day
- Each commentThreads.list request: ~1-5 quota units
- Use caching to minimize API calls
- Monitor quota usage in YouTube Developer Console

---

_Last updated: January 2025_
