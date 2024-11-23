from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, concatenate_audioclips
from pydub import AudioSegment
import os
import logging
import subprocess
from typing import List, Dict
import yt_dlp

def sync_audio_with_video(video_url: str, tts_segments: List[Dict], output_dir: str) -> str:
    """
    Synchronize TTS audio segments with the original video.
    
    Args:
        video_url (str): URL of the YouTube video
        tts_segments (List[Dict]): List of TTS segments with timing information
        output_dir (str): Directory to save the output video
        
    Returns:
        str: Path to the synchronized video file
    """
    logger = logging.getLogger('yt_germanizer')
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Download video using yt-dlp
        logger.info("Downloading video...")
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            video_path = os.path.join(output_dir, f"{info['id']}.mp4")
        
        # Create a composite audio track
        logger.info("Creating composite audio track...")
        final_audio = AudioSegment.silent(duration=int(VideoFileClip(video_path).duration * 1000))
        
        # Add each TTS segment at the correct time
        for segment in tts_segments:
            # Load TTS audio
            tts_audio = AudioSegment.from_mp3(segment['audio_path'])
            
            # Add to final audio at the correct position
            position_ms = int(segment['start'])
            final_audio = final_audio.overlay(tts_audio, position=position_ms)
        
        # Export the final audio
        temp_audio_path = os.path.join(output_dir, "temp_final_audio.mp3")
        final_audio.export(temp_audio_path, format="mp3")
        
        # Create the final video with synchronized audio using FFmpeg
        logger.info("Creating final video...")
        output_path = os.path.join(output_dir, f"{info['id']}_german.mp4")
        
        # FFmpeg command to combine video and audio
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-i', temp_audio_path,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-strict', 'experimental',
            '-map', '0:v:0',
            '-map', '1:a:0',
            output_path
        ]
        
        # Run FFmpeg command
        process = subprocess.run(cmd, capture_output=True, text=True)
        if process.returncode != 0:
            raise Exception(f"FFmpeg error: {process.stderr}")
        
        # Clean up temporary files
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        if os.path.exists(video_path):
            os.remove(video_path)
        
        return output_path
        
    except Exception as e:
        logger.error(f"Error synchronizing video: {str(e)}")
        raise Exception(f"Video synchronization error: {str(e)}")
