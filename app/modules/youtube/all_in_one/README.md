# 🚀 All-in-One Video Processing Module

## Overview

The All-in-One module provides a single API endpoint that automatically generates all available content for a YouTube video in one comprehensive request. This eliminates the need to make multiple API calls and provides a streamlined experience for content creators.

## 🎯 Features

- **📝 Title Generation**: Generate 10 eye-catching YouTube titles
- **📄 Description Generation**: Create comprehensive video descriptions with SEO optimization
- **⏰ Timestamps Generation**: Extract and format video timestamps automatically
- **🖼️ Thumbnail Generation**: Generate multiple thumbnail options
- **⚡ Parallel Processing**: All tasks run efficiently with proper error handling
- **📊 Detailed Results**: Individual success/failure status for each generation task

## 🛠️ API Endpoint

**Endpoint**: `POST /api/youtube/all-in-one/{video_id}/process`

## 📋 Path Parameters

| Parameter  | Type   | Required | Description                   |
| ---------- | ------ | -------- | ----------------------------- |
| `video_id` | string | ✅       | Video ID (UUID or YouTube ID) |

## 📋 Request Body

No request body required - all parameters come from the URL path.

**Note**: All generation features (titles, description, timestamps, thumbnails) are automatically enabled with default settings.

## 📤 Response Format

```json
{
  "success": true,
  "message": "All-in-one processing completed: 4/4 tasks successful",
  "video_id": "dQw4w9WgXcQ",
  "total_tasks": 4,
  "completed_tasks": 4,
  "failed_tasks": 0,
  "processing_time_seconds": 45.67,
  "errors": [],
  "results": {
    "titles": {
      "success": true,
      "message": "Titles generated successfully",
      "generated_titles": [
        "How to Build a React App in 2024",
        "Complete React Tutorial for Beginners",
        "Master React Development: Step-by-Step Guide"
      ]
    },
    "description": {
      "success": true,
      "message": "Description generated successfully",
      "generated_description": "Learn how to build modern React applications..."
    },
    "timestamps": {
      "success": true,
      "message": "Timestamps generated successfully",
      "generated_timestamps": [
        { "time": "0:00", "title": "Introduction" },
        { "time": "2:30", "title": "Setting up the project" },
        { "time": "8:15", "title": "Creating components" }
      ]
    },
    "thumbnails": {
      "success": true,
      "message": "Thumbnails generated successfully",
      "generated_thumbnails": [
        "thumbnail_1.jpg",
        "thumbnail_2.jpg",
        "thumbnail_3.jpg"
      ]
    }
  }
}
```

## 🔧 cURL Example

