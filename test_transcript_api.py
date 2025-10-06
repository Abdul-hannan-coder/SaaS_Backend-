#!/usr/bin/env python3
"""
Test script for YouTube Transcript API functionality
"""

def test_youtube_transcript_api():
    """Test if youtube-transcript-api is working correctly"""
    
    print("🔍 Testing YouTube Transcript API...")
    
    # Test 1: Import check
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        print("✅ Successfully imported YouTubeTranscriptApi")
        
        # Check available methods
        methods = [method for method in dir(YouTubeTranscriptApi) if not method.startswith('_')]
        print(f"📋 Available methods: {methods}")
        
        # Check method signatures
        import inspect
        try:
            fetch_signature = inspect.signature(YouTubeTranscriptApi.fetch)
            print(f"🔍 fetch method signature: {fetch_signature}")
        except Exception as e:
            print(f"Could not get fetch signature: {e}")
            
        try:
            list_signature = inspect.signature(YouTubeTranscriptApi.list)
            print(f"🔍 list method signature: {list_signature}")
        except Exception as e:
            print(f"Could not get list signature: {e}")
        
    except ImportError as e:
        print(f"❌ Failed to import YouTubeTranscriptApi: {e}")
        return False
    
    # Test 2: Check if fetch method exists
    if hasattr(YouTubeTranscriptApi, 'fetch'):
        print("✅ fetch method exists")
    else:
        print("❌ fetch method not found")
        return False
    
    # Test 3: Try to fetch transcript for a known video with transcript
    test_video_id = "ngYXsg4z8K8"  # Your test video
    
    try:
        print(f"🎬 Testing transcript fetch for video: {test_video_id}")
        api = YouTubeTranscriptApi()
        transcript = api.fetch(test_video_id)
        
        if transcript:
            print(f"✅ Successfully fetched transcript! Found {len(transcript)} segments")
            
            # Show first few segments
            print("📝 First 3 segments:")
            for i, segment in enumerate(transcript[:3]):
                print(f"  {i+1}. [{segment.get('start', 0):.1f}s] {segment.get('text', '')}")
                
            return True
        else:
            print("⚠️ Transcript fetch returned empty result")
            return False
            
    except Exception as e:
        print(f"❌ Error fetching transcript: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # Try alternative video IDs that are known to have transcripts
        alternative_videos = [
            "dQw4w9WgXcQ",  # Rick Roll (popular video, likely has transcript)
            "jNQXAC9IVRw",  # "Me at the zoo" (first YouTube video)
        ]
        
        for alt_video in alternative_videos:
            try:
                print(f"🔄 Trying alternative video: {alt_video}")
                api = YouTubeTranscriptApi()
                alt_transcript = api.fetch(alt_video)
                if alt_transcript:
                    print(f"✅ Alternative video worked! Found {len(alt_transcript)} segments")
                    print("📝 First segment:", alt_transcript[0] if alt_transcript else "None")
                    return True
            except Exception as alt_e:
                print(f"❌ Alternative video {alt_video} also failed: {alt_e}")
                continue
        
        return False

def test_transcript_formatting():
    """Test the transcript formatting logic"""
    
    print("\n🔧 Testing transcript formatting...")
    
    # Mock transcript data (similar to what YouTube API returns)
    mock_transcript = [
        {'start': 0.0, 'duration': 3.5, 'text': 'Hello and welcome to this video'},
        {'start': 3.5, 'duration': 2.8, 'text': 'Today we are going to talk about'},
        {'start': 6.3, 'duration': 4.2, 'text': 'the amazing features of this device'},
        {'start': 65.7, 'duration': 3.1, 'text': 'After one minute and five seconds'},
    ]
    
    # Test formatting logic
    try:
        segments = []
        for entry in mock_transcript:
            # Convert seconds to MM:SS format
            start_time = entry['start']
            minutes = int(start_time // 60)
            seconds = int(start_time % 60)
            timestamp = f"{minutes:02d}:{seconds:02d}"
            
            segments.append({
                "timestamp": timestamp,
                "text": entry['text'].strip()
            })
        
        print("✅ Transcript formatting successful!")
        print("📝 Formatted segments:")
        for segment in segments:
            print(f"  [{segment['timestamp']}] {segment['text']}")
            
        # Test JSON serialization
        import json
        transcript_data = {
            "segments": segments,
            "source": "youtube",
            "fetched_at": "2025-09-29T13:00:00"
        }
        
        json_str = json.dumps(transcript_data)
        print(f"✅ JSON serialization successful! Length: {len(json_str)} chars")
        
        return True
        
    except Exception as e:
        print(f"❌ Transcript formatting failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting YouTube Transcript API Tests\n")
    
    # Test 1: API functionality
    api_test_passed = test_youtube_transcript_api()
    
    # Test 2: Formatting logic
    format_test_passed = test_transcript_formatting()
    
    print(f"\n📊 Test Results:")
    print(f"   API Test: {'✅ PASSED' if api_test_passed else '❌ FAILED'}")
    print(f"   Format Test: {'✅ PASSED' if format_test_passed else '❌ FAILED'}")
    
    if api_test_passed and format_test_passed:
        print("🎉 All tests passed! YouTube Transcript API is ready to use.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
