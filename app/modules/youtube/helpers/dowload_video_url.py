from ....utils.my_logger import get_logger

logger = get_logger("DOWNLOAD_VIDEO")


def download_youtube_video(url: str, output_dir: str = ".") -> tuple[str, str]:
    """
    Download a YouTube video in the highest available quality (video+audio merged).
    
    Args:
        url (str): YouTube video URL
        output_dir (str): Folder to save the downloaded video
    
    Returns:
        tuple[str, str]: (video_id, filepath) - YouTube video ID and path to the saved video file
    """
    try:
        import yt_dlp
        
        ydl_opts = {
            'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
            'format': 'bv*+ba/b',   # best video + best audio, fallback to best
            'merge_output_format': 'mp4',
            'noplaylist': True,
            'quiet': False,         # set to True if you want no console logs
            'concurrent_fragment_downloads': 5,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info['id']
            filepath = ydl.prepare_filename(info).replace(".webm", ".mp4").replace(".mkv", ".mp4")
            logger.info(f"Downloaded video: {filepath}")
            return video_id, filepath
                
    except ImportError:
        logger.error("❌ yt-dlp not installed. Install with: pip install yt-dlp")
        return None, None
    except Exception as e:
        logger.error(f"❌ yt-dlp error: {e}")
        return None, None
