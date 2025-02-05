"""Modern GUI interface for the Mafia Wiki Scraper."""
import asyncio
import os
import sys
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog
import json
import subprocess
import threading
import webbrowser
from typing import Optional
import queue

import customtkinter as ctk
from PIL import Image, ImageTk
import pygame.mixer

from .scraper import WikiScraper

# Set theme and color scheme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Color scheme
COLORS = {
    'primary': '#D90416',     # Main red
    'primary_dark': '#C20626',# Darker red
    'secondary': '#C20626',   # Darker red
    'white': '#FFFFFF',       # Pure white
    'dark_gray': '#232323',   # Dark gray
    'black': '#0D0D0D',       # Almost black
    'amber': '#FFB000',       # Rich amber for inspection
    'orange': '#FF8C42',      # Warm orange for fetching
    'emerald': '#50C878',     # Classic emerald for scraping
}

class AnimatedProgressBar(ctk.CTkProgressBar):
    """Progress bar with pulsing animation."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pulsing = False
        self.pulse_direction = 1
        self.pulse_value = 0
        
    def pulse(self):
        """Create a pulsing animation effect."""
        if not self.pulsing:
            return
        
        # Update pulse value
        self.pulse_value += 0.02 * self.pulse_direction
        if self.pulse_value >= 1:
            self.pulse_value = 1
            self.pulse_direction = -1
        elif self.pulse_value <= 0:
            self.pulse_value = 0
            self.pulse_direction = 1
        
        self.set(self.pulse_value)
        if self.pulsing:
            self.after(20, self.pulse)

class MafiaWikiScraperGUI(ctk.CTk):
    """Main GUI window for the Mafia Wiki Scraper."""
    
    def __init__(self):
        """Initialize the GUI."""
        super().__init__()
        
        # Initialize pygame mixer for sound effects
        pygame.mixer.init()
        
        # Load sound effects
        self.sounds = {
            'hover': pygame.mixer.Sound(str(Path(__file__).parent / 'resources' / 'hover.wav')),
            'click': pygame.mixer.Sound(str(Path(__file__).parent / 'resources' / 'click.wav')),
            'success': pygame.mixer.Sound(str(Path(__file__).parent / 'resources' / 'success.wav')),
            'error': pygame.mixer.Sound(str(Path(__file__).parent / 'resources' / 'error.wav')),
        }
        
        # Initialize variables
        self.scraping = False
        self.current_output_file = None
        self.base_url = "https://bnb-mafia.gitbook.io/bnb-mafia"
        self.output_dir = tk.StringVar()  # Add output directory variable
        
        # Setup async event loop in a separate thread
        self.async_queue = queue.Queue()
        self.loop = asyncio.new_event_loop()
        self.async_thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self.async_thread.start()
        
        # Configure window
        self.title("Mafia Wiki Scraper")
        self.geometry("1000x700")
        self.configure(fg_color=COLORS['black'])
        
        # Center the window
        self.center_window()
        
        # Load and save settings
        self.settings_file = Path.home() / ".mafia_scraper_settings.json"
        self.settings = self.load_settings()
        
        # Create main container with gradient background
        self.container = ctk.CTkFrame(self, fg_color=COLORS['black'])
        self.container.pack(fill="both", expand=True)
        
        # Create header with dark background
        self.header_frame = ctk.CTkFrame(self.container, fg_color=COLORS['black'], height=200)
        self.header_frame.pack(fill="x", padx=40, pady=(40, 20))
        self.header_frame.pack_propagate(False)  # Force height
        
        # Load and display logo
        logo_path = Path(__file__).parent / 'resources' / 'logo.png'
        try:
            # Load and resize logo
            original_image = Image.open(logo_path)
            
            # Calculate size for header while maintaining aspect ratio
            target_height = 160
            aspect_ratio = original_image.width / original_image.height
            new_width = int(target_height * aspect_ratio)
            
            # Resize image
            logo_image = original_image.resize(
                (new_width, target_height),
                Image.Resampling.LANCZOS
            )
            
            # Create logo container frame with black background
            logo_frame = ctk.CTkFrame(
                self.header_frame,
                fg_color=COLORS['black'],
                width=new_width,
                height=target_height
            )
            logo_frame.pack(side="left", padx=(20, 0))
            logo_frame.pack_propagate(False)
            
            # Display logo
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = ctk.CTkLabel(
                logo_frame,
                image=self.logo_photo,
                text="",
                fg_color=COLORS['black']
            )
            logo_label.pack(expand=True)
            
            # Add vertical separator
            separator = ctk.CTkFrame(
                self.header_frame,
                width=2,
                height=140,
                fg_color=COLORS['primary']
            )
            separator.pack(side="left", padx=40, fill="y")
            
        except Exception as e:
            print(f"Error loading logo: {e}")
            
        # Add title frame
        title_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        title_frame.pack(side="left", fill="y", expand=True)
        
        # Add title with custom font
        title = ctk.CTkLabel(
            title_frame,
            text="WIKI SCRAPER",
            font=ctk.CTkFont(family="Copperplate", size=48, weight="bold"),
            text_color=COLORS['primary']
        )
        title.pack(anchor="w", pady=(20, 0))
        
        # Add subtitle
        subtitle = ctk.CTkLabel(
            title_frame,
            text="Extract knowledge from the underworld",
            font=ctk.CTkFont(size=16),
            text_color=COLORS['white']
        )
        subtitle.pack(anchor="w")
        
        # Create content frame
        self.content_frame = ctk.CTkFrame(self.container, fg_color=COLORS['dark_gray'])
        self.content_frame.pack(fill="both", expand=True, padx=40, pady=(0, 40))
        
        # Setup UI components
        self.setup_directory_frame()
        self.setup_progress_section()
        self.setup_control_buttons()

    def setup_directory_frame(self):
        """Setup the directory selection frame."""
        dir_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        dir_frame.pack(fill="x", padx=20, pady=20)
        
        dir_label = ctk.CTkLabel(
            dir_frame,
            text="Output Directory:",
            font=("Optima", 14)
        )
        dir_label.pack(side="left", padx=(0, 10))
        
        self.dir_entry = ctk.CTkEntry(
            dir_frame,
            width=400,
            placeholder_text="Select output directory..."
        )
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.dir_entry.insert(0, self.settings.get('last_directory', str(Path.home() / "MafiaWikiOutput")))
        
        dir_button = ctk.CTkButton(
            dir_frame,
            text="Browse",
            width=100,
            command=self.browse_directory,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary']
        )
        dir_button.pack(side="right")

    def setup_progress_section(self):
        """Setup the progress bars."""
        # Create frame for progress bars
        progress_frame = ctk.CTkFrame(self.content_frame, fg_color=COLORS['black'])
        progress_frame.pack(fill="x", padx=20, pady=(10, 0))

        # Create inspection progress bar
        inspection_label = ctk.CTkLabel(
            progress_frame,
            text="INSPECTING WIKI",
            text_color=COLORS['amber'],
            font=("Inter", 12, "bold")
        )
        inspection_label.pack(fill="x")
        self.inspection_progress = AnimatedProgressBar(
            progress_frame,
            fg_color=COLORS['black'],
            progress_color=COLORS['amber']
        )
        self.inspection_progress.pack(fill="x", pady=(0, 10))

        # Create fetching progress bar
        fetching_label = ctk.CTkLabel(
            progress_frame,
            text="FETCHING PAGES",
            text_color=COLORS['orange'],
            font=("Inter", 12, "bold")
        )
        fetching_label.pack(fill="x")
        self.fetching_progress = AnimatedProgressBar(
            progress_frame,
            fg_color=COLORS['black'],
            progress_color=COLORS['orange']
        )
        self.fetching_progress.pack(fill="x", pady=(0, 10))

        # Create scraping progress bar
        scraping_label = ctk.CTkLabel(
            progress_frame,
            text="SCRAPING CONTENT",
            text_color=COLORS['emerald'],
            font=("Inter", 12, "bold")
        )
        scraping_label.pack(fill="x")
        self.progress_bar = AnimatedProgressBar(
            progress_frame,
            fg_color=COLORS['black'],
            progress_color=COLORS['emerald']
        )
        self.progress_bar.pack(fill="x", pady=(0, 10))

        # Add status label with elegant font
        self.status_label = ctk.CTkLabel(
            progress_frame,
            text="Ready to start scraping...",
            font=("Optima", 14),
            text_color=COLORS['white']
        )
        self.status_label.pack(pady=(10, 0))

    def setup_control_buttons(self):
        """Setup the control buttons."""
        button_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.scrape_button = ctk.CTkButton(
            button_frame,
            text="Start Scraping",
            font=("Optima", 16, "bold"),
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary'],
            command=self.start_scraping
        )
        self.scrape_button.pack(side="left", padx=(0, 10))

        # Add stats frame
        self.stats_frame = ctk.CTkFrame(self.content_frame, fg_color=COLORS['black'])
        self.stats_frame.pack(fill="x", padx=20, pady=20)
        
        self.pages_label = ctk.CTkLabel(
            self.stats_frame,
            text="Pages Scraped: 0",
            font=("Optima", 14),
            text_color=COLORS['white']
        )
        self.pages_label.pack(side="left", padx=20, pady=10)
        
        self.time_label = ctk.CTkLabel(
            self.stats_frame,
            text="Time Elapsed: 0:00",
            font=("Optima", 14),
            text_color=COLORS['white']
        )
        self.time_label.pack(side="right", padx=20, pady=10)
        
        # Add output file frame
        self.output_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.output_frame.pack(fill="x", padx=20, pady=20)
        
        self.output_label = ctk.CTkLabel(
            self.output_frame,
            text="",
            font=("Optima", 14),
            text_color=COLORS['white']
        )
        self.output_label.pack(side="left", padx=20)
        
        self.open_button = ctk.CTkButton(
            self.output_frame,
            text="Open File",
            width=100,
            command=self.open_output_file,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary']
        )
        self.open_button.pack(side="right", padx=20)
        self.open_button.configure(state="disabled")

    def play_sound(self, sound_name: str):
        """Play a sound effect."""
        try:
            self.sounds[sound_name].play()
        except:
            pass
    
    def center_window(self):
        """Center the window on the screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def load_settings(self):
        """Load settings from file."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    if "last_directory" in settings:
                        self.output_dir.set(settings["last_directory"])
                    return settings
        except Exception as e:
            print(f"Error loading settings: {e}")
        return {"last_directory": ""}

    def save_settings(self):
        """Save settings to file."""
        settings = {
            "last_directory": self.output_dir.get()
        }
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def browse_directory(self):
        """Open directory browser and update the output directory."""
        current_dir = self.output_dir.get() or os.getcwd()
        directory = filedialog.askdirectory(
            initialdir=current_dir,
            title="Select Output Directory"
        )
        if directory:
            self.output_dir.set(directory)
            self.settings["last_directory"] = directory
            self.save_settings()
    
    def update_status(self, text: str, error: bool = False):
        """Update status label in a thread-safe way."""
        self.after(0, lambda: self.status_label.configure(
            text=text,
            text_color=COLORS['primary'] if error else COLORS['white']
        ))

    def update_inspection_progress(self, current: int, total: int):
        """Update inspection progress bar in a thread-safe way."""
        if total > 0:
            progress = current / total
            self.after(0, lambda: (
                self.inspection_progress.set(progress),
                self.update_status(f"Inspecting wiki... ({current}/{total} pages)")
            ))

    def update_fetching_progress(self, current: int, total: int):
        """Update fetching progress bar in a thread-safe way."""
        if total > 0:
            progress = current / total
            self.after(0, lambda: (
                self.fetching_progress.set(progress),
                self.update_status(f"Fetching page {current} of {total}")
            ))

    def update_progress(self, value: float):
        """Update all progress bars to the given value."""
        self.after(0, lambda: self._update_progress_safe(value))
        
    def _update_progress_safe(self, value: float):
        """Thread-safe progress bar update."""
        try:
            normalized = max(0, min(value, 100)) / 100
            self.inspection_progress.set(normalized)
            self.fetching_progress.set(normalized)
            self.progress_bar.set(normalized)
        except Exception as e:
            print(f"Error updating progress: {e}")

    def show_error(self, message: str):
        """Show an error message in the status label."""
        self.scraping = False
        self.scrape_button.configure(text="Start Scraping", state="normal")
        self.play_sound('error')
        self.status_label.configure(text=f"Error: {message}")
        self.update()  # Force update of GUI state

    def open_output_file(self):
        """Open the output file in the default text editor."""
        self.play_sound('click')
        if not self.current_output_file:
            return
        
        output_path = Path(self.current_output_file)
        if not output_path.exists():
            return
            
        if sys.platform == "darwin":  # macOS
            subprocess.run(["open", str(output_path)])
        elif sys.platform == "win32":  # Windows
            subprocess.run(["start", str(output_path)], shell=True)
        else:  # Linux and others
            subprocess.run(["xdg-open", str(output_path)])

    async def start_scraping(self):
        """Start or stop the scraping process."""
        if self.scraping:
            self.scraping = False
            self.scrape_button.configure(text="Start Scraping")
            return

        output_dir = self.output_dir.get()
        if not output_dir:
            self.show_error("Please select an output directory first")
            return

        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                self.show_error(f"Could not create output directory: {e}")
                return

        self.scraping = True
        self.scrape_button.configure(text="Stop Scraping")
        
        # Start the scraping process
        asyncio.run_coroutine_threadsafe(self._run_scraper(), self.loop)

    async def _run_scraper(self):
        """Run the scraper in the background."""
        if not self.output_dir.get():
            self.show_error("Please select an output directory first.")
            return

        self.scraping = True
        self.scrape_button.configure(text="Stop Scraping", state="normal")
        self.update()

        try:
            async with WikiScraper(self.base_url) as scraper:
                print("Starting scraping process...")  # Debug
                
                # Get all internal links
                total_links = 0
                async for current, total in scraper.get_all_internal_links():
                    total_links = total
                    self.update_progress((current / total) * 100)
                    self.update_status(f"Found {current} links in {self.base_url}")
                print(f"Found {total_links} total links")  # Debug

                # Fetch all pages
                pages = []
                async for current, total in scraper.fetch_pages_with_progress():
                    self.update_progress((current / total) * 100)
                    self.update_status(f"Fetching page {current} of {total}")
                print(f"Fetched all pages")  # Debug

                # Scrape all pages
                scraped_pages = []
                async for page in scraper.scrape_all_pages_with_progress():
                    scraped_pages.append(page)
                    current = len(scraped_pages)
                    total = total_links
                    self.update_progress((current / total) * 100)
                    self.update_status(f"Scraping page {current} of {total}")
                print(f"Scraped {len(scraped_pages)} pages")  # Debug
                print(f"Scraper results: {len(scraper.results)} pages")  # Debug

                # Save results to file
                output_file = os.path.join(self.output_dir.get(), "mafia_wiki.json")
                print(f"Saving to {output_file}")  # Debug
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(scraper.results, f, indent=4, ensure_ascii=False)
                print(f"File saved successfully")  # Debug

                self.current_output_file = output_file
                self.update_status("Scraping completed successfully!")
                self.play_sound('success')

        except Exception as e:
            print(f"Error during scraping: {str(e)}")  # Debug
            self.show_error(str(e))
            return
        finally:
            self.scraping = False
            self.scrape_button.configure(text="Start Scraping", state="normal")
            self.update()  # Force update of GUI state

    def _run_async_loop(self):
        """Run the async event loop in a separate thread."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

def main():
    """Main entry point for the GUI."""
    app = MafiaWikiScraperGUI()
    app.mainloop()

if __name__ == "__main__":
    main()
