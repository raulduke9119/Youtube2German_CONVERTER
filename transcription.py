import assemblyai as aai
import logging
from typing import Dict, List

def transcribe_audio(api_key: str, audio_path: str) -> List[Dict[str, str]]:
    """
    Transcribe audio file using AssemblyAI API with speaker diarization.
    
    Args:
        api_key (str): AssemblyAI API key
        audio_path (str): Path to the audio file
        
    Returns:
        List[Dict[str, str]]: List of transcription segments with text, timestamps, and speaker labels
    """
    logger = logging.getLogger('yt_germanizer')
    
    try:
        # Configure AssemblyAI client
        aai.settings.api_key = api_key
        
        logger.info("Uploading audio file...")
        # Create a transcriber instance
        transcriber = aai.Transcriber()
        
        # Configure transcription with speaker diarization
        config = aai.TranscriptionConfig(
            speaker_labels=True,
            language_code="en"  # You can make this configurable if needed
        )
        
        # Start transcription
        transcript = transcriber.transcribe(audio_path, config=config)
        
        if not transcript.utterances:
            raise Exception("No transcription results found")
            
        # Extract utterances with speaker labels and timestamps
        segments = []
        for utterance in transcript.utterances:
            segments.append({
                'text': utterance.text,
                'start': utterance.start,
                'end': utterance.end,
                'speaker': utterance.speaker,
                'confidence': utterance.confidence
            })
            
        return segments
        
    except Exception as e:
        logger.error(f"Error during transcription: {str(e)}")
        raise Exception(f"Transcription error: {str(e)}")
