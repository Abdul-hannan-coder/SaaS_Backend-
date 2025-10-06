#!/usr/bin/env python3
"""
Entry point for the Data Migration Project
Run this from the project root directory
"""

from app import app
import uvicorn
from app.config.my_settings import settings

if __name__ == "__main__":
    uvicorn.run("run:app", host="0.0.0.0", port=settings.PORT, reload=True) 


 