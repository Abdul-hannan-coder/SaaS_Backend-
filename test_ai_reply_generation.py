#!/usr/bin/env python3
"""
Test script for AI reply generation functionality
"""
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.modules.youtube.comment.service import generate_ai_replies_service
from app.utils.database_dependency import get_database_session
from sqlmodel import Session
from uuid import UUID

async def test_ai_reply_generation():
    """Test the AI reply generation service"""
    
    print("🤖 Testing AI Reply Generation Service")
    print("=" * 50)
    
    # Test data
    test_comments = [
        {
            "comment_id": "test_comment_1",
            "comment_text": "Great video! Thanks for sharing this tutorial."
        },
        {
            "comment_id": "test_comment_2", 
            "comment_text": "Could you explain more about the advanced concepts?"
        },
        {
            "comment_id": "test_comment_3",
            "comment_text": "This was really helpful for my project!"
        }
    ]
    
    test_user_id = UUID("12345678-1234-5678-9012-123456789012")  # Example user ID
    
    # Get database session
    db = next(get_database_session())
    
    try:
        print(f"📝 Testing with comments: {test_comments}")
        print(f"👤 User ID: {test_user_id}")
        print()
        
        # Test AI reply generation
        result = await generate_ai_replies_service(
            comments=test_comments,
            user_id=test_user_id,
            db=db
        )
        
        print("✅ AI Reply Generation Result:")
        print(f"Success: {result.success}")
        print(f"Message: {result.message}")
        print(f"Total Generated: {result.total_generated}")
        print()
        
        if result.success and result.generated_replies:
            print("🤖 Generated Replies:")
            for i, reply in enumerate(result.generated_replies, 1):
                print(f"\n{i}. Comment: {reply.comment_text}")
                print(f"   Reply: {reply.generated_reply}")
                print(f"   Confidence: {reply.confidence}")
        else:
            print("❌ No replies were generated")
            
    except Exception as e:
        print(f"❌ Error testing AI reply generation: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starting AI Reply Generation Test")
    asyncio.run(test_ai_reply_generation())
    print("\n✨ Test completed!")
