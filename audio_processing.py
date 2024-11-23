from moviepy.editor import AudioFileClip
import os
import time
import logging
from typing import Optional
import yt_dlp
import re

def get_video_id(video_url: str) -> str:
    """
    Extract video ID from YouTube video URL.
    
    Args:
        video_url (str): YouTube video URL
        
    Returns:
        str: Video ID
    """
    # Support both standard and shortened YouTube URLs
    if 'youtu.be' in video_url:
        return video_url.split('/')[-1]
    else:
        pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
        match = re.search(pattern, video_url)
        if match:
            return match.group(1)
        raise ValueError("Invalid YouTube URL")

def download_audio(video_url: str, output_dir: str, quality: str = '192') -> str:
    """
    Download audio from a YouTube video URL using yt-dlp.
    
    Args:
        video_url (str): YouTube video URL
        output_dir (str): Directory to save the downloaded audio
        quality (str): Audio quality in kbps (default: '192')
        
    Returns:
        str: Path to the downloaded audio file
    """
    logger = logging.getLogger('yt_germanizer')
    
    logger.info("Downloading audio using yt-dlp...")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get video ID for filename
    video_id = get_video_id(video_url)
    output_path = os.path.join(output_dir, f"{video_id}.mp3")
    
    # Configure yt-dlp options for best audio quality
    ydl_opts = {
        'format': 'm4a/bestaudio/best',  # Prefer m4a format for better quality
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': quality,
        }],
        'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
        'quiet': False,
        'no_warnings': True,
        'extract_audio': True,
        'audio_quality': 0,  # Best audio quality
        'postprocessor_args': [
            '-ar', '44100'  # Set audio sample rate
        ],
        'writethumbnail': True,  # Download video thumbnail
        'writesubtitles': True,  # Download subtitles if available
        'writeautomaticsub': True  # Download auto-generated subtitles if available
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get video info first
            logger.info("Retrieving video information...")
            info = ydl.extract_info(video_url, download=False)
            
            # Check if video is available
            if info.get('is_live'):
                raise ValueError("Live streams are not supported")
                
            # Download the video
            logger.info(f"Downloading audio from video: {info.get('title', video_id)}")
            ydl.download([video_url])
            
            # Verify the downloaded file exists
            if not os.path.exists(output_path):
                raise FileNotFoundError(f"Downloaded audio file not found at {output_path}")
            
            logger.info(f"Successfully downloaded audio to {output_path}")
            return output_path
            
    except yt_dlp.utils.DownloadError as e:
        logger.error(f"YouTube download error: {str(e)}")
        raise Exception(f"Error downloading video: {str(e)}")
    except Exception as e:
        logger.error(f"Error downloading audio: {str(e)}")
        raise Exception(f"Error downloading audio: {str(e)}")
