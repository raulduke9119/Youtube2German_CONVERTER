from deep_translator import GoogleTranslator
import logging
from typing import List, Dict

def translate_text(text: str, source_lang: str = 'en', target_lang: str = 'de') -> str:
    """
    Translate text from source language to target language using Google Translate.
    
    Args:
        text (str): Text to translate
        source_lang (str): Source language code (default: 'en')
        target_lang (str): Target language code (default: 'de')
        
    Returns:
        str: Translated text
    """
    logger = logging.getLogger('yt_germanizer')
    
    try:
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        translated = translator.translate(text)
        return translated
        
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        raise Exception(f"Translation error: {str(e)}")

def translate_segments(segments: List[Dict], source_lang: str = 'en', target_lang: str = 'de') -> List[Dict]:
    """
    Translate a list of text segments.
    
    Args:
        segments (List[Dict]): List of segments with text and timing information
        source_lang (str): Source language code (default: 'en')
        target_lang (str): Target language code (default: 'de')
        
    Returns:
        List[Dict]: List of segments with translated text
    """
    logger = logging.getLogger('yt_germanizer')
    translated_segments = []
    
    try:
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        
        for segment in segments:
            # Translate the text while preserving timing information
            translated_text = translator.translate(segment['text'])
            translated_segments.append({
                'text': translated_text,
                'start': segment['start'],
                'end': segment['end']
            })
            
        return translated_segments
        
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        raise Exception(f"Translation error: {str(e)}")
