# YouTube Germanizer

An AI-powered tool that automatically creates German versions of YouTube videos using AssemblyAI for transcription, deep-translator for translation, and TTS for German voiceover generation.

## Overview

YouTube Germanizer is a powerful tool that helps content creators reach German-speaking audiences by automatically:
- Extracting and transcribing audio from YouTube videos using AssemblyAI
- Translating content to German using deep-translator
- Generating natural German voiceovers with TTS (Text-to-Speech)
- Creating a new video with synchronized German audio and subtitles

## Quick Start

See our [Get Started Guide](get_started.md) for detailed setup and usage instructions.

## Key Features

- 🎥 Smart YouTube video download using yt-dlp
- 🎯 High-accuracy transcription with AssemblyAI
- 🔄 Neural machine translation to German
- 🗣️ High-quality TTS synthesis using TTS library
- 🎬 Precise audio-video synchronization with moviepy
- 🖥️ User-friendly GUI built with customtkinter
- 📊 Progress tracking and logging
- ⚡ Efficient audio processing with pydub

## Requirements

- Python 3.8 or higher
- FFmpeg (for audio/video processing)
- AssemblyAI API key
- 4GB+ RAM recommended
- Internet connection

## Tech Stack

- **Audio Processing**: FFmpeg, pydub
- **Video Processing**: moviepy, yt-dlp
- **AI/ML**: AssemblyAI, TTS, deep-translator
- **UI**: customtkinter, Pillow
- **Core**: Python 3.8+, torch

## Project Structure

```
asssymbleytgeramniz/
├── src/               # Core source code
├── data/              # Input/output data
├── app.py            # Main application
├── gui.py            # GUI implementation
├── main.py           # CLI interface
└── requirements.txt  # Dependencies
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions:
1. Check the troubleshooting section in get_started.md
2. Open an issue in the repository
3. Join our community discussions
