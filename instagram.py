from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from urllib.parse import urlencode
import requests
import os

app = FastAPI()

BASE_URL = "https://www.instagram.com/oauth/authorize"
TOKEN_URL = "https://api.instagram.com/oauth/access_token"

# In-memory "DB" to store codes and tokens
db_codes = []
db_tokens = {}

# Current redirect URI (can be updated)
CURRENT_REDIRECT_URI = "https://6e36fc3a9566.ngrok-free.app/callback"

# Store the exact redirect URI used in OAuth requests
oauth_redirect_uri = None

# Store the exact OAuth URL parameters for debugging
oauth_params = None

@app.get("/generate_instagram_url")
def generate_instagram_url(
    client_id: str = Query("25151268451125305", description="Your Instagram Client ID"),
    redirect_uri: str = Query("https://6e36fc3a9566.ngrok-free.app/callback", description="Redirect URI after consent"),
):
    # Use redirect URI exactly as provided (no normalization)
    print(f"Using redirect_uri: {redirect_uri}")
    
    # Store the exact redirect URI and parameters used in OAuth request
    global oauth_redirect_uri, oauth_params
    oauth_redirect_uri = redirect_uri
    
    # Define essential parameters for Instagram OAuth
    params = {
        "force_reauth": "true",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "instagram_business_basic,instagram_business_manage_messages,instagram_business_manage_comments,instagram_business_content_publish,instagram_business_manage_insights"
    }
    
    # Store the exact parameters for debugging
    oauth_params = params.copy()

    url = f"{BASE_URL}?{urlencode(params)}"
    return JSONResponse({
        "consent_url": url,
        "redirect_uri_used": redirect_uri,
        "debug_info": {
            "client_id": client_id,
            "redirect_uri": redirect_uri
        }
    })

@app.get("/callback")
async def callback(code: str = Query(..., description="OAuth code from Instagram")):
    # Store code in our in-memory "DB"
    db_codes.append(code)
    print("Received OAuth code:", code)

    # Exchange code for access token
    client_secret = os.getenv("INSTAGRAM_CLIENT_SECRET", "aeeb6a5532bef258de1d5ab6f5bf3583")
    
    # Use the exact same redirect URI that was used in the OAuth request
    global oauth_redirect_uri, oauth_params
    redirect_uri = oauth_redirect_uri if oauth_redirect_uri else CURRENT_REDIRECT_URI
    
    print(f"Using redirect_uri for token exchange: {redirect_uri}")
    print(f"OAuth request redirect_uri: {oauth_redirect_uri}")
    print(f"OAuth params: {oauth_params}")
    print(f"Are they identical? {redirect_uri == oauth_redirect_uri}")
    print(f"URL encoded redirect_uri: {urlencode({'redirect_uri': redirect_uri})}")
    
    # Try using the exact same parameters as the OAuth request
    if oauth_params:
        print(f"Using stored OAuth params for token exchange")
        token_data = {
            "client_id": oauth_params["client_id"],
            "client_secret": client_secret,
            "grant_type": "authorization_code",
            "redirect_uri": oauth_params["redirect_uri"],
            "code": code
        }
    else:
        print(f"Using fallback parameters for token exchange")
        token_data = {
            "client_id": "25151268451125305",
            "client_secret": client_secret,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
            "code": code
        }

    try:
        print(f"Exchanging code for token with data: {token_data}")
        response = requests.post(TOKEN_URL, data=token_data)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response content: {response.text}")
        
        if response.status_code != 200:
            return JSONResponse({
                "error": "Failed to exchange code for tokens",
                "status_code": response.status_code,
                "response": response.text
            }, status_code=400)
            
        token_info = response.json()
        
        # Store tokens in our in-memory "DB"
        db_tokens[code] = token_info

        return JSONResponse({
            "message": "Code exchanged for tokens successfully!",
            "access_token": token_info.get("access_token"),
            "user_id": token_info.get("user_id")
        })

    except requests.exceptions.RequestException as e:
        print(f"Request exception: {str(e)}")
        return JSONResponse({
            "error": "Failed to exchange code for tokens",
            "details": str(e)
        }, status_code=400)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return JSONResponse({
            "error": "Unexpected error occurred",
            "details": str(e)
        }, status_code=500)

@app.get("/tokens")
def get_tokens():
    """Get all stored tokens (for debugging)"""
    return JSONResponse({
        "codes": db_codes,
        "tokens": db_tokens
    })

@app.get("/clear_tokens")
def clear_tokens():
    """Clear all stored tokens (for debugging)"""
    global db_codes, db_tokens
    db_codes.clear()
    db_tokens.clear()
    return JSONResponse({"message": "All tokens cleared"})

@app.get("/config")
def get_config():
    """Get current configuration"""
    client_secret = os.getenv("INSTAGRAM_CLIENT_SECRET", "aeeb6a5532bef258de1d5ab6f5bf3583")
    return JSONResponse({
        "current_redirect_uri": CURRENT_REDIRECT_URI,
        "client_id": "25151268451125305",
        "client_secret_length": len(client_secret),
        "client_secret_starts_with": client_secret[:8] + "...",
        "token_url": TOKEN_URL,
        "base_url": BASE_URL
    })

@app.post("/update_redirect_uri")
def update_redirect_uri(new_uri: str):
    """Update the redirect URI (useful when ngrok URL changes)"""
    global CURRENT_REDIRECT_URI
    CURRENT_REDIRECT_URI = new_uri
    return JSONResponse({
        "message": "Redirect URI updated",
        "new_redirect_uri": CURRENT_REDIRECT_URI
    })

@app.post("/update_client_secret")
def update_client_secret(new_secret: str):
    """Update the client secret"""
    # Set environment variable for this session
    os.environ["INSTAGRAM_CLIENT_SECRET"] = new_secret
    return JSONResponse({
        "message": "Client secret updated",
        "new_secret_length": len(new_secret),
        "new_secret_starts_with": new_secret[:8] + "..."
    })

@app.get("/debug_urls")
def debug_urls():
    """Debug endpoint to compare OAuth and token exchange URLs"""
    return JSONResponse({
        "stored_oauth_redirect_uri": oauth_redirect_uri,
        "stored_oauth_params": oauth_params,
        "current_redirect_uri": CURRENT_REDIRECT_URI,
        "token_exchange_redirect_uri": oauth_redirect_uri if oauth_redirect_uri else CURRENT_REDIRECT_URI,
        "comparison": {
            "oauth_redirect_uri": oauth_redirect_uri,
            "token_redirect_uri": oauth_redirect_uri if oauth_redirect_uri else CURRENT_REDIRECT_URI,
            "are_identical": oauth_redirect_uri == (oauth_redirect_uri if oauth_redirect_uri else CURRENT_REDIRECT_URI),
            "oauth_url_encoded": urlencode({"redirect_uri": oauth_redirect_uri}) if oauth_redirect_uri else None
        }
    })

@app.get("/")
def root():
    """Root endpoint with basic info"""
    return JSONResponse({
        "message": "Instagram OAuth API",
        "current_redirect_uri": CURRENT_REDIRECT_URI,
        "endpoints": {
            "generate_url": "/generate_instagram_url",
            "callback": "/callback",
            "tokens": "/tokens",
            "clear_tokens": "/clear_tokens",
            "config": "/config",
            "update_redirect": "/update_redirect_uri",
            "debug_urls": "/debug_urls",
            "docs": "/docs"
        }
    })
