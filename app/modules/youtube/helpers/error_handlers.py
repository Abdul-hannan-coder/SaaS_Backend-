"""
Global error handlers for the FastAPI application
"""
from fastapi import Request
from fastapi.responses import JSONResponse

# Import error models from all modules
from ...login_logout.models.error_models import (
    UserNotFoundError,
    UserAlreadyExistsError,
    DatabaseError as LoginDatabaseError,
    AuthenticationError,
    ValidationError as LoginValidationError
)
from ...youtube.gemini.error_models import (
    GeminiKeyNotFoundError,
    GeminiKeyAlreadyExistsError,
    GeminiKeyInvalidError,
    DatabaseError as GeminiDatabaseError,
    ValidationError as GeminiValidationError
)
from ...youtube.title_generator.error_models import (
    TitleGenerationError,
    VideoNotFoundError,
    VideoTranscriptNotFoundError,
    ApiKeyMissingError,
    ValidationError as TitleValidationError,
    DatabaseError as TitleDatabaseError
)
from ...youtube.discription_generator.error_models import (
    DescriptionGenerationError,
    DescriptionSaveError,
    VideoNotFoundError as DescriptionVideoNotFoundError,
    VideoTranscriptNotFoundError as DescriptionVideoTranscriptNotFoundError,
    ApiKeyMissingError as DescriptionApiKeyMissingError,
    ValidationError as DescriptionValidationError,
    DatabaseError as DescriptionDatabaseError
)
from ...youtube.thumbnail_generator.error_models import (
    ThumbnailGenerationError,
    ThumbnailSaveError,
    ThumbnailUploadError,
    VideoNotFoundError as ThumbnailVideoNotFoundError,
    VideoTranscriptNotFoundError as ThumbnailVideoTranscriptNotFoundError,
    ApiKeyMissingError as ThumbnailApiKeyMissingError,
    ValidationError as ThumbnailValidationError,
    DatabaseError as ThumbnailDatabaseError
)
from ...youtube.timestamps_generator.error_models import (
    TimestampsGenerationError,
    TimestampsSaveError,
    VideoNotFoundError as TimestampsVideoNotFoundError,
    VideoTranscriptNotFoundError as TimestampsVideoTranscriptNotFoundError,
    ApiKeyMissingError as TimestampsApiKeyMissingError,
    ValidationError as TimestampsValidationError,
    DatabaseError as TimestampsDatabaseError
)
from ...youtube.privacy_status.error_models import (
    PrivacyStatusUpdateError,
    PrivacyStatusGetError,
    VideoNotFoundError as PrivacyVideoNotFoundError,
    VideoAccessDeniedError,
    ValidationError as PrivacyValidationError,
    DatabaseError as PrivacyDatabaseError
)
from ...youtube.playlist.error_models import (
    PlaylistCreationError,
    PlaylistRetrievalError,
    PlaylistSelectionError,
    VideoNotFoundError as PlaylistVideoNotFoundError,
    VideoAccessDeniedError as PlaylistVideoAccessDeniedError,
    YouTubeApiError,
    YouTubeAuthError,
    ValidationError as PlaylistValidationError,
    DatabaseError as PlaylistDatabaseError
)
from ...youtube.schedule.error_models import (
    ScheduleCreationError,
    ScheduleRetrievalError,
    ScheduleCancellationError,
    VideoNotFoundError as ScheduleVideoNotFoundError,
    ValidationError as ScheduleValidationError,
    DatabaseError as ScheduleDatabaseError
)
from ...youtube.youtube_creds.error_models import (
    YouTubeCredentialsAlreadyExistsError,
    YouTubeCredentialsNotFoundError,
    YouTubeCredentialsCreationError,
    YouTubeCredentialsRetrievalError,
    YouTubeCredentialsUpdateError,
    YouTubeCredentialsDeletionError,
    ValidationError as YouTubeCredentialsValidationError,
    DatabaseError as YouTubeCredentialsDatabaseError
)
from ...youtube.video.error_models import (
    VideoUploadError,
    VideoNotFoundError,
    VideoRetrievalError,
    VideoUpdateError,
    VideoDeletionError,
    VideoProcessingError,
    VideoDownloadError,
    InvalidFileTypeError,
    FileSystemError,
    ValidationError as VideoValidationError,
    DatabaseError as VideoDatabaseError
)
from ...youtube.youtube_token.error_models import (
    TokenCreationError,
    TokenNotFoundError,
    TokenRetrievalError,
    TokenRefreshError,
    OAuthCallbackError,
    OAuthUrlGenerationError,
    GoogleApiError,
    ValidationError as YouTubeTokenValidationError,
    DatabaseError as YouTubeTokenDatabaseError
)
from ...youtube.video_upload.error_models import (
    VideoUploadError,
    VideoFileNotFoundError,
    InvalidVideoFormatError,
    UploadInterruptedError,
    ThumbnailUploadError,
    PlaylistAdditionError,
    VideoMetadataError,
    YouTubeApiQuotaError,
    VideoTooLargeError,
    UploadTimeoutError,
    YouTubeApiError as VideoUploadYouTubeApiError,
    ValidationError as VideoUploadValidationError,
    DatabaseError as VideoUploadDatabaseError
)


