from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel
from fastapi.middleware.cors import CORSMiddleware
from .config.database import (
    initialize_database_engine,
)
from .utils.my_logger import get_logger
from .config.my_settings import settings
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

# LIFESPAN
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    await startup_event(app)

    # This is where the app runs (yield)
    yield 

    # Shutdown event
    await shutdown_event(app)

# FASTAPI APP
app = FastAPI(
    version="0.1.0",
    lifespan=lifespan  
)

# GLOBAL ERROR HANDLERS
from .modules.youtube.helpers.error_handlers import register_error_handlers

# Register error handlers
register_error_handlers(app)

# CORS MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# STARTUP EVENT
async def startup_event(app: FastAPI):
    get_logger(name="UZAIR").info("🚀 Starting up Data Migration Project...")
    
    # Initialize and store in app.state
    app.state.database_engine = initialize_database_engine()
    
    # Create database tables
    try:        
        # Create all tables (including YouTube tables)
        SQLModel.metadata.create_all(app.state.database_engine)
        
        get_logger(name="UZAIR").info("✅ Database tables created successfully")
    except Exception as e:
        get_logger(name="UZAIR").error(f"❌ Error creating database tables: {e}")

# INCLUDE LOGIN ROUTERS
from .modules.login_logout.routes.user_routes import router as user_router
from .modules.google_login.routes.google_auth_routes import router as google_auth_router

# INCLUDE YouTube ROUTES
from .youtube_routes import register_youtube_routes

app.include_router(user_router)
app.include_router(google_auth_router)

# Register all YouTube routes
register_youtube_routes(app)

# MOUNT STATIC FILES
from pathlib import Path

# Create thumbnails directory if it doesn't exist
thumbnails_dir = Path("thumbnails")
thumbnails_dir.mkdir(exist_ok=True)

# Mount static files directories
app.mount("/videos", StaticFiles(directory="videos"), name="videos")
app.mount("/thumbnails", StaticFiles(directory="thumbnails"), name="thumbnails")

# ROOT REDIRECT TO DOCS
@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

# HEALTH CHECK
@app.get("/health")
async def health_check():
    return {"status": "The server is running successfully"}

# SHUTDOWN EVENT
async def shutdown_event(app: FastAPI):
    get_logger(name="UZAIR").info("🛑 Shutting down Data Migration Project...")
    
    # Cleanup - ClickHouse client doesn't need explicit closing
    # The client will be garbage collected automatically
    if hasattr(app.state, 'cartlow_clickhouse_prod_client'):
        get_logger(name="UZAIR").info("✅ ClickHouse client cleanup completed")
    if hasattr(app.state, 'cartlow_fantacy4_mysql_engine'):
        get_logger(name="UZAIR").info("✅ Cartlow Fantacy4 MySQL engine cleanup completed")
    if hasattr(app.state, 'cartlow_dev_mysql_engine'):
        get_logger(name="UZAIR").info("✅ Cartlow Dev MySQL engine cleanup completed")
    if hasattr(app.state, 'cartlow_prod_mysql_engine'):
        get_logger(name="UZAIR").info("✅ Cartlow Prod MySQL engine cleanup completed")