```bash
curl -X POST "http://localhost:8000/api/youtube/all-in-one/dQw4w9WgXcQ/process" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## **💾 Save Generated Content API**

**Endpoint:** `POST /api/youtube/all-in-one/{video_id}/save-content`

**Purpose:** Save selected generated content (title, thumbnail, description, timestamps) to the video record in the database.

### **Path Parameters:**

| Parameter  | Type   | Required | Description                   |
| ---------- | ------ | -------- | ----------------------------- |
| `video_id` | string | ✅       | Video ID (UUID or YouTube ID) |

### **Request Body:**

```json
{
  "selected_title": "Amazing Python Tutorial for Beginners",
  "selected_thumbnail_url": "https://pollinations.ai/p/cool-image-123",
  "description": "This comprehensive Python tutorial covers all the basics you need to get started with programming. Learn variables, functions, loops, and more in this step-by-step guide perfect for beginners.",
  "timestamps": [
    {
      "time": "00:00",
      "title": "Introduction"
    },
    {
      "time": "02:30",
      "title": "Setting Up Python"
    },
    {
      "time": "05:15",
      "title": "Variables and Data Types"
    },
    {
      "time": "10:45",
      "title": "Functions"
    },
    {
      "time": "15:20",
      "title": "Conclusion"
    }
  ],
  "privacy_status": "public",
  "playlist_name": "Python Tutorials",
  "schedule_datetime": "2024-01-15T10:00:00Z"
}
```

### **Request Parameters:**

| Parameter                | Type                      | Required | Description                                |
| ------------------------ | ------------------------- | -------- | ------------------------------------------ |
| `selected_title`         | string                    | ❌       | Title to save to video record              |
| `selected_thumbnail_url` | string                    | ❌       | Thumbnail URL to download and save         |
| `description`            | string                    | ❌       | Generated description to save              |
| `timestamps`             | List of timestamp objects | ❌       | Generated timestamps to save               |
| `privacy_status`         | string                    | ❌       | Privacy status (public, private, unlisted) |
| `playlist_name`          | string                    | ❌       | Playlist name for the video                |
| `schedule_datetime`      | string                    | ❌       | Schedule datetime (ISO format)             |

### **Response:**

```json
{
  "success": true,
  "message": "Successfully saved content for video dc434041-11a2-41f8-8e3a-ab4538b81289 - Saved: title, thumbnail, description, timestamps",
  "video_id": "dc434041-11a2-41f8-8e3a-ab4538b81289",
  "saved_content": {
    "title": "Amazing Python Tutorial for Beginners",
    "thumbnail": {
      "url": "https://pollinations.ai/p/cool-image-123",
      "path": "/thumbnails/dc434041-11a2-41f8-8e3a-ab4538b81289_thumbnail.jpg"
    },
    "description": "This comprehensive Python tutorial covers all the basics you need to get started with programming. Learn variables, functions, loops, and more in this step-by-step guide perfect for beginners.",
    "timestamps": [
      {
        "time": "00:00",
        "title": "Introduction"
      },
      {
        "time": "02:30",
        "title": "Setting Up Python"
      },
      {
        "time": "05:15",
        "title": "Variables and Data Types"
      },
      {
        "time": "10:45",
        "title": "Functions"
      },
      {
        "time": "15:20",
        "title": "Conclusion"
      }
    ],
    "privacy_status": "public",
    "playlist_name": "Python Tutorials",
    "schedule_datetime": "2024-01-15T10:00:00Z"
  },
  "thumbnail_path": "/thumbnails/dc434041-11a2-41f8-8e3a-ab4538b81289_thumbnail.jpg"
}
```

### **cURL Example:**

```bash
curl -X POST "http://localhost:8000/api/youtube/all-in-one/dc434041-11a2-41f8-8e3a-ab4538b81289/save-content" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "selected_title": "Amazing Python Tutorial for Beginners",
    "selected_thumbnail_url": "https://pollinations.ai/p/cool-image-123",
    "description": "This comprehensive Python tutorial covers all the basics you need to get started with programming. Learn variables, functions, loops, and more in this step-by-step guide perfect for beginners.",
    "timestamps": [
      {
        "time": "00:00",
        "title": "Introduction"
      },
      {
        "time": "02:30",
        "title": "Setting Up Python"
      },
      {
        "time": "05:15",
        "title": "Variables and Data Types"
      },
      {
        "time": "10:45",
        "title": "Functions"
      },
      {
        "time": "15:20",
        "title": "Conclusion"
      }
    ],
    "privacy_status": "public",
    "playlist_name": "Python Tutorials",
    "schedule_datetime": "2024-01-15T10:00:00Z"
  }'
```

## 💡 Usage Examples

### Frontend JavaScript

```javascript
const processVideoAllInOne = async (videoId) => {
  const requestBody = {
    video_id: videoId,
  };

  try {
    const response = await fetch("/api/youtube/all-in-one/process", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(requestBody),
    });

    const result = await response.json();

    if (result.success) {
      console.log(
        `✅ Processing completed in ${result.processing_time_seconds}s`
      );
      console.log(
        `📊 Results: ${result.completed_tasks}/${result.total_tasks} tasks successful`
      );

      // Handle individual results
      if (result.results.titles?.success) {
        console.log(
          "📝 Generated titles:",
          result.results.titles.generated_titles
        );
      }

      if (result.results.description?.success) {
        console.log(
          "📄 Generated description:",
          result.results.description.generated_description
        );
      }

      if (result.results.timestamps?.success) {
        console.log(
          "⏰ Generated timestamps:",
          result.results.timestamps.generated_timestamps
        );
      }

      if (result.results.thumbnails?.success) {
        console.log(
          "🖼️ Generated thumbnails:",
          result.results.thumbnails.generated_thumbnails
        );
      }
    } else {
      console.error("❌ Processing failed:", result.message);
      console.error("Errors:", result.errors);
    }

    return result;
  } catch (error) {
    console.error("❌ API call failed:", error);
    throw error;
  }
};

