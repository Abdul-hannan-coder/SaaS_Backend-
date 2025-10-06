#!/usr/bin/env python3
"""
Test script for All-in-One video processing functionality
"""
import asyncio
import sys
import os
import time

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.modules.youtube.all_in_one.service import process_video_all_in_one
from app.modules.youtube.all_in_one.model import AllInOneRequest
from app.utils.database_dependency import get_database_session
from sqlmodel import Session
from uuid import UUID

async def test_all_in_one_processing():
    """Test the all-in-one video processing service"""
    
    print("🚀 Testing All-in-One Video Processing Service")
    print("=" * 60)
    
    # Test data
    test_video_id = "dQw4w9WgXcQ"  # Example YouTube video ID
    test_user_id = UUID("12345678-1234-5678-9012-123456789012")  # Example user ID
    
    # Get database session
    db = next(get_database_session())
    
    try:
        print(f"🎥 Video ID: {test_video_id}")
        print(f"👤 User ID: {test_user_id}")
        print()
        
        # Test 1: Full processing (all features enabled)
        print("🧪 Test 1: Full Processing (All Features)")
        print("-" * 40)
        
        request = AllInOneRequest(
            video_id=test_video_id
        )
        
        start_time = time.time()
        result = await process_video_all_in_one(request, test_user_id, db)
        end_time = time.time()
        
        print(f"⏱️ Processing Time: {end_time - start_time:.2f} seconds")
        print(f"✅ Overall Success: {result.success}")
        print(f"📊 Tasks: {result.completed_tasks}/{result.total_tasks} completed")
        print(f"❌ Failed Tasks: {result.failed_tasks}")
        print(f"📝 Message: {result.message}")
        print()
        
        # Display individual results
        print("📋 Individual Results:")
        for task_name, task_result in result.results.items():
            status = "✅" if task_result.success else "❌"
            print(f"  {status} {task_name.title()}: {task_result.message}")
            
            if hasattr(task_result, 'generated_titles') and task_result.generated_titles:
                print(f"    📝 Generated {len(task_result.generated_titles)} titles")
            elif hasattr(task_result, 'generated_description') and task_result.generated_description:
                print(f"    📄 Generated description ({len(task_result.generated_description)} chars)")
            elif hasattr(task_result, 'generated_timestamps') and task_result.generated_timestamps:
                print(f"    ⏰ Generated {len(task_result.generated_timestamps)} timestamps")
            elif hasattr(task_result, 'generated_thumbnails') and task_result.generated_thumbnails:
                print(f"    🖼️ Generated {len(task_result.generated_thumbnails)} thumbnails")
        print()
        
        # Test 2: Different video ID
        print("🧪 Test 2: Different Video ID")
        print("-" * 30)
        
        request_partial = AllInOneRequest(
            video_id="test_video_2"
        )
        
        start_time = time.time()
        result_partial = await process_video_all_in_one(request_partial, test_user_id, db)
        end_time = time.time()
        
        print(f"⏱️ Processing Time: {end_time - start_time:.2f} seconds")
        print(f"✅ Overall Success: {result_partial.success}")
        print(f"📊 Tasks: {result_partial.completed_tasks}/{result_partial.total_tasks} completed")
        print(f"📝 Message: {result_partial.message}")
        print()
        
        # Display partial results
        print("📋 Partial Results:")
        for task_name, task_result in result_partial.results.items():
            status = "✅" if task_result.success else "❌"
            print(f"  {status} {task_name.title()}: {task_result.message}")
        print()
        
        # Test 3: Error handling (invalid video ID)
        print("🧪 Test 3: Error Handling (Invalid Video ID)")
        print("-" * 45)
        
        request_error = AllInOneRequest(
            video_id="invalid_video_id"
        )
        
        start_time = time.time()
        result_error = await process_video_all_in_one(request_error, test_user_id, db)
        end_time = time.time()
        
        print(f"⏱️ Processing Time: {end_time - start_time:.2f} seconds")
        print(f"✅ Overall Success: {result_error.success}")
        print(f"📊 Tasks: {result_error.completed_tasks}/{result_error.total_tasks} completed")
        print(f"❌ Failed Tasks: {result_error.failed_tasks}")
        print(f"📝 Message: {result_error.message}")
        
        if result_error.errors:
            print("🚨 Errors:")
            for error in result_error.errors:
                print(f"  ❌ {error}")
        print()
        
        # Summary
        print("📊 Test Summary:")
        print(f"  🧪 Total Tests: 3")
        print(f"  ✅ Full Processing: {'PASS' if result.success else 'FAIL'}")
        print(f"  ✅ Partial Processing: {'PASS' if result_partial.success else 'FAIL'}")
        print(f"  ✅ Error Handling: {'PASS' if not result_error.success else 'FAIL'}")
        
    except Exception as e:
        print(f"❌ Error testing all-in-one processing: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starting All-in-One Video Processing Test")
    asyncio.run(test_all_in_one_processing())
    print("\n✨ Test completed!")
