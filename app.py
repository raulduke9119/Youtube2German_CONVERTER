import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

from src.audio_processing import download_audio
from src.transcription import transcribe_audio
from src.tts_generation import generate_tts
from src.video_sync import sync_audio_with_video
from src.utils import setup_logging, clean_filename, get_video_id, translate_segments
from src import config

# Set page configuration
st.set_page_config(
    page_title="YouTube Germanizer",
    page_icon="🎥",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    /* Modern color scheme and overall styling */
    :root {
        --primary-color: #4F46E5;
        --secondary-color: #7C3AED;
        --success-color: #059669;
        --error-color: #DC2626;
        --background-color: #F9FAFB;
        --text-color: #1F2937;
    }

    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
    }

    /* Header styling */
    .main-title {
        background: linear-gradient(120deg, var(--primary-color), var(--secondary-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 3.5em;
        font-weight: 800;
        margin: 1em 0;
        padding: 0.5em;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }

    /* Input fields styling */
    .stTextInput input {
        border-radius: 10px;
        border: 2px solid #E5E7EB;
        padding: 0.75em 1em;
        transition: all 0.3s ease;
    }

    .stTextInput input:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.2);
    }

    /* Button styling */
    .stButton button {
        border-radius: 10px;
        padding: 0.75em 2em;
        font-weight: 600;
        transition: all 0.3s ease;
        background: linear-gradient(120deg, var(--primary-color), var(--secondary-color));
        border: none;
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
    }

    /* Status boxes styling */
    .status-box {
        padding: 1.25em;
        border-radius: 12px;
        margin: 1.5em 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        animation: fadeIn 0.5s ease-in-out;
    }

    .success {
        background-color: #ECFDF5;
        color: var(--success-color);
        border-left: 4px solid var(--success-color);
    }

    .error {
        background-color: #FEF2F2;
        color: var(--error-color);
        border-left: 4px solid var(--error-color);
    }

    .info {
        background-color: #EEF2FF;
        color: var(--primary-color);
        border-left: 4px solid var(--primary-color);
    }

    /* Sidebar styling */
    .css-1d391kg {
        background-color: #FFFFFF;
        border-right: 1px solid #E5E7EB;
        padding: 2em 1em;
    }

    .css-1d391kg .stSelectbox label {
        color: var(--text-color);
        font-weight: 600;
    }

    /* Progress bar styling */
    .stProgress > div > div {
        background-color: var(--primary-color);
        border-radius: 999px;
        height: 8px;
    }

    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Download button styling */
    .stDownloadButton button {
        background: var(--success-color);
        color: white;
        border-radius: 10px;
        padding: 0.75em 2em;
        font-weight: 600;
        transition: all 0.3s ease;
        margin-top: 1em;
        width: 100%;
    }

    .stDownloadButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.2);
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #FFFFFF;
        border-radius: 10px;
        border: 1px solid #E5E7EB;
        padding: 1em;
        font-weight: 600;
    }

    /* Footer styling */
    footer {
        margin-top: 2em;
        padding: 1em;
        text-align: center;
        border-top: 1px solid #E5E7EB;
    }
    
    /* Progress Animation Styles */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    @keyframes slideIn {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes fadeInUp {
        from { transform: translateY(20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Progress Step Container */
    .progress-step {
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.2);
        animation: fadeInUp 0.5s ease forwards;
    }
    
    .progress-step.active {
        border: 1px solid var(--primary-color);
        animation: pulse 2s infinite;
    }
    
    .progress-step.completed {
        border-color: var(--success-color);
        background: linear-gradient(135deg, rgba(5, 150, 105, 0.1), rgba(5, 150, 105, 0.05));
    }
    
    /* Progress Icons */
    .progress-icon {
        font-size: 1.5em;
        margin-right: 0.5em;
        display: inline-block;
    }
    
    .progress-icon.spin {
        animation: spin 2s linear infinite;
    }
    
    /* Progress Details */
    .progress-details {
        margin-top: 0.5rem;
        font-size: 0.9em;
        color: rgba(255,255,255,0.7);
        padding-left: 2.5rem;
    }
    
    /* Progress Bar Enhancement */
    .stProgress > div > div {
        background: linear-gradient(90deg, 
            var(--primary-color) 0%, 
            var(--secondary-color) 50%, 
            var(--primary-color) 100%);
        background-size: 200% 100%;
        animation: gradientMove 2s linear infinite;
    }
    
    @keyframes gradientMove {
        0% { background-position: 100% 0%; }
        100% { background-position: -100% 0%; }
    }
    
    /* Status Message Styles */
    .status-message {
        display: flex;
        align-items: center;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        animation: slideIn 0.5s ease;
    }
    
    .status-message.info {
        background: linear-gradient(135deg, rgba(79, 70, 229, 0.1), rgba(79, 70, 229, 0.05));
        border-left: 4px solid var(--primary-color);
    }
    
    .status-message.success {
        background: linear-gradient(135deg, rgba(5, 150, 105, 0.1), rgba(5, 150, 105, 0.05));
        border-left: 4px solid var(--success-color);
    }
    
    .status-message.error {
        background: linear-gradient(135deg, rgba(220, 38, 38, 0.1), rgba(220, 38, 38, 0.05));
        border-left: 4px solid var(--error-color);
    }
    </style>
""", unsafe_allow_html=True)

def create_progress_step(icon: str, title: str, details: str, status: str = "waiting"):
    """Helper function to create a progress step with consistent styling"""
    class_name = {
        "waiting": "",
        "active": "active",
        "completed": "completed",
        "error": "error"
    }.get(status, "")
    
    icon_class = "spin" if status == "active" else ""
    
    return f"""
    <div class="progress-step {class_name}">
        <div class="progress-icon {icon_class}">{icon}</div>
        <strong>{title}</strong>
        <div class="progress-details">{details}</div>
    </div>
    """

def main():
    # Header with animation
    st.markdown("<h1 class='main-title'>🎥 YouTube Germanizer</h1>", unsafe_allow_html=True)
    
    # Sidebar configuration with better organization
    st.sidebar.markdown("### ⚙️ Configuration")
    st.sidebar.markdown("---")
    
    # API Key input in sidebar with better explanation
    api_key = st.sidebar.text_input(
        "AssemblyAI API Key",
        value=os.getenv('ASSEMBLYAI_API_KEY', ''),
        type="password",
        help="Your AssemblyAI API key is required for audio transcription"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎚️ Quality Settings")
    
    # Quality settings in sidebar with tooltips
    audio_quality = st.sidebar.select_slider(
        "Audio Quality",
        options=['64', '128', '192', '256', '320'],
        value='192',
        help="Higher quality means better audio but larger file size"
    )
    
    # Advanced settings expander in sidebar
    with st.sidebar.expander("🔧 Advanced Settings"):
        tts_speed = st.checkbox(
            "Slow TTS",
            value=False,
            help="Slow down the German speech for better clarity"
        )
        video_preset = st.select_slider(
            "Video Encoding Speed",
            options=['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow'],
            value='medium',
            help="Faster encoding = lower quality, Slower encoding = better quality"
        )
    
    # Main content area with better organization
    st.markdown("### 🎬 Enter YouTube Video URL")
    video_url = st.text_input(
        "",
        placeholder="https://www.youtube.com/watch?v=...",
        help="Paste your YouTube video URL here"
    )
    
    # Process button with loading state
    if st.button("🚀 Start Germanizing", type="primary"):
        if not api_key:
            st.error("⚠️ Please enter your AssemblyAI API Key in the sidebar")
            return
        
        if not video_url:
            st.error("⚠️ Please enter a YouTube video URL")
            return
        
        try:
            # Create progress containers
            progress_placeholder = st.empty()
            status_placeholder = st.empty()
            progress_bar = st.progress(0)
            
            # Initialize progress steps
            steps_placeholder = st.container()
            with steps_placeholder:
                col1, col2 = st.columns([3, 1])
                with col1:
                    # Step 1: Download
                    status_placeholder.markdown(
                        create_progress_step(
                            "📥",
                            "Downloading Video Audio",
                            "Extracting high-quality audio from YouTube video...",
                            "active"
                        ),
                        unsafe_allow_html=True
                    )
                with col2:
                    st.metric("Progress", "0%")
                
            video_id = get_video_id(video_url)
            audio_path = download_audio(video_url, config.TEMP_DIR)
            progress_bar.progress(20)
            
            # Update status and show completed step 1
            with steps_placeholder:
                col1, col2 = st.columns([3, 1])
                with col1:
                    status_placeholder.markdown(
                        create_progress_step(
                            "✅",
                            "Audio Download Complete",
                            f"Successfully extracted audio from video ID: {video_id}",
                            "completed"
                        ) +
                        create_progress_step(
                            "🎯",
                            "Transcribing Audio",
                            "Converting speech to text with speaker detection...",
                            "active"
                        ),
                        unsafe_allow_html=True
                    )
                with col2:
                    st.metric("Progress", "20%")
            
            # Step 2: Transcribe
            transcript = transcribe_audio(audio_path, api_key)
            progress_bar.progress(40)
            
            # Update status and show completed step 2
            with steps_placeholder:
                col1, col2 = st.columns([3, 1])
                with col1:
                    status_placeholder.markdown(
                        create_progress_step(
                            "✅",
                            "Audio Download Complete",
                            f"Successfully extracted audio from video ID: {video_id}",
                            "completed"
                        ) +
                        create_progress_step(
                            "✅",
                            "Transcription Complete",
                            f"Processed {len(transcript)} segments of speech",
                            "completed"
                        ) +
                        create_progress_step(
                            "🗣️",
                            "Generating German Speech",
                            "Creating natural-sounding German audio...",
                            "active"
                        ),
                        unsafe_allow_html=True
                    )
                with col2:
                    st.metric("Progress", "40%")
            
            # Step 3: Generate TTS
            tts_output = generate_tts(transcript, config.TTS_DIR)
            progress_bar.progress(60)
            
            # Update status and show completed step 3
            with steps_placeholder:
                col1, col2 = st.columns([3, 1])
                with col1:
                    status_placeholder.markdown(
                        create_progress_step(
                            "✅",
                            "Audio Download Complete",
                            f"Successfully extracted audio from video ID: {video_id}",
                            "completed"
                        ) +
                        create_progress_step(
                            "✅",
                            "Transcription Complete",
                            f"Processed {len(transcript)} segments of speech",
                            "completed"
                        ) +
                        create_progress_step(
                            "✅",
                            "German Speech Generated",
                            "Created natural German voice audio",
                            "completed"
                        ) +
                        create_progress_step(
                            "🎵",
                            "Syncing Audio with Video",
                            "Matching speech timing with video...",
                            "active"
                        ),
                        unsafe_allow_html=True
                    )
                with col2:
                    st.metric("Progress", "60%")
            
            # Step 4: Sync audio
            output_path = sync_audio_with_video(video_url, tts_output, config.OUTPUT_DIR)
            progress_bar.progress(100)
            
            # Show all completed steps
            with steps_placeholder:
                col1, col2 = st.columns([3, 1])
                with col1:
                    status_placeholder.markdown(
                        create_progress_step(
                            "✅",
                            "Audio Download Complete",
                            f"Successfully extracted audio from video ID: {video_id}",
                            "completed"
                        ) +
                        create_progress_step(
                            "✅",
                            "Transcription Complete",
                            f"Processed {len(transcript)} segments of speech",
                            "completed"
                        ) +
                        create_progress_step(
                            "✅",
                            "German Speech Generated",
                            "Created natural German voice audio",
                            "completed"
                        ) +
                        create_progress_step(
                            "✅",
                            "Audio Syncing Complete",
                            "Successfully merged German audio with video",
                            "completed"
                        ),
                        unsafe_allow_html=True
                    )
                with col2:
                    st.metric("Progress", "100%")
            
            # Success message with animation
            st.success("✨ Processing complete! Your video is ready to download.")
            
            # Attractive download button with animation
            with open(output_path, 'rb') as file:
                st.download_button(
                    label="📥 Download Your Germanized Video",
                    data=file,
                    file_name=f"germanized_{video_id}.mp4",
                    mime="video/mp4"
                )
            
        except Exception as e:
            # Error message with details
            error_message = f"""
            <div class="status-message error">
                <div style="flex-grow: 1">
                    <strong>❌ Error occurred</strong><br>
                    <small>{str(e)}</small>
                </div>
            </div>
            """
            st.markdown(error_message, unsafe_allow_html=True)
            return
    
    # Instructions with better organization
    with st.expander("ℹ️ How to use YouTube Germanizer"):
        st.markdown("""
        1. 🔑 Enter your AssemblyAI API key in the sidebar
        2. 📋 Paste a YouTube video URL in the input field
        3. ⚙️ Adjust quality settings in the sidebar if needed
        4. 🚀 Click 'Start Germanizing' to begin
        5. ⏳ Wait for processing to complete
        6. 📥 Download your Germanized video
        
        **Tips:**
        - Higher audio quality gives better results but larger files
        - Use slow TTS if you want clearer German pronunciation
        - For best video quality, use 'slower' encoding (takes more time)
        """)
    
    # Footer with better styling
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #6B7280; padding: 1em;'>"
        "Made with ❤️ by the YouTube Germanizer team | "
        "<a href='https://github.com/yourgithub/yt-germanizer/issues' style='color: #4F46E5; text-decoration: none;'>Report an issue</a>"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
