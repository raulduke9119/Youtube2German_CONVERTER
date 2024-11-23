import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# Base directories
BASE_DIR = PROJECT_ROOT
DATA_DIR = BASE_DIR / 'data'

# Input/Output directories
INPUT_DIR = DATA_DIR / 'input'
OUTPUT_DIR = DATA_DIR / 'output'
TTS_DIR = DATA_DIR / 'tts'
TEMP_DIR = DATA_DIR / 'temp'
LOG_DIR = DATA_DIR / 'logs'

# File formats
AUDIO_FORMAT = 'mp3'
VIDEO_FORMAT = 'mp4'
TEMP_AUDIO_FORMAT = 'm4a'

# Create directories if they don't exist
for directory in [INPUT_DIR, OUTPUT_DIR, TTS_DIR, TEMP_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# File paths
LOG_FILE = LOG_DIR / 'yt_germanizer.log'

# AssemblyAI configuration
ASSEMBLYAI_LANGUAGE_CODE = 'en'  # Source language code
ASSEMBLYAI_FEATURES = {
    'speaker_labels': True,
    'auto_chapters': True,
    'entity_detection': True
}

# TTS configuration
TTS_LANGUAGE = 'de'  # Target language (German)
TTS_SLOW = False     # Normal speed
TTS_QUALITY = '192'  # Audio quality in kbps
TTS_TLD = 'de'      # Top-level domain for German Google TTS

# Audio processing configuration
AUDIO_BITRATE = '192k'

# Video processing configuration
VIDEO_CODEC = 'libx264'
AUDIO_CODEC = 'aac'
VIDEO_BITRATE = '4000k'
VIDEO_PRESET = 'medium'  # Encoding preset (ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow)

# Threading configuration
MAX_WORKERS = os.cpu_count() or 4  # Number of worker threads for parallel processing

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# Cache configuration
CACHE_DIR = DATA_DIR / 'cache'
CACHE_EXPIRY = 24 * 60 * 60  # 24 hours in seconds
