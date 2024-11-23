from TTS.api import TTS
import os
import tempfile
import torch
from typing import Dict, Any, Optional
import logging
from pathlib import Path
from pydub import AudioSegment
import random

# Initialize TTS model globally for better performance
tts_model = None

def init_tts_model():
    """Initialize the Coqui TTS model with Thorsten voice."""
    global tts_model
    if tts_model is None:
        tts_model = TTS(model_name="tts_models/de/thorsten/tacotron2-DDC", progress_bar=False)

# Define different voice profiles for speakers
VOICE_PROFILES = {
    'A': {'speed': 1.0, 'pitch': 0},      # Default voice
    'B': {'speed': 0.95, 'pitch': 2},     # Slightly slower, higher pitch
    'C': {'speed': 1.05, 'pitch': -2},    # Slightly faster, lower pitch
    'D': {'speed': 0.9, 'pitch': 4},      # Slower, higher pitch
    'E': {'speed': 1.1, 'pitch': -4},     # Faster, lower pitch
}

def get_voice_profile(speaker: str) -> Dict[str, float]:
    """
    Get voice profile for a speaker. If the speaker doesn't have a profile,
    create a new one with random variations.
    
    Args:
        speaker (str): Speaker identifier
        
    Returns:
        Dict[str, float]: Voice profile with pitch and speed settings
    """
    if speaker not in VOICE_PROFILES:
        # Create a new random profile for unknown speakers
        VOICE_PROFILES[speaker] = {
            'speed': random.uniform(0.9, 1.1),
            'pitch': random.uniform(-4, 4)
        }
    return VOICE_PROFILES[speaker]

def generate_tts_audio(transcription: Dict[str, Any], output_path: str = 'data/output/synced_audio.mp3') -> str:
    """
    Generate TTS audio from transcription with timing synchronization and speaker voices.
    
    Args:
        transcription (dict): Transcription data containing words, timing, and speakers
        output_path (str): Path to save the synchronized TTS audio
        
    Returns:
        str: Path to the generated audio file
    """
    try:
        # Initialize TTS model if not already initialized
        init_tts_model()
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Process each utterance
        audio_segments = []
        current_position = 0
        
        for utterance in transcription['utterances']:
            # Generate TTS for each segment
            tts_path = generate_tts(
                utterance.text,
                os.path.dirname(output_path),
                utterance.start,
                utterance.get('speaker', 'A')
            )
            
            # Add to segments list
            audio_segments.append({
                'path': tts_path,
                'start': utterance.start,
                'end': utterance.end,
                'speaker': utterance.get('speaker', 'A')
            })
        
        # Combine all segments
        final_audio = AudioSegment.silent(duration=0)
        
        for segment in audio_segments:
            # Load the segment audio
            segment_audio = AudioSegment.from_wav(segment['path'])
            
            # Add silence if needed
            if segment['start'] > current_position:
                silence_duration = segment['start'] - current_position
                final_audio += AudioSegment.silent(duration=silence_duration)
            
            # Add the segment audio
            final_audio += segment_audio
            current_position = segment['end']
        
        # Export final audio
        final_audio.export(output_path, format="mp3")
        return output_path
        
    except Exception as e:
        raise Exception(f"TTS generation error: {str(e)}")

def generate_tts(text: str, output_dir: str, start_time: float, speaker: Optional[str] = None) -> str:
    """
    Generate German TTS audio for a text segment using Coqui TTS with Thorsten voice.
    
    Args:
        text (str): Text to convert to speech
        output_dir (str): Directory to save the TTS audio files
        start_time (float): Start time of the segment in milliseconds
        speaker (Optional[str]): Speaker identifier for voice profile
        
    Returns:
        str: Path to the generated TTS audio file
    """
    logger = logging.getLogger('yt_germanizer')
    
    try:
        # Initialize TTS model if not already initialized
        init_tts_model()
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate a unique filename based on the start time and speaker
        speaker_suffix = f"_{speaker}" if speaker else ""
        filename = f"tts_{int(start_time)}{speaker_suffix}.wav"
        output_path = os.path.join(output_dir, filename)
        
        # Get voice profile for the speaker
        voice_profile = get_voice_profile(speaker) if speaker else VOICE_PROFILES['A']
        
        # Generate TTS audio
        logger.info(f"Generating TTS for speaker {speaker}: {text[:50]}...")
        
        # Generate speech with Coqui TTS
        tts_model.tts_to_file(
            text=text,
            file_path=output_path,
            speed=voice_profile['speed']
        )
        
        return output_path
        
    except Exception as e:
        logger.error(f"Error generating TTS: {str(e)}")
        raise Exception(f"TTS generation error: {str(e)}")
