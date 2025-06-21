import customtkinter as ctk
from .settings import Settings
import os
from queue import Empty
import tkinter as tk
# We use a try-except block to make torch an optional dependency
try:
    import torch
except ImportError:
    torch = None

class ControlPanel(ctk.CTk):
    def __init__(self, settings: Settings, on_close_callback=None, is_model_downloaded_callback=None, download_model_callback=None, download_queue=None, are_local_dependencies_installed=None, install_local_dependencies_callback=None):
        super().__init__()
        self.settings = settings
        self.on_close_callback = on_close_callback
        self.is_model_downloaded = is_model_downloaded_callback
        self.download_model = download_model_callback
        self.download_queue = download_queue
        self.are_local_dependencies_installed = are_local_dependencies_installed
        self.install_local_dependencies = install_local_dependencies_callback

        self.title("OpenSpeak Settings")
        self.geometry("450x480") # Adjusted size
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'os_icon.ico')
            self.iconbitmap(icon_path)
        except Exception as e:
            print(f"Could not load window icon: {e}")

        ctk.set_appearance_mode("system")
        
        # --- Layout ---
        self.grid_rowconfigure(0, weight=1) 
        self.grid_columnconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # --- UI Elements ---
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.pack(padx=0, pady=0, fill="both", expand=True)
        self.tabview.add("General")
        self.tabview.add("Transcription")

        # General Tab
        general_frame = self.tabview.tab("General")
        
        ctk.CTkLabel(general_frame, text="Activation Mode:").pack(pady=(10,0), padx=20, anchor="w")
        self.mode_var = ctk.StringVar(value=self.settings.get_general('hotkey_mode'))
        ctk.CTkRadioButton(general_frame, text="Hold to Talk", variable=self.mode_var, value="hold").pack(pady=5, padx=40, anchor="w")
        ctk.CTkRadioButton(general_frame, text="Toggle to Talk", variable=self.mode_var, value="toggle").pack(pady=5, padx=40, anchor="w")

        ctk.CTkLabel(general_frame, text="Activation Hotkey:").pack(pady=(10,0), padx=20, anchor="w")
        self.hotkey_var = ctk.StringVar(value=self.settings.get_general('hotkey'))
        self.hotkey_entry = ctk.CTkEntry(general_frame, textvariable=self.hotkey_var)
        self.hotkey_entry.pack(pady=5, padx=20, fill="x")
        ctk.CTkLabel(general_frame, text="Examples: 'right shift', 'ctrl+alt+x', 'f9'", font=("Arial", 10), text_color="gray").pack(padx=20, anchor="w")

        # Transcription Tab
        transcription_frame = self.tabview.tab("Transcription")

        ctk.CTkLabel(transcription_frame, text="Engine:").pack(pady=(10,0), padx=20, anchor="w")
        self.engine_var = ctk.StringVar(value=self.settings.get_general('engine_type'))
        self.local_radio = ctk.CTkRadioButton(transcription_frame, text="Local", variable=self.engine_var, value="local", command=self.toggle_engine_fields)
        self.local_radio.pack(pady=5, padx=40, anchor="w")
        self.openai_radio = ctk.CTkRadioButton(transcription_frame, text="OpenAI API", variable=self.engine_var, value="openai", command=self.toggle_engine_fields)
        self.openai_radio.pack(pady=5, padx=40, anchor="w")

        # Local Model Settings Frame
        self.local_frame = ctk.CTkFrame(transcription_frame)
        
        # -- Local - Dependency Installation Frame --
        self.install_frame = ctk.CTkFrame(self.local_frame)
        ctk.CTkLabel(self.install_frame, text="Local Transcription Dependencies").pack(pady=(5,0), padx=10, anchor="w")
        self.install_status_label = ctk.CTkLabel(self.install_frame, text="Status: Not Installed", text_color="orange")
        self.install_status_label.pack(pady=(0, 5), padx=10, anchor="w")
        self.install_button = ctk.CTkButton(self.install_frame, text="Install Dependencies (~2.5 GB)", command=self.on_install_dependencies_click)
        self.install_button.pack(pady=5, padx=10, fill="x")
        self.progress_log_textbox = ctk.CTkTextbox(self.install_frame, height=120, state="disabled")
        self.progress_log_textbox.pack(pady=(5,10), padx=10, fill="both", expand=True)

        # -- Local - Main Settings Frame (shown after install) --
        self.local_settings_frame = ctk.CTkFrame(self.local_frame)
        
        # Hardware Acceleration
        ctk.CTkLabel(self.local_settings_frame, text="Hardware Acceleration:").pack(pady=(5,0), padx=10, anchor="w")
        self.device_var = ctk.StringVar(value=self.settings.get_general('device'))
        self.cpu_radio = ctk.CTkRadioButton(self.local_settings_frame, text="CPU", variable=self.device_var, value="cpu")
        self.cpu_radio.pack(pady=5, padx=20, anchor="w")
        self.gpu_radio = ctk.CTkRadioButton(self.local_settings_frame, text="GPU (NVIDIA/CUDA)", variable=self.device_var, value="cuda")
        self.gpu_radio.pack(pady=5, padx=20, anchor="w")
        
        ctk.CTkLabel(self.local_settings_frame, text="Model Size:").pack(pady=(5,0), padx=10, anchor="w")
        
        # Model Dropdown
        self.model_size_var = ctk.StringVar(value=self.settings.get_local('model_size'))
        self.model_size_menu = ctk.CTkOptionMenu(self.local_settings_frame, variable=self.model_size_var, 
                                                 values=["tiny.en", "base.en", "small.en", "medium.en"],
                                                 command=self.on_model_select)
        self.model_size_menu.pack(pady=5, padx=10, fill="x")

        # Model Status Label
        self.model_status_label = ctk.CTkLabel(self.local_settings_frame, text="", font=("Arial", 10))
        self.model_status_label.pack(pady=(0, 5), padx=10, anchor="w")
        
        # Download Button
        self.download_button = ctk.CTkButton(self.local_settings_frame, text="Download Model", command=self.on_download_click)

        # OpenAI Settings Frame
        self.openai_frame = ctk.CTkFrame(transcription_frame)
        ctk.CTkLabel(self.openai_frame, text="OpenAI API Key:").pack(pady=(5,0), padx=10, anchor="w")
        self.api_key_var = ctk.StringVar(value=self.settings.get_openai('api_key'))
        ctk.CTkEntry(self.openai_frame, textvariable=self.api_key_var, show="*").pack(pady=5, padx=10, fill="x")

        # Save Button
        self.save_button = ctk.CTkButton(self, text="Save and Close", command=self.save_and_close)
        self.save_button.grid(row=1, column=0, pady=10, padx=20, sticky="se")
        
        self.toggle_engine_fields() # Set initial visibility
        self.update_local_transcriber_ui()
        self.check_download_queue() # Start polling for download results

    def is_cuda_available(self):
        # Check if torch was imported and if cuda is available
        return torch is not None and torch.cuda.is_available()

    def update_local_transcriber_ui(self):
        """Shows/hides UI elements based on whether local dependencies are installed."""
        if self.are_local_dependencies_installed():
            self.install_frame.pack_forget()
            self.local_settings_frame.pack(pady=5, padx=0, fill="x", expand=True)
            self.on_model_select(self.model_size_var.get())
        else:
            self.install_frame.pack(pady=5, padx=0, fill="x", expand=True)
            self.local_settings_frame.pack_forget()

    def on_install_dependencies_click(self):
        self.set_ui_state("disabled")
        self.install_button.configure(state="disabled")
        self.progress_log_textbox.configure(state="normal")
        self.progress_log_textbox.delete("1.0", tk.END)
        self.log_progress("Starting installation...")
        self.install_local_dependencies(self.on_install_progress)
        
    def log_progress(self, message):
        self.progress_log_textbox.insert(tk.END, message + "\n")
        self.progress_log_textbox.see(tk.END)
        self.update_idletasks() # Force UI update

    def on_install_progress(self, message):
        if "Dependencies installed successfully." in message:
            self.log_progress(message)
            self.log_progress("\nInstallation complete! Reloading...")
            self.after(2000, self.on_install_complete) # Give user time to read message
        else:
            self.log_progress(message)

    def on_install_complete(self):
        self.set_ui_state("normal")
        self.update_local_transcriber_ui()
        self.save_settings() # Save any other changes
        
    def check_download_queue(self):
        """Checks the queue for download results and processes them."""
        try:
            success, callback = self.download_queue.get_nowait()
            callback(success) # Execute the original on_download_complete callback
        except Empty:
            pass # Queue is empty, do nothing
        finally:
            # Check again after a short delay
            self.after(100, self.check_download_queue)

    def on_model_select(self, selected_model):
        """Called when a new model is selected from the dropdown."""
        if self.is_model_downloaded(selected_model):
            self.model_status_label.configure(text="Status: Downloaded", text_color="gray")
            self.download_button.pack_forget() # Hide button if downloaded
        else:
            self.model_status_label.configure(text="Status: Not Downloaded", text_color="orange")
            self.download_button.pack(pady=5, padx=10, fill="x") # Show button

    def on_download_click(self):
        """Called when the 'Download Model' button is clicked."""
        selected_model = self.model_size_var.get()
        
        # Disable UI elements
        self.set_ui_state("disabled")
        self.model_status_label.configure(text=f"Status: Downloading {selected_model}...", text_color="yellow")
        self.download_button.pack_forget()

        # Start download via callback to main app
        self.download_model(selected_model, self.on_download_complete)

    def on_download_complete(self, success: bool):
        """Callback function for when the download thread finishes."""
        self.set_ui_state("normal") # Re-enable UI
        selected_model = self.model_size_var.get()
        if success:
            self.model_status_label.configure(text="Status: Downloaded", text_color="gray")
        else:
            self.model_status_label.configure(text="Status: Download failed", text_color="red")
            self.download_button.pack(pady=5, padx=10, fill="x") # Show button again on failure
        
    def set_ui_state(self, state: str):
        """Disables or enables key UI elements."""
        self.save_button.configure(state=state)
        self.local_radio.configure(state=state)
        self.openai_radio.configure(state=state)
        self.model_size_menu.configure(state=state)
        self.api_key_var.get() # No easy way to disable entry, but this is fine
        self.mode_var.get() # Radios are not easily disabled as a group

    def toggle_engine_fields(self):
        engine = self.engine_var.get()
        if engine == "local":
            self.local_frame.pack(pady=5, padx=20, fill="x", expand=True)
            self.update_local_transcriber_ui()
            self.openai_frame.pack_forget()
        else: # openai
            self.local_frame.pack_forget()
            self.openai_frame.pack(pady=5, padx=20, fill="x", expand=True)
        self.settings.set('General', 'engine_type', self.engine_var.get())
        self.settings.set('General', 'device', self.device_var.get())
        self.settings.set('Local', 'model_size', self.model_size_var.get())
        self.settings.set('OpenAI', 'api_key', self.api_key_var.get())

    def save_settings(self):
        """Saves all the current settings from the UI."""
        # Get hotkey directly from the entry widget since textvariable binding isn't working
        hotkey_value = self.hotkey_entry.get()
        print(f"Saving hotkey: '{hotkey_value}'")
        self.settings.set('General', 'hotkey_mode', self.mode_var.get())
        self.settings.set('General', 'hotkey', hotkey_value)
        self.settings.set('General', 'engine_type', self.engine_var.get())
        self.settings.set('General', 'device', self.device_var.get())
        self.settings.set('Local', 'model_size', self.model_size_var.get())
        self.settings.set('OpenAI', 'api_key', self.api_key_var.get())
        print("Settings saved to config file")

    def on_closing(self):
        self.withdraw() # Hide window instead of destroying it
        if self.on_close_callback:
            self.on_close_callback()

    def save_and_close(self):
        self.save_settings()
        self.on_closing()

if __name__ == '__main__':
    # For testing the GUI independently
    settings = Settings()
    app = ControlPanel(settings)
    app.mainloop() 