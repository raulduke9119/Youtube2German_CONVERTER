import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import threading
from PIL import Image
import os
from dotenv import load_dotenv

# Import existing functionality
from src.audio_processing import download_audio
from src.transcription import transcribe_audio
from src.tts_generation import generate_tts
from src.video_sync import sync_audio_with_video
from src.utils import setup_logging, clean_filename, get_video_id
from src import config

# Load environment variables
load_dotenv()

class YouTubeGermanizerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("YouTube Germanizer")
        self.geometry("1100x700")
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create sidebar frame
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        # App logo/title
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="YouTube\nGermanizer", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # API Key input
        self.api_key_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="AssemblyAI API Key:",
            anchor="w"
        )
        self.api_key_label.grid(row=1, column=0, padx=20, pady=(10, 0))
        
        self.api_key_entry = ctk.CTkEntry(
            self.sidebar_frame,
            placeholder_text="Enter API Key",
            show="•"
        )
        self.api_key_entry.grid(row=2, column=0, padx=20, pady=(0, 10))
        self.api_key_entry.insert(0, os.getenv('ASSEMBLYAI_API_KEY', ''))
        
        # Quality settings
        self.quality_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Audio Quality:",
            anchor="w"
        )
        self.quality_label.grid(row=3, column=0, padx=20, pady=(10, 0))
        
        self.quality_option = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["64 kbps", "128 kbps", "192 kbps", "256 kbps", "320 kbps"],
            command=self.change_quality
        )
        self.quality_option.grid(row=4, column=0, padx=20, pady=(0, 10))
        self.quality_option.set("192 kbps")
        
        # Advanced settings
        self.advanced_frame = ctk.CTkFrame(self.sidebar_frame)
        self.advanced_frame.grid(row=5, column=0, padx=20, pady=10, sticky="ew")
        
        self.slow_tts = ctk.CTkSwitch(
            self.advanced_frame,
            text="Slow TTS",
            command=self.toggle_tts_speed
        )
        self.slow_tts.grid(row=0, column=0, padx=20, pady=10)
        
        self.encoding_label = ctk.CTkLabel(
            self.advanced_frame,
            text="Encoding Speed:",
            anchor="w"
        )
        self.encoding_label.grid(row=1, column=0, padx=20, pady=(10, 0))
        
        self.encoding_option = ctk.CTkOptionMenu(
            self.advanced_frame,
            values=["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"],
            command=self.change_encoding
        )
        self.encoding_option.grid(row=2, column=0, padx=20, pady=(0, 10))
        self.encoding_option.set("medium")
        
        # Main content area
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)
        
        # URL input
        self.url_frame = ctk.CTkFrame(self.main_frame)
        self.url_frame.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="ew")
        self.url_frame.grid_columnconfigure(0, weight=1)
        
        self.url_label = ctk.CTkLabel(
            self.url_frame,
            text="YouTube Video URL:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.url_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        
        self.url_entry = ctk.CTkEntry(
            self.url_frame,
            placeholder_text="https://www.youtube.com/watch?v=..."
        )
        self.url_entry.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        # Start button
        self.start_button = ctk.CTkButton(
            self.url_frame,
            text="Start Germanizing",
            command=self.start_processing,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.start_button.grid(row=2, column=0, padx=10, pady=10)
        
        # Progress area
        self.progress_frame = ctk.CTkFrame(self.main_frame)
        self.progress_frame.grid(row=1, column=0, padx=20, pady=20, sticky="ew")
        self.progress_frame.grid_columnconfigure(0, weight=1)
        
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="Progress:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.progress_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(
            self.progress_frame,
            text="Ready to start...",
            font=ctk.CTkFont(size=13)
        )
        self.status_label.grid(row=2, column=0, padx=10, pady=(0, 10))
        
        # Status boxes
        self.status_boxes_frame = ctk.CTkFrame(self.main_frame)
        self.status_boxes_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.status_boxes_frame.grid_columnconfigure(0, weight=1)
        
        # Create status boxes for each step
        self.status_boxes = []
        steps = [
            ("📥 Download", "Waiting to start..."),
            ("🎯 Transcribe", "Waiting to start..."),
            ("🗣️ Generate TTS", "Waiting to start..."),
            ("🎵 Sync Audio", "Waiting to start...")
        ]
        
        for i, (title, status) in enumerate(steps):
            box = self.create_status_box(self.status_boxes_frame, title, status)
            box.grid(row=i, column=0, padx=10, pady=5, sticky="ew")
            self.status_boxes.append(box)
        
        # Initialize processing state
        self.processing = False
        self.current_step = 0
    
    def create_status_box(self, parent, title, status):
        frame = ctk.CTkFrame(parent)
        frame.grid_columnconfigure(1, weight=1)
        
        title_label = ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=10, pady=5)
        
        status_label = ctk.CTkLabel(
            frame,
            text=status,
            font=ctk.CTkFont(size=12)
        )
        status_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        frame.title_label = title_label
        frame.status_label = status_label
        return frame
    
    def update_status_box(self, index, status, is_active=False, is_complete=False):
        box = self.status_boxes[index]
        box.status_label.configure(text=status)
        
        if is_active:
            box.configure(fg_color=("gray85", "gray25"))
        elif is_complete:
            box.configure(fg_color=("#D4EDDA", "#1B4332"))
        else:
            box.configure(fg_color=("gray80", "gray20"))
    
    def change_quality(self, value):
        # Strip "kbps" from value
        self.audio_quality = value.split()[0]
    
    def toggle_tts_speed(self):
        pass  # Will be implemented when needed
    
    def change_encoding(self, value):
        self.encoding_preset = value
    
    def update_progress(self, value, status):
        self.progress_bar.set(value)
        self.status_label.configure(text=status)
        self.update()
    
    def start_processing(self):
        if self.processing:
            return
        
        # Validate inputs
        api_key = self.api_key_entry.get()
        video_url = self.url_entry.get()
        
        if not api_key:
            messagebox.showerror("Error", "Please enter your AssemblyAI API Key")
            return
        
        if not video_url:
            messagebox.showerror("Error", "Please enter a YouTube video URL")
            return
        
        # Start processing in a separate thread
        self.processing = True
        self.start_button.configure(state="disabled")
        threading.Thread(target=self.process_video, args=(api_key, video_url), daemon=True).start()
    
    def process_video(self, api_key, video_url):
        try:
            # Step 1: Download
            self.update_progress(0.0, "Downloading video audio...")
            self.update_status_box(0, "Downloading...", is_active=True)
            
            video_id = get_video_id(video_url)
            audio_path = download_audio(video_url, config.TEMP_DIR)
            
            self.update_progress(0.25, "Audio downloaded successfully")
            self.update_status_box(0, "Complete ✓", is_complete=True)
            
            # Step 2: Transcribe
            self.update_progress(0.25, "Transcribing audio...")
            self.update_status_box(1, "Transcribing...", is_active=True)
            
            transcript = transcribe_audio(audio_path, api_key)
            
            self.update_progress(0.5, "Transcription complete")
            self.update_status_box(1, "Complete ✓", is_complete=True)
            
            # Step 3: Generate TTS
            self.update_progress(0.5, "Generating German speech...")
            self.update_status_box(2, "Generating...", is_active=True)
            
            tts_output = generate_tts(transcript, config.TTS_DIR)
            
            self.update_progress(0.75, "TTS generation complete")
            self.update_status_box(2, "Complete ✓", is_complete=True)
            
            # Step 4: Sync audio
            self.update_progress(0.75, "Syncing audio with video...")
            self.update_status_box(3, "Syncing...", is_active=True)
            
            output_path = sync_audio_with_video(video_url, tts_output, config.OUTPUT_DIR)
            
            self.update_progress(1.0, "Processing complete!")
            self.update_status_box(3, "Complete ✓", is_complete=True)
            
            # Show success message and open folder
            if messagebox.askyesno(
                "Success",
                "Video processing complete! Would you like to open the output folder?"
            ):
                os.startfile(str(config.OUTPUT_DIR))
        
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.update_progress(0, "Error occurred")
        
        finally:
            self.processing = False
            self.start_button.configure(state="normal")

if __name__ == "__main__":
    app = YouTubeGermanizerGUI()
    app.mainloop()
