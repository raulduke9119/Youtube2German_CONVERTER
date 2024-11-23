# Getting Started with YouTube Germanizer

This guide will walk you through setting up and using YouTube Germanizer to create German versions of your YouTube videos.

## Prerequisites

Before installation, ensure you have:
- Python 3.8 or higher installed
- FFmpeg installed and accessible from command line
- An AssemblyAI API key (sign up at [AssemblyAI](https://www.assemblyai.com))
- At least 4GB of available RAM
- Stable internet connection

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/youtube-germanizer.git
   cd youtube-germanizer
   ```

2. **Set Up Python Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure API Keys**
   Create a `.env` file in the project root:
   ```
   ASSEMBLYAI_API_KEY=your_assemblyai_api_key
   ```

## Usage Options

### 1. GUI Interface (Recommended)
```bash
python app.py
```
- Launch the graphical interface
- Paste your YouTube URL
- Select output quality and options
- Click "Start Processing"

### 2. Command Line Interface
```bash
python main.py <youtube_url> [--quality QUALITY]
```
Example:
```bash
python main.py https://youtube.com/watch?v=example --quality 192
```

## Processing Steps

1. **Video Download**
   - Downloads video using yt-dlp
   - Extracts audio in high quality
   - Saves in data/input directory

2. **Transcription**
   - Uploads audio to AssemblyAI
   - Receives timestamped transcription
   - Processes speaker segments

3. **Translation**
   - Translates text to German
   - Preserves timing information
   - Maintains speaker context

4. **Voice Generation**
   - Generates natural German speech
   - Matches original timing
   - Adjusts speech rate if needed

5. **Video Assembly**
   - Combines original video
   - Adds German audio track
   - Synchronizes perfectly

## Configuration Options

### Audio Quality Settings
```python
# In config.py or via CLI
AUDIO_QUALITY = '192'  # Options: 64, 128, 192, 256
TTS_VOICE_TYPE = 'male'  # Options: male, female
SPEECH_RATE = 1.0  # Default speech rate
```

### Translation Settings
```python
TRANSLATION_QUALITY = 'high'  # Options: fast, balanced, high
TARGET_DIALECT = 'DE'  # German (Default)
```

## Troubleshooting

### Common Issues

1. **Installation Problems**
   - Ensure all dependencies are installed:
     ```bash
     pip install -r requirements.txt --upgrade
     ```
   - Verify FFmpeg installation:
     ```bash
     ffmpeg -version
     ```

2. **Processing Errors**
   - Check API key validity
   - Ensure sufficient disk space
   - Verify internet connection
   - Check Python version compatibility

3. **Quality Issues**
   - Try higher audio quality settings
   - Adjust speech rate for better sync
   - Use high-quality translation mode

### Error Messages

- `FFmpeg not found`: Install FFmpeg
- `API Key Invalid`: Check .env file
- `Memory Error`: Free up system RAM
- `Processing Failed`: Check logs in data/logs

## Best Practices

1. **Input Video Selection**
   - Use videos with clear audio
   - Avoid videos with complex background noise
   - Check video length (longer = more processing time)

2. **Resource Management**
   - Close unnecessary applications
   - Monitor CPU and RAM usage
   - Keep sufficient disk space

3. **Quality Control**
   - Preview generated audio
   - Check translation accuracy
   - Verify audio synchronization

## Getting Help

Need assistance? Try these steps:
1. Check the error message in logs
2. Search existing issues
3. Create a new issue with:
   - Error message
   - Steps to reproduce
   - System information
