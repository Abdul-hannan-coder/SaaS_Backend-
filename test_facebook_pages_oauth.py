#!/usr/bin/env python3
"""
Test script for Facebook Pages OAuth flow
This script helps debug the Facebook Pages OAuth process
"""

import requests
import json

# Your local server
BASE_URL = "http://127.0.0.1:8001"  # Different port for Facebook Pages

def test_oauth_flow():
    print("🔍 Testing Facebook Pages OAuth Flow")
    print("=" * 50)
    
    # Step 1: Get the OAuth URL
    print("1. Getting OAuth URL...")
    response = requests.get(f"{BASE_URL}/generate_facebook_url")
    
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
            print(f"🔑 Client Secret: {config.get('client_secret_starts_with')}")
        
        print("\n" + "=" * 50)
        print("🚨 IMPORTANT: Make sure your Facebook app settings match!")
        print(f"   Redirect URI in Facebook app: {data.get('redirect_uri_used')}")
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
        print(f"📄 Stored pages: {len(tokens.get('pages', {}))}")
        if tokens.get('tokens'):
            print("🎉 Tokens found!")
            for code, token_info in tokens.get('tokens', {}).items():
                print(f"   Code: {code[:20]}...")
                print(f"   Access Token: {token_info.get('access_token', 'N/A')[:20]}...")
                print(f"   User ID: {token_info.get('user_id', 'N/A')}")
        if tokens.get('pages'):
            print("📄 Pages found!")
            for code, pages in tokens.get('pages', {}).items():
                print(f"   Code: {code[:20]}...")
                print(f"   Pages: {len(pages)} pages")
                for page in pages:
                    print(f"     - {page.get('name', 'Unknown')} (ID: {page.get('id', 'Unknown')})")
    else:
        print(f"❌ Failed to get tokens: {response.status_code}")

def update_client_secret(new_secret):
    print(f"\n4. Updating client secret...")
    response = requests.post(f"{BASE_URL}/update_client_secret", params={"new_secret": new_secret})
    if response.status_code == 200:
        print(f"✅ Client secret updated: {response.json()}")
    else:
        print(f"❌ Failed to update client secret: {response.status_code}")

def test_pages_endpoint(code):
    print(f"\n5. Testing pages endpoint for code: {code[:20]}...")
    response = requests.get(f"{BASE_URL}/pages/{code}")
    if response.status_code == 200:
        pages_data = response.json()
        print(f"✅ Pages retrieved: {pages_data.get('pages_count', 0)} pages")
        for page in pages_data.get('pages', []):
            print(f"   - {page.get('name', 'Unknown')} (ID: {page.get('id', 'Unknown')})")
    else:
        print(f"❌ Failed to get pages: {response.status_code}")

if __name__ == "__main__":
    print("🚀 Facebook Pages OAuth Test Script")
    print("Make sure your server is running: uvicorn facebook_pages:app --reload --port 8001")
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
    print("1. Make sure your Facebook app redirect URI matches exactly")
    print("2. Check that ngrok is running and the URL is accessible")
    print("3. Verify your Facebook App ID and secret are correct")
    print("4. Try clearing tokens and starting fresh: GET /clear_tokens")
    print("5. Update client secret if needed: POST /update_client_secret")
    print("=" * 50)


