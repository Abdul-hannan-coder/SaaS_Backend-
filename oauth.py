PROVIDER = "linkedin"
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import json
import os
import uvicorn

app = FastAPI()

NANGO_API_URL = "https://api.nango.dev"
NANGO_SECRET_KEY = "87a446ef-12a5-41df-b24e-2102bcb29161"   # replace with regenerated secret


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post("/create-session")
async def create_session(user_id: str):
    """
    Create a Nango session token for the user.
    This token will be used on frontend to start OAuth.
    """
    payload = {
        "end_user": {"id": user_id},  # unique per user in your DB
        "allowed_integrations": ["linkedin"]
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{NANGO_API_URL}/v1/session-token",
            headers={"Authorization": f"Bearer {NANGO_SECRET_KEY}"},
            json=payload
        )

    return JSONResponse(resp.json())


@app.get("/fetch-token/{user_id}")
async def fetch_token(user_id: str):
    """
    Fetch the OAuth credentials for this user from Nango.
    """
    connection_id = user_id  # Nango uses end_user.id as connection_id

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{NANGO_API_URL}/v1/connection/{connection_id}",
            headers={"Authorization": f"Bearer {NANGO_SECRET_KEY}"}
        )

    token_data = resp.json()

    # Save token locally
    with open(f"{user_id}_linkedin_token.json", "w") as f:
        json.dump(token_data, f, indent=4)

    return token_data


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)