def register_error_handlers(app):
    """Register all global error handlers with the FastAPI app"""
    
    # Login/Auth Error Handlers
    @app.exception_handler(UserNotFoundError)
    async def user_not_found_handler(request: Request, exc: UserNotFoundError):
        return JSONResponse(
            status_code=404,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(UserAlreadyExistsError)
    async def user_already_exists_handler(request: Request, exc: UserAlreadyExistsError):
        return JSONResponse(
            status_code=400,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(AuthenticationError)
    async def authentication_error_handler(request: Request, exc: AuthenticationError):
        return JSONResponse(
            status_code=401,
            content=exc.error_detail.to_dict()
        )
    
    # Gemini Error Handlers
    @app.exception_handler(GeminiKeyNotFoundError)
    async def gemini_key_not_found_handler(request: Request, exc: GeminiKeyNotFoundError):
        return JSONResponse(
            status_code=404,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(GeminiKeyAlreadyExistsError)
    async def gemini_key_already_exists_handler(request: Request, exc: GeminiKeyAlreadyExistsError):
        return JSONResponse(
            status_code=400,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(GeminiKeyInvalidError)
    async def gemini_key_invalid_handler(request: Request, exc: GeminiKeyInvalidError):
        return JSONResponse(
            status_code=400,
            content=exc.error_detail.to_dict()
        )
    
    # Title Generator Error Handlers
    @app.exception_handler(TitleGenerationError)
    async def title_generation_error_handler(request: Request, exc: TitleGenerationError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(VideoNotFoundError)
    async def video_not_found_handler(request: Request, exc: VideoNotFoundError):
        return JSONResponse(
            status_code=404,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(VideoTranscriptNotFoundError)
    async def video_transcript_not_found_handler(request: Request, exc: VideoTranscriptNotFoundError):
        return JSONResponse(
            status_code=404,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(ApiKeyMissingError)
    async def api_key_missing_handler(request: Request, exc: ApiKeyMissingError):
        return JSONResponse(
            status_code=400,
            content=exc.error_detail.to_dict()
        )
    
    # Validation Error Handlers
    @app.exception_handler(LoginValidationError)
    async def login_validation_error_handler(request: Request, exc: LoginValidationError):
        return JSONResponse(
            status_code=400,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(GeminiValidationError)
    async def gemini_validation_error_handler(request: Request, exc: GeminiValidationError):
        return JSONResponse(
            status_code=400,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(TitleValidationError)
    async def title_validation_error_handler(request: Request, exc: TitleValidationError):
        return JSONResponse(
            status_code=400,
            content=exc.error_detail.to_dict()
        )
    
    # Database Error Handlers
    @app.exception_handler(LoginDatabaseError)
    async def login_database_error_handler(request: Request, exc: LoginDatabaseError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(GeminiDatabaseError)
    async def gemini_database_error_handler(request: Request, exc: GeminiDatabaseError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(TitleDatabaseError)
    async def title_database_error_handler(request: Request, exc: TitleDatabaseError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )
    
    # Description Generator Error Handlers
    @app.exception_handler(DescriptionGenerationError)
    async def description_generation_error_handler(request: Request, exc: DescriptionGenerationError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(DescriptionSaveError)
    async def description_save_error_handler(request: Request, exc: DescriptionSaveError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(DescriptionVideoNotFoundError)
    async def description_video_not_found_handler(request: Request, exc: DescriptionVideoNotFoundError):
        return JSONResponse(
            status_code=404,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(DescriptionVideoTranscriptNotFoundError)
    async def description_video_transcript_not_found_handler(request: Request, exc: DescriptionVideoTranscriptNotFoundError):
        return JSONResponse(
            status_code=404,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(DescriptionApiKeyMissingError)
    async def description_api_key_missing_handler(request: Request, exc: DescriptionApiKeyMissingError):
        return JSONResponse(
            status_code=400,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(DescriptionValidationError)
    async def description_validation_error_handler(request: Request, exc: DescriptionValidationError):
        return JSONResponse(
            status_code=400,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(DescriptionDatabaseError)
    async def description_database_error_handler(request: Request, exc: DescriptionDatabaseError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )
    
    # Thumbnail Generator Error Handlers
    @app.exception_handler(ThumbnailGenerationError)
    async def thumbnail_generation_error_handler(request: Request, exc: ThumbnailGenerationError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(ThumbnailSaveError)
    async def thumbnail_save_error_handler(request: Request, exc: ThumbnailSaveError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(ThumbnailUploadError)
    async def thumbnail_upload_error_handler(request: Request, exc: ThumbnailUploadError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(ThumbnailVideoNotFoundError)
    async def thumbnail_video_not_found_handler(request: Request, exc: ThumbnailVideoNotFoundError):
        return JSONResponse(
            status_code=404,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(ThumbnailVideoTranscriptNotFoundError)
    async def thumbnail_video_transcript_not_found_handler(request: Request, exc: ThumbnailVideoTranscriptNotFoundError):
        return JSONResponse(
            status_code=404,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(ThumbnailApiKeyMissingError)
    async def thumbnail_api_key_missing_handler(request: Request, exc: ThumbnailApiKeyMissingError):
        return JSONResponse(
            status_code=400,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(ThumbnailValidationError)
    async def thumbnail_validation_error_handler(request: Request, exc: ThumbnailValidationError):
        return JSONResponse(
            status_code=400,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(ThumbnailDatabaseError)
    async def thumbnail_database_error_handler(request: Request, exc: ThumbnailDatabaseError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )
    
    # Timestamps Generator Error Handlers
    @app.exception_handler(TimestampsGenerationError)
    async def timestamps_generation_error_handler(request: Request, exc: TimestampsGenerationError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(TimestampsSaveError)
    async def timestamps_save_error_handler(request: Request, exc: TimestampsSaveError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(TimestampsVideoNotFoundError)
    async def timestamps_video_not_found_handler(request: Request, exc: TimestampsVideoNotFoundError):
        return JSONResponse(
            status_code=404,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(TimestampsVideoTranscriptNotFoundError)
    async def timestamps_video_transcript_not_found_handler(request: Request, exc: TimestampsVideoTranscriptNotFoundError):
        return JSONResponse(
            status_code=404,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(TimestampsApiKeyMissingError)
    async def timestamps_api_key_missing_handler(request: Request, exc: TimestampsApiKeyMissingError):
        return JSONResponse(
            status_code=400,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(TimestampsValidationError)
    async def timestamps_validation_error_handler(request: Request, exc: TimestampsValidationError):
        return JSONResponse(
            status_code=400,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(TimestampsDatabaseError)
    async def timestamps_database_error_handler(request: Request, exc: TimestampsDatabaseError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )
    
    # Privacy Status Error Handlers
    @app.exception_handler(PrivacyStatusUpdateError)
    async def privacy_status_update_error_handler(request: Request, exc: PrivacyStatusUpdateError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(PrivacyStatusGetError)
    async def privacy_status_get_error_handler(request: Request, exc: PrivacyStatusGetError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(PrivacyVideoNotFoundError)
    async def privacy_video_not_found_handler(request: Request, exc: PrivacyVideoNotFoundError):
        return JSONResponse(
            status_code=404,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(VideoAccessDeniedError)
    async def video_access_denied_handler(request: Request, exc: VideoAccessDeniedError):
        return JSONResponse(
            status_code=403,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(PrivacyValidationError)
    async def privacy_validation_error_handler(request: Request, exc: PrivacyValidationError):
        return JSONResponse(
            status_code=400,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(PrivacyDatabaseError)
    async def privacy_database_error_handler(request: Request, exc: PrivacyDatabaseError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )
    
    # Playlist Error Handlers
    @app.exception_handler(PlaylistCreationError)
    async def playlist_creation_error_handler(request: Request, exc: PlaylistCreationError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(PlaylistRetrievalError)
    async def playlist_retrieval_error_handler(request: Request, exc: PlaylistRetrievalError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(PlaylistSelectionError)
    async def playlist_selection_error_handler(request: Request, exc: PlaylistSelectionError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(PlaylistVideoNotFoundError)
    async def playlist_video_not_found_handler(request: Request, exc: PlaylistVideoNotFoundError):
        return JSONResponse(
            status_code=404,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(PlaylistVideoAccessDeniedError)
    async def playlist_video_access_denied_handler(request: Request, exc: PlaylistVideoAccessDeniedError):
        return JSONResponse(
            status_code=403,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(YouTubeApiError)
    async def youtube_api_error_handler(request: Request, exc: YouTubeApiError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(YouTubeAuthError)
    async def youtube_auth_error_handler(request: Request, exc: YouTubeAuthError):
        return JSONResponse(
            status_code=401,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(PlaylistValidationError)
    async def playlist_validation_error_handler(request: Request, exc: PlaylistValidationError):
        return JSONResponse(
            status_code=400,
            content=exc.error_detail.to_dict()
        )
    
    @app.exception_handler(PlaylistDatabaseError)
    async def playlist_database_error_handler(request: Request, exc: PlaylistDatabaseError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )

    # Schedule Error Handlers
    @app.exception_handler(ScheduleCreationError)
    async def schedule_creation_error_handler(request: Request, exc: ScheduleCreationError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(ScheduleRetrievalError)
    async def schedule_retrieval_error_handler(request: Request, exc: ScheduleRetrievalError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(ScheduleCancellationError)
    async def schedule_cancellation_error_handler(request: Request, exc: ScheduleCancellationError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(ScheduleVideoNotFoundError)
    async def schedule_video_not_found_handler(request: Request, exc: ScheduleVideoNotFoundError):
        return JSONResponse(
            status_code=404,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(ScheduleValidationError)
    async def schedule_validation_error_handler(request: Request, exc: ScheduleValidationError):
        return JSONResponse(
            status_code=400,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(ScheduleDatabaseError)
    async def schedule_database_error_handler(request: Request, exc: ScheduleDatabaseError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )

    # YouTube Credentials Error Handlers
    @app.exception_handler(YouTubeCredentialsAlreadyExistsError)
    async def youtube_credentials_already_exists_handler(request: Request, exc: YouTubeCredentialsAlreadyExistsError):
        return JSONResponse(
            status_code=400,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(YouTubeCredentialsNotFoundError)
    async def youtube_credentials_not_found_handler(request: Request, exc: YouTubeCredentialsNotFoundError):
        return JSONResponse(
            status_code=404,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(YouTubeCredentialsCreationError)
    async def youtube_credentials_creation_error_handler(request: Request, exc: YouTubeCredentialsCreationError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(YouTubeCredentialsRetrievalError)
    async def youtube_credentials_retrieval_error_handler(request: Request, exc: YouTubeCredentialsRetrievalError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(YouTubeCredentialsUpdateError)
    async def youtube_credentials_update_error_handler(request: Request, exc: YouTubeCredentialsUpdateError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(YouTubeCredentialsDeletionError)
    async def youtube_credentials_deletion_error_handler(request: Request, exc: YouTubeCredentialsDeletionError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(YouTubeCredentialsValidationError)
    async def youtube_credentials_validation_error_handler(request: Request, exc: YouTubeCredentialsValidationError):
        return JSONResponse(
            status_code=400,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(YouTubeCredentialsDatabaseError)
    async def youtube_credentials_database_error_handler(request: Request, exc: YouTubeCredentialsDatabaseError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )

    # Video Error Handlers
    @app.exception_handler(VideoUploadError)
    async def video_upload_error_handler(request: Request, exc: VideoUploadError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(VideoNotFoundError)
    async def video_not_found_handler(request: Request, exc: VideoNotFoundError):
        return JSONResponse(
            status_code=404,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(VideoRetrievalError)
    async def video_retrieval_error_handler(request: Request, exc: VideoRetrievalError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(VideoUpdateError)
    async def video_update_error_handler(request: Request, exc: VideoUpdateError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(VideoDeletionError)
    async def video_deletion_error_handler(request: Request, exc: VideoDeletionError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(VideoProcessingError)
    async def video_processing_error_handler(request: Request, exc: VideoProcessingError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(VideoDownloadError)
    async def video_download_error_handler(request: Request, exc: VideoDownloadError):
        return JSONResponse(
            status_code=400,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(InvalidFileTypeError)
    async def invalid_file_type_error_handler(request: Request, exc: InvalidFileTypeError):
        return JSONResponse(
            status_code=400,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(FileSystemError)
    async def file_system_error_handler(request: Request, exc: FileSystemError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(VideoValidationError)
    async def video_validation_error_handler(request: Request, exc: VideoValidationError):
        return JSONResponse(
            status_code=400,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(VideoDatabaseError)
    async def video_database_error_handler(request: Request, exc: VideoDatabaseError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )

    # YouTube Token Error Handlers
    @app.exception_handler(TokenCreationError)
    async def token_creation_error_handler(request: Request, exc: TokenCreationError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(TokenNotFoundError)
    async def token_not_found_handler(request: Request, exc: TokenNotFoundError):
        return JSONResponse(
            status_code=404,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(TokenRetrievalError)
    async def token_retrieval_error_handler(request: Request, exc: TokenRetrievalError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(TokenRefreshError)
    async def token_refresh_error_handler(request: Request, exc: TokenRefreshError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(OAuthCallbackError)
    async def oauth_callback_error_handler(request: Request, exc: OAuthCallbackError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(OAuthUrlGenerationError)
    async def oauth_url_generation_error_handler(request: Request, exc: OAuthUrlGenerationError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(GoogleApiError)
    async def google_api_error_handler(request: Request, exc: GoogleApiError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(YouTubeTokenValidationError)
    async def youtube_token_validation_error_handler(request: Request, exc: YouTubeTokenValidationError):
        return JSONResponse(
            status_code=400,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(YouTubeTokenDatabaseError)
    async def youtube_token_database_error_handler(request: Request, exc: YouTubeTokenDatabaseError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )

    # Video Upload Error Handlers
    @app.exception_handler(VideoUploadError)
    async def video_upload_error_handler(request: Request, exc: VideoUploadError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(VideoFileNotFoundError)
    async def video_file_not_found_handler(request: Request, exc: VideoFileNotFoundError):
        return JSONResponse(
            status_code=404,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(InvalidVideoFormatError)
    async def invalid_video_format_handler(request: Request, exc: InvalidVideoFormatError):
        return JSONResponse(
            status_code=400,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(UploadInterruptedError)
    async def upload_interrupted_handler(request: Request, exc: UploadInterruptedError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(ThumbnailUploadError)
    async def thumbnail_upload_error_handler(request: Request, exc: ThumbnailUploadError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(PlaylistAdditionError)
    async def playlist_addition_error_handler(request: Request, exc: PlaylistAdditionError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(VideoMetadataError)
    async def video_metadata_error_handler(request: Request, exc: VideoMetadataError):
        return JSONResponse(
            status_code=400,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(YouTubeApiQuotaError)
    async def youtube_api_quota_error_handler(request: Request, exc: YouTubeApiQuotaError):
        return JSONResponse(
            status_code=429,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(VideoTooLargeError)
    async def video_too_large_error_handler(request: Request, exc: VideoTooLargeError):
        return JSONResponse(
            status_code=413,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(UploadTimeoutError)
    async def upload_timeout_error_handler(request: Request, exc: UploadTimeoutError):
        return JSONResponse(
            status_code=408,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(VideoUploadYouTubeApiError)
    async def video_upload_youtube_api_error_handler(request: Request, exc: VideoUploadYouTubeApiError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(VideoUploadValidationError)
    async def video_upload_validation_error_handler(request: Request, exc: VideoUploadValidationError):
        return JSONResponse(
            status_code=400,
            content=exc.error_detail.to_dict()
        )

    @app.exception_handler(VideoUploadDatabaseError)
    async def video_upload_database_error_handler(request: Request, exc: VideoUploadDatabaseError):
        return JSONResponse(
            status_code=500,
            content=exc.error_detail.to_dict()
        )
