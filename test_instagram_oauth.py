#!/usr/bin/env python3
"""
Test script for Instagram OAuth flow
This script helps debug the redirect URI issue
"""

import requests
import json

# Your local server
BASE_URL = "http://127.0.0.1:8000"

def test_oauth_flow():
    print("🔍 Testing Instagram OAuth Flow")
    print("=" * 50)
    
    # Step 1: Get the OAuth URL
    print("1. Getting OAuth URL...")
    response = requests.get(f"{BASE_URL}/generate_instagram_url")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ OAuth URL generated successfully")
        print(f"📋 Redirect URI used: {data.get('redirect_uri_used')}")
        print(f"🔗 Consent URL: {data.get('consent_url')}")
        print(f"🔧 Debug info: {json.dumps(data.get('debug_info'), indent=2)}")
        
        # Step 2: Check current config
        print("\n2. Checking current configuration...")
        config_response = requests.get(f"{BASE_URL}/config")
        if config_response.status_code == 200:
            config = config_response.json()
            print(f"📊 Current redirect URI: {config.get('current_redirect_uri')}")
            print(f"🆔 Client ID: {config.get('client_id')}")
        
        print("\n" + "=" * 50)
        print("🚨 IMPORTANT: Make sure your Instagram app settings match!")
        print(f"   Redirect URI in Instagram app: {data.get('redirect_uri_used')}")
        print("=" * 50)
        
        return data.get('consent_url')
    else:
        print(f"❌ Failed to get OAuth URL: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def check_tokens():
    print("\n3. Checking stored tokens...")
    response = requests.get(f"{BASE_URL}/tokens")
    if response.status_code == 200:
        tokens = response.json()
        print(f"📦 Stored codes: {len(tokens.get('codes', []))}")
        print(f"🔑 Stored tokens: {len(tokens.get('tokens', {}))}")
        if tokens.get('tokens'):
            print("🎉 Tokens found!")
            for code, token_info in tokens.get('tokens', {}).items():
                print(f"   Code: {code[:20]}...")
                print(f"   Access Token: {token_info.get('access_token', 'N/A')[:20]}...")
                print(f"   User ID: {token_info.get('user_id', 'N/A')}")
    else:
        print(f"❌ Failed to get tokens: {response.status_code}")

def update_redirect_uri(new_uri):
    print(f"\n4. Updating redirect URI to: {new_uri}")
    response = requests.post(f"{BASE_URL}/update_redirect_uri", params={"new_uri": new_uri})
    if response.status_code == 200:
        print(f"✅ Redirect URI updated: {response.json()}")
    else:
        print(f"❌ Failed to update redirect URI: {response.status_code}")

if __name__ == "__main__":
    print("🚀 Instagram OAuth Test Script")
    print("Make sure your server is running: uvicorn instagram:app --reload")
    print()
    
    # Test the OAuth flow
    oauth_url = test_oauth_flow()
    
    if oauth_url:
        print(f"\n🌐 Open this URL in your browser:")
        print(f"   {oauth_url}")
        print("\nAfter completing OAuth, run this script again to check tokens.")
    
    # Check current tokens
    check_tokens()
    
    print("\n" + "=" * 50)
    print("💡 TROUBLESHOOTING TIPS:")
    print("1. Make sure your Instagram app redirect URI matches exactly")
    print("2. Check that ngrok is running and the URL is accessible")
    print("3. Verify your client ID and secret are correct")
    print("4. Try clearing tokens and starting fresh: GET /clear_tokens")
    print("=" * 50)


