#!/usr/bin/env python3
"""
Test script for the new playlist details API
"""

import requests
import json
from typing import Dict, Any

def test_playlist_details_api():
    """Test the playlist details API endpoint"""
    
    # Configuration
    base_url = "http://localhost:8000"  # Adjust if your server runs on different port
    playlist_id = "PLrAXtmRdnEQy6nuLMOV8u4fOqR0U4vO3p"  # Example playlist ID
    
    # You'll need to get a valid Bearer token from your authentication system
    # For testing, you can get this from your login endpoint
    bearer_token = "YOUR_BEARER_TOKEN_HERE"  # Replace with actual token
    
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    
    # Test the new playlist details endpoint
    endpoint = f"{base_url}/playlists/{playlist_id}"
    
    print(f"Testing playlist details API: {endpoint}")
    print(f"Playlist ID: {playlist_id}")
    print("-" * 50)
    
    try:
        response = requests.get(endpoint, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Playlist details retrieved:")
            print(json.dumps(data, indent=2))
            
            # Validate response structure
            if data.get("success") and data.get("data"):
                playlist_data = data["data"]
                print("\n📊 Playlist Information:")
                print(f"  - ID: {playlist_data.get('playlist_id')}")
                print(f"  - Name: {playlist_data.get('playlist_name')}")
                print(f"  - Description: {playlist_data.get('description', 'N/A')[:100]}...")
                print(f"  - Video Count: {playlist_data.get('video_count')}")
                print(f"  - Channel: {playlist_data.get('channel_title')}")
                print(f"  - Privacy: {playlist_data.get('privacy_status')}")
                
                # Display analytics
                analytics = playlist_data.get('analytics')
                if analytics:
                    print(f"\n📊 Playlist Analytics:")
                    print(f"  - Total Views: {analytics.get('total_views', 0):,}")
                    print(f"  - Total Likes: {analytics.get('total_likes', 0):,}")
                    print(f"  - Total Comments: {analytics.get('total_comments', 0):,}")
                    print(f"  - Average Engagement Rate: {analytics.get('average_engagement_rate', 0):.4f}")
                    print(f"  - Top Video by Views: {analytics.get('top_video_by_views_title', 'N/A')} ({analytics.get('top_video_by_views_count', 0):,} views)")
                    print(f"  - Top Video by Likes: {analytics.get('top_video_by_likes_title', 'N/A')} ({analytics.get('top_video_by_likes_count', 0):,} likes)")
                    print(f"  - Last Analytics Update: {analytics.get('last_analytics_update', 'N/A')}")
                
                top_videos = playlist_data.get('top_videos', [])
                print(f"\n🎥 Top 2 Videos in Playlist ({len(top_videos)}):")
                for i, video in enumerate(top_videos):
                    performance_type = video.get('performance_type', 'N/A')
                    print(f"  {i+1}. {video.get('title', 'N/A')}")
                    print(f"     - Performance Type: {performance_type}")
                    print(f"     - Views: {video.get('view_count', 0):,}")
                    print(f"     - Likes: {video.get('like_count', 0):,}")
                    print(f"     - Comments: {video.get('comment_count', 0):,}")
                    print(f"     - Duration: {video.get('duration', 'N/A')}")
                    print(f"     - Published: {video.get('published_at', 'N/A')}")
                    print()
                    
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the server is running on the correct port")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_playlist_all_videos_api():
    """Test the new playlist all videos API"""
    
    base_url = "http://localhost:8000"
    playlist_id = "PLrAXtmRdnEQy6nuLMOV8u4fOqR0U4vO3p"  # Example playlist ID
    bearer_token = "YOUR_BEARER_TOKEN_HERE"  # Replace with actual token
    
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    
    endpoint = f"{base_url}/playlists/{playlist_id}/videos?refresh=false"
    
    print(f"Testing playlist all videos API: {endpoint}")
    print(f"Playlist ID: {playlist_id}")
    print("-" * 50)
    
    try:
        response = requests.get(endpoint, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! All playlist videos retrieved:")
            
            # Validate response structure
            if data.get("success") and data.get("data"):
                playlist_data = data["data"]
                print(f"\n📋 Playlist Information:")
                print(f"  - ID: {playlist_data.get('playlist_id')}")
                print(f"  - Name: {playlist_data.get('playlist_name')}")
                print(f"  - Total Videos: {playlist_data.get('total_videos')}")
                
                videos = playlist_data.get('videos', [])
                print(f"\n🎥 All Videos in Playlist ({len(videos)}):")
                
                # Show first 5 videos with details
                for i, video in enumerate(videos[:5]):
                    print(f"  {i+1}. {video.get('title', 'N/A')}")
                    print(f"     - Video ID: {video.get('video_id', 'N/A')}")
                    print(f"     - Views: {video.get('view_count', 0):,}")
                    print(f"     - Likes: {video.get('like_count', 0):,}")
                    print(f"     - Comments: {video.get('comment_count', 0):,}")
                    print(f"     - Duration: {video.get('duration', 'N/A')}")
                    print(f"     - Privacy: {video.get('privacy_status', 'N/A')}")
                    if video.get('watch_time_minutes'):
                        print(f"     - Watch Time: {video.get('watch_time_minutes'):.2f} minutes")
                    print(f"     - Published: {video.get('published_at', 'N/A')}")
                    print(f"     - URL: {video.get('youtube_video_url', 'N/A')}")
                    print()
                
                if len(videos) > 5:
                    print(f"  ... and {len(videos) - 5} more videos")
                    
                print(f"\n💾 Data Storage:")
                print(f"  - All {len(videos)} videos stored in 'single_video_details' table")
                print(f"  - Each video includes complete analytics and metadata")
                    
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the server is running on the correct port")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_playlist_list_api():
    """Test the existing playlist list API for comparison"""
    
    base_url = "http://localhost:8000"
    bearer_token = "YOUR_BEARER_TOKEN_HERE"  # Replace with actual token
    
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    
    endpoint = f"{base_url}/playlists/"
    
    print(f"\nTesting playlist list API: {endpoint}")
    print("-" * 50)
    
    try:
        response = requests.get(endpoint, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Playlist list retrieved successfully")
            
            if data.get("success") and data.get("data", {}).get("playlists"):
                playlists = data["data"]["playlists"]
                print(f"📋 Found {len(playlists)} playlists:")
                for i, playlist in enumerate(playlists[:5]):  # Show first 5
                    print(f"  {i+1}. {playlist.get('playlist_name')} (ID: {playlist.get('playlist_id')})")
                
                if len(playlists) > 5:
                    print(f"  ... and {len(playlists) - 5} more playlists")
                    
                # Suggest testing with the first playlist
                if playlists:
                    first_playlist_id = playlists[0].get('playlist_id')
                    print(f"\n💡 You can test the details API with this playlist ID: {first_playlist_id}")
                    print(f"   Endpoint: {base_url}/playlists/{first_playlist_id}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🧪 Testing Playlist Details API")
    print("=" * 60)
    
    print("\n1. Testing Playlist List API (to get available playlists):")
    test_playlist_list_api()
    
    print("\n2. Testing Playlist Details API (top 2 videos + analytics):")
    test_playlist_details_api()
    
    print("\n3. Testing Playlist All Videos API (complete video list):")
    test_playlist_all_videos_api()
    
    print("\n" + "=" * 60)
    print("📝 Instructions:")
    print("1. Make sure your server is running (python run.py)")
    print("2. Replace 'YOUR_BEARER_TOKEN_HERE' with a valid Bearer token")
    print("3. Update the playlist_id if needed")
    print("4. Run this script to test the API endpoints")
    print("\n💾 Data Storage:")
    print("- All video details are stored in 'single_video_details' table")
    print("- Playlist analytics are stored in 'user_playlist' table")
    print("- Each API call updates the database with fresh data")
    print("\n🔗 Available Endpoints:")
    print("- GET /playlists/ - List all playlists")
    print("- GET /playlists/{playlist_id} - Get playlist details (top 2 videos + analytics)")
    print("- GET /playlists/{playlist_id}/videos - Get all videos in playlist")
    print("\n🔄 Refresh Parameter:")
    print("- ?refresh=false (default) - Return cached data from database (faster)")
    print("- ?refresh=true - Always fetch fresh data from YouTube API")
