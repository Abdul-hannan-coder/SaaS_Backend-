import aiohttp
from pathlib import Path


async def download_image_from_url(url: str, dir_path: str ,video_id: str) -> dict:
    """
    Downloads an image from a URL and saves it to the images directory.
    
    Args:
        url: The URL of the image to download
        filename: The filename to save the image as
        
    Returns:
        Dictionary containing:
        - 'success': Boolean indicating if download was successful
        - 'url': The original URL of the image
        - 'local_path': The full path to the saved image file (if successful)
        - 'filename': The actual filename used
        - 'message': Success or error message
    """

    # Create images directory if it doesn't exist
    image_dir = Path(dir_path)
    image_dir.mkdir(exist_ok=True)
    filename = f"{video_id}.png"
    
    # Add .png extension if not present
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        filename += '.png'
        
    filepath = image_dir / filename
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    with open(filepath, 'wb') as f:
                        f.write(await response.read())
                    
                    return {
                        'success': True,
                        'url': url,
                        'custom_thumbnail_path': str(filepath),
                        'filename': filename,
                        'message': f'Image downloaded successfully to {filepath}'
                    }
                else:
                    return {
                        'success': False,
                        'url': url,
                        'custom_thumbnail_path': None,
                        'filename': f"{video_id}.png",
                        'message': f'Failed to download image. Status code: {response.status}'
                    }
                    
    except Exception as e:
        return {
            'success': False,
            'url': url,
            'custom_thumbnail_path': None,
            'filename': filename,
            'message': f'Error downloading image: {str(e)}'
        }