// Usage
processVideoAllInOne("dQw4w9WgXcQ");
```

### Python Example

```python
import requests
import json

def process_video_all_in_one(video_id, token):
    url = "http://localhost:8000/api/youtube/all-in-one/process"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    request_body = {
        "video_id": video_id,
    }

    try:
        response = requests.post(url, headers=headers, json=request_body)
        result = response.json()

        if result["success"]:
            print(f"✅ Processing completed in {result['processing_time_seconds']}s")
            print(f"📊 Results: {result['completed_tasks']}/{result['total_tasks']} tasks successful")

            # Handle results
            for task_name, task_result in result["results"].items():
                if task_result["success"]:
                    print(f"✅ {task_name.title()}: {task_result['message']}")
                else:
                    print(f"❌ {task_name.title()}: {task_result['message']}")
        else:
            print(f"❌ Processing failed: {result['message']}")
            if result["errors"]:
                print("Errors:", result["errors"])

        return result
    except Exception as e:
        print(f"❌ API call failed: {e}")
        raise

# Usage
result = process_video_all_in_one("dQw4w9WgXcQ", "your_jwt_token")
```

## ⚠️ Error Handling

The API provides comprehensive error handling:

- **Individual Task Failures**: If one task fails, others continue processing
- **Partial Success**: You'll get results for successful tasks even if some fail
- **Detailed Error Messages**: Each failed task includes specific error information
- **Overall Status**: The main `success` field indicates if ALL tasks completed successfully

### Error Response Example

```json
{
  "success": false,
  "message": "All-in-one processing completed: 3/4 tasks successful, 1 failed",
  "video_id": "dQw4w9WgXcQ",
  "total_tasks": 4,
  "completed_tasks": 3,
  "failed_tasks": 1,
  "processing_time_seconds": 42.15,
  "errors": ["Thumbnails generation failed: API key not configured"],
  "results": {
    "titles": {
      "success": true,
      "message": "Titles generated successfully",
      "generated_titles": ["Title 1", "Title 2", "Title 3"]
    },
    "description": {
      "success": true,
      "message": "Description generated successfully",
      "generated_description": "Generated description..."
    },
    "timestamps": {
      "success": true,
      "message": "Timestamps generated successfully",
      "generated_timestamps": [{ "time": "0:00", "title": "Intro" }]
    },
    "thumbnails": {
      "success": false,
      "message": "Thumbnails generation failed: API key not configured",
      "error": "Thumbnails generation failed: API key not configured"
    }
  }
}
```

## 🔄 Processing Flow

1. **Request Validation**: Validate video ID and options
2. **Task Counting**: Count total tasks to be processed
3. **Parallel Processing**: Execute all enabled generation tasks
4. **Error Collection**: Collect any errors without stopping other tasks
5. **Result Compilation**: Compile all results into structured response
6. **Performance Metrics**: Calculate processing time and success rates

## 🚀 Performance

- **Efficient Processing**: Tasks run concurrently where possible
- **Timeout Handling**: Individual task timeouts don't affect others
- **Resource Management**: Proper cleanup and error handling
- **Progress Tracking**: Real-time logging of task completion

## 📊 Use Cases

- **Content Creator Workflow**: Generate all content for a video in one step
- **Batch Processing**: Process multiple videos efficiently
- **Content Optimization**: Get all optimization tools in one API call
- **Time Saving**: Eliminate multiple API calls and waiting periods

---

**Note**: This module requires proper setup of all individual generation services (title, description, timestamps, thumbnails) and their respective API keys for full functionality.
