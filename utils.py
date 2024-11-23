import os
import logging
import textwrap
from typing import Optional, List, Dict
from pathlib import Path

def setup_logging(log_file: Optional[str] = None) -> logging.Logger:
    """
    Set up logging configuration.
    
    Args:
        log_file (str, optional): Path to log file. If None, logs to console only.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger('yt_germanizer')
    logger.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Add file handler if log_file is provided
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def clean_filename(filename: str) -> str:
    """
    Clean a filename by removing invalid characters.
    
    Args:
        filename (str): Original filename
    
    Returns:
        str: Cleaned filename
    """
    # Replace invalid characters with underscores
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def ensure_dir(directory: str) -> str:
    """
    Ensure a directory exists, create it if it doesn't.
    
    Args:
        directory (str): Directory path
    
    Returns:
        str: Absolute path to the directory
    """
    path = Path(directory).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return str(path)

def get_video_id(url: str) -> str:
    """
    Extract video ID from YouTube URL.
    
    Args:
        url (str): YouTube URL
    
    Returns:
        str: Video ID
    
    Raises:
        ValueError: If URL is invalid
    """
    if 'youtu.be' in url:
        return url.split('/')[-1].split('?')[0]
    elif 'youtube.com' in url:
        if 'v=' in url:
            return url.split('v=')[1].split('&')[0]
        elif 'embed/' in url:
            return url.split('embed/')[-1].split('?')[0]
    raise ValueError("Invalid YouTube URL format")

def chunk_text(text: str, max_length: int = 4500) -> List[str]:
    """
    Split text into chunks that don't exceed max_length while preserving sentence boundaries.
    
    Args:
        text (str): Text to split
        max_length (int): Maximum length of each chunk
        
    Returns:
        List[str]: List of text chunks
    """
    # First split by sentences (roughly)
    sentences = text.replace('? ', '?|').replace('! ', '!|').replace('. ', '.|').split('|')
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # If single sentence is too long, split it into smaller parts
        if len(sentence) > max_length:
            words = sentence.split()
            temp_chunk = []
            temp_length = 0
            
            for word in words:
                if temp_length + len(word) + 1 > max_length:
                    chunks.append(' '.join(temp_chunk))
                    temp_chunk = [word]
                    temp_length = len(word)
                else:
                    temp_chunk.append(word)
                    temp_length += len(word) + 1
            
            if temp_chunk:
                chunks.append(' '.join(temp_chunk))
            continue
        
        # Try to add sentence to current chunk
        if current_length + len(sentence) + 1 <= max_length:
            current_chunk.append(sentence)
            current_length += len(sentence) + 1
        else:
            # Current chunk is full, start a new one
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
            current_length = len(sentence)
    
    # Add the last chunk if it exists
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def translate_segments(segments: List[Dict]) -> List[Dict]:
    """
    Translate transcription segments from English to German.
    
    Args:
        segments (list): List of transcription segments with 'text', 'start', and 'end' keys
        
    Returns:
        list: List of translated segments with the same structure
    """
    from deep_translator import GoogleTranslator
    logger = logging.getLogger('yt_germanizer')
    
    translator = GoogleTranslator(source='auto', target='de')
    translated_segments = []
    
    for segment in segments:
        try:
            # Split text into smaller chunks if needed
            text = segment['text']
            if len(text) > 4500:  # Leave some margin for safety
                chunks = chunk_text(text)
                translated_chunks = []
                for chunk in chunks:
                    translated_chunk = translator.translate(chunk)
                    translated_chunks.append(translated_chunk)
                translated_text = ' '.join(translated_chunks)
            else:
                translated_text = translator.translate(text)
            
            translated_segments.append({
                'text': translated_text,
                'start': segment['start'],
                'end': segment['end'],
                'speaker': segment.get('speaker', 'A')  # Preserve speaker information
            })
            
        except Exception as e:
            logger.error(f"Error translating segment: {str(e)}")
            # If translation fails, use original text
            translated_segments.append(segment)
    
    return translated_segments
