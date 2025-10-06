from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from urllib.parse import urlencode

app = FastAPI()

BASE_URL = "https://web.facebook.com/privacy/consent/gdp/"

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from urllib.parse import urlencode
# In-memory "DB" to store codes
db_codes = []

app = FastAPI()

BASE_URL = "https://web.facebook.com/privacy/consent/gdp/"

@app.get("/generate_fb_url")
def generate_fb_url(
    app_id: str = Query("1136209781299705", description="Your Facebook App ID"),
    redirect_uri: str = Query("http://localhost:8000/callback", description="Redirect URI after consent"),
    state: str = Query("secure_random_state_123", description="Security token to prevent CSRF"),
):
    # Define essential parameters only with simplified scope
    params = {
        "app_id": app_id,
        "redirect_uri": redirect_uri,
        "scope": "email,public_profile",  # simplified scopes
        "state": state
    }

    url = f"{BASE_URL}?{urlencode(params)}"
    return JSONResponse({"consent_url": url})

@app.get("/callback")
def callback(code: str = Query(..., description="OAuth code from Facebook")):
    # Store code in our in-memory "DB"
    db_codes.append(code)
    print("Received OAuth code:", code)  # prints to console
    return JSONResponse({
        "message": "Code received and stored!",
        "stored_codes": db_codes
    })
