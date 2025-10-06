import os
import shutil
import subprocess
import platform
from pathlib import Path
from typing import Optional, List
from ....utils.my_logger import get_logger

logger = get_logger("FFMPEG_FINDER")

class FFmpegFinder:
    """Comprehensive ffmpeg finder utility"""
    
    @staticmethod
    def find_ffmpeg() -> str:
        """
        Find ffmpeg executable using multiple strategies
        
        Returns:
            str: Path to ffmpeg executable
            
        Raises:
            FileNotFoundError: If ffmpeg cannot be found
        """
        logger.info("🔍 Searching for ffmpeg executable...")
        
        # Strategy 1: Check common system paths
        system_paths = FFmpegFinder._get_system_paths()
        for path in system_paths:
            if FFmpegFinder._is_executable(path):
                logger.info(f"✅ Found ffmpeg at: {path}")
                return path
        
        # Strategy 2: Use which/where command
        which_path = FFmpegFinder._find_with_which()
        if which_path:
            logger.info(f"✅ Found ffmpeg with which: {which_path}")
            return which_path
        
        # Strategy 3: Search in PATH directories
        path_found = FFmpegFinder._search_in_path()
        if path_found:
            logger.info(f"✅ Found ffmpeg in PATH: {path_found}")
            return path_found
        
        # Strategy 4: Try to install ffmpeg automatically
        try:
            installed_path = FFmpegFinder._try_auto_install()
            if installed_path:
                logger.info(f"✅ Auto-installed ffmpeg at: {installed_path}")
                return installed_path
        except Exception as e:
            logger.warning(f"Auto-install failed: {e}")
        
        # If all strategies fail
        error_msg = "❌ ffmpeg not found! Please install ffmpeg manually."
        logger.error(error_msg)
        logger.error("Installation commands:")
        logger.error("  Ubuntu/Debian: sudo apt update && sudo apt install -y ffmpeg")
        logger.error("  CentOS/RHEL: sudo yum install -y ffmpeg")
        logger.error("  macOS: brew install ffmpeg")
        logger.error("  Windows: Download from https://ffmpeg.org/download.html")
        
        raise FileNotFoundError(error_msg)
    
    @staticmethod
    def _get_system_paths() -> List[str]:
        """Get common system paths where ffmpeg might be installed"""
        system = platform.system().lower()
        
        if system == "linux":
            return [
                "/usr/bin/ffmpeg",
                "/usr/local/bin/ffmpeg",
                "/opt/ffmpeg/bin/ffmpeg",
                "/snap/bin/ffmpeg",
                "/home/ubuntu/.local/bin/ffmpeg",
                "/home/carlow/.local/bin/ffmpeg",
            ]
        elif system == "darwin":  # macOS
            return [
                "/usr/local/bin/ffmpeg",
                "/opt/homebrew/bin/ffmpeg",
                "/usr/bin/ffmpeg",
            ]
        elif system == "windows":
            return [
                "C:\\ffmpeg\\bin\\ffmpeg.exe",
                "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
                "C:\\Program Files (x86)\\ffmpeg\\bin\\ffmpeg.exe",
            ]
        else:
            return []
    
    @staticmethod
    def _is_executable(path: str) -> bool:
        """Check if a path is an executable file"""
        try:
            return os.path.isfile(path) and os.access(path, os.X_OK)
        except Exception:
            return False
    
    @staticmethod
    def _find_with_which() -> Optional[str]:
        """Use which/where command to find ffmpeg"""
        try:
            if platform.system().lower() == "windows":
                result = subprocess.run(["where", "ffmpeg"], capture_output=True, text=True)
            else:
                result = subprocess.run(["which", "ffmpeg"], capture_output=True, text=True)
            
            if result.returncode == 0:
                path = result.stdout.strip().split('\n')[0]
                if FFmpegFinder._is_executable(path):
                    return path
        except Exception as e:
            logger.debug(f"which/where command failed: {e}")
        
        return None
    
    @staticmethod
    def _search_in_path() -> Optional[str]:
        """Search for ffmpeg in PATH environment variable"""
        try:
            path_dirs = os.environ.get('PATH', '').split(os.pathsep)
            for directory in path_dirs:
                if directory:
                    potential_path = os.path.join(directory, 'ffmpeg')
                    if platform.system().lower() == "windows":
                        potential_path += '.exe'
                    
                    if FFmpegFinder._is_executable(potential_path):
                        return potential_path
        except Exception as e:
            logger.debug(f"PATH search failed: {e}")
        
        return None
    
    @staticmethod
    def _try_auto_install() -> Optional[str]:
        """Try to automatically install ffmpeg"""
        try:
            system = platform.system().lower()
            
            if system == "linux":
                # Try to detect package manager
                if shutil.which("apt"):
                    logger.info("🔄 Attempting to install ffmpeg with apt...")
                    subprocess.run(["sudo", "apt", "update"], check=True, capture_output=True)
                    subprocess.run(["sudo", "apt", "install", "-y", "ffmpeg"], check=True, capture_output=True)
                    return "/usr/bin/ffmpeg"
                
                elif shutil.which("yum"):
                    logger.info("🔄 Attempting to install ffmpeg with yum...")
                    subprocess.run(["sudo", "yum", "install", "-y", "ffmpeg"], check=True, capture_output=True)
                    return "/usr/bin/ffmpeg"
                
                elif shutil.which("dnf"):
                    logger.info("🔄 Attempting to install ffmpeg with dnf...")
                    subprocess.run(["sudo", "dnf", "install", "-y", "ffmpeg"], check=True, capture_output=True)
                    return "/usr/bin/ffmpeg"
                    
        except Exception as e:
            logger.debug(f"Auto-install failed: {e}")
        
        return None
    
    @staticmethod
    def test_ffmpeg(ffmpeg_path: str) -> bool:
        """Test if ffmpeg is working correctly"""
        try:
            result = subprocess.run(
                [ffmpeg_path, "-version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode == 0:
                logger.info("✅ ffmpeg test successful")
                return True
            else:
                logger.error(f"❌ ffmpeg test failed: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            logger.error("❌ ffmpeg test timed out")
            return False
        except Exception as e:
            logger.error(f"❌ ffmpeg test error: {e}")
            return False

# Convenience function
def find_ffmpeg() -> str:
    """Find ffmpeg executable"""
    return FFmpegFinder.find_ffmpeg()

def test_ffmpeg(ffmpeg_path: str) -> bool:
    """Test if ffmpeg is working"""
    return FFmpegFinder.test_ffmpeg(ffmpeg_path)
