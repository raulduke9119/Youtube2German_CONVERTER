import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add debug prints for environment loading
print("Current working directory:", os.getcwd())
print("Loading .env file...")
load_dotenv(Path(__file__).parent / '.env')
print("Environment variables loaded")

from src.audio_processing import download_audio
from src.transcription import transcribe_audio
from src.tts_generation import generate_tts
from src.video_sync import sync_audio_with_video
from src.utils import setup_logging, clean_filename, get_video_id, translate_segments
from src import config

def main():
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python main.py <youtube_url> [--quality QUALITY]")
        return 1
    
    video_url = sys.argv[1]
    audio_quality = '192'  # Default quality
    
    # Parse optional quality argument
    if len(sys.argv) > 3 and sys.argv[2] == '--quality':
        audio_quality = sys.argv[3]
    
    # Load environment variables
    api_key = os.getenv('ASSEMBLYAI_API_KEY')
    print("API Key present:", bool(api_key))
    if not api_key:
        print("Error: Please set ASSEMBLYAI_API_KEY in your .env file")
        return 1
    
    # Setup logging
    logger = setup_logging(config.LOG_FILE)
    logger.info("Starting YouTube Video Germanizer")
    
    try:
        # Get YouTube video URL from user
        video_id = get_video_id(video_url)
        logger.info(f"Processing video ID: {video_id}")
        
        # Create output directory for this video
        video_output_dir = config.OUTPUT_DIR / clean_filename(video_id)
        os.makedirs(video_output_dir, exist_ok=True)
        
        # Step 1: Download audio from YouTube video
        logger.info("Downloading audio from YouTube...")
        audio_path = download_audio(
            video_url,
            output_dir=str(config.INPUT_DIR),
            quality=audio_quality
        )
        logger.info(f"Audio downloaded successfully to: {audio_path}")
        
        # Step 2: Transcribe audio with AssemblyAI
        logger.info("Transcribing audio with speaker diarization...")
        transcription = transcribe_audio(api_key, audio_path)
        logger.info(f"Transcription completed: {len(transcription)} segments")
        
        # Log speaker information
        speakers = set(segment['speaker'] for segment in transcription)
        logger.info(f"Detected {len(speakers)} speakers: {', '.join(speakers)}")
        
        # Step 3: Translate transcription to German
        logger.info("Translating transcription to German...")
        translated_segments = translate_segments(transcription)
        logger.info(f"Translation completed: {len(translated_segments)} segments")
        
        # Step 4: Generate German TTS for each segment
        logger.info("Generating German TTS...")
        tts_segments = []
        current_speaker = None
        
        for segment in translated_segments:
            # Check if speaker changed to adjust voice
            if segment['speaker'] != current_speaker:
                current_speaker = segment['speaker']
                logger.info(f"Switching to voice for speaker {current_speaker}")
            
            # Generate TTS for each segment
            tts_path = generate_tts(
                text=segment['text'],
                output_dir=str(config.TTS_DIR),
                start_time=segment['start'],
                speaker=segment['speaker']  # Pass speaker info to TTS generator
            )
            tts_segments.append({
                'audio_path': tts_path,
                'start': segment['start'],
                'end': segment['end'],
                'speaker': segment['speaker']
            })
        logger.info(f"TTS generation completed: {len(tts_segments)} segments")
        
        # Step 5: Synchronize TTS with video
        logger.info("Synchronizing TTS with video...")
        output_path = sync_audio_with_video(
            video_url=video_url,
            tts_segments=tts_segments,
            output_dir=str(config.OUTPUT_DIR)
        )
        
        logger.info(f"Video processing completed! Output saved to: {output_path}")
        return output_path
    
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
