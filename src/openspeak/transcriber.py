# transcriber.py
# This module will handle the speech-to-text transcription using faster-whisper. 

import os
import subprocess
import sys
import importlib

def are_dependencies_installed():
    """Check if faster-whisper and torch are installed."""
    try:
        importlib.import_module('faster_whisper')
        # Torch is a dependency of faster-whisper, but we can check explicitly
        importlib.import_module('torch')
        return True
    except ImportError:
        return False

def install_dependencies(progress_callback=None):
    """
    Install faster-whisper and its torch dependencies.
    This is a blocking operation and should be run in a separate thread.
    """
    if progress_callback:
        progress_callback("Starting dependency installation...")

    # It's recommended to install a specific version of PyTorch that is compatible with CUDA
    # For simplicity, we use the versions from the original requirements, targeting CUDA 11.8
    # A more advanced implementation would detect CUDA version and select the appropriate torch wheels.
    pytorch_wheel_url = "https://download.pytorch.org/whl/cu118"
    
    try:
        # Command to install torch, torchaudio, torchvision
        command = [
            sys.executable, "-m", "pip", "install",
            "torch", "torchaudio", "torchvision",
            "--index-url", pytorch_wheel_url
        ]
        
        if progress_callback:
            progress_callback("Installing PyTorch (this may take a while)...")
        
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, creationflags=subprocess.CREATE_NO_WINDOW)
        for line in iter(process.stdout.readline, ''):
            if progress_callback:
                progress_callback(line.strip())
        process.wait()
        
        if process.returncode != 0:
            if progress_callback:
                progress_callback(f"PyTorch installation failed with exit code {process.returncode}.")
            return False

        # Command to install faster-whisper
        command = [sys.executable, "-m", "pip", "install", "faster-whisper"]

        if progress_callback:
            progress_callback("Installing faster-whisper...")

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, creationflags=subprocess.CREATE_NO_WINDOW)
        for line in iter(process.stdout.readline, ''):
            if progress_callback:
                progress_callback(line.strip())
        process.wait()
        
        if process.returncode == 0:
            if progress_callback:
                progress_callback("Dependencies installed successfully.")
            # Invalidate caches to ensure the new module is found
            importlib.invalidate_caches()
            return True
        else:
            if progress_callback:
                progress_callback(f"faster-whisper installation failed with exit code {process.returncode}.")
            return False
            
    except Exception as e:
        if progress_callback:
            progress_callback(f"An error occurred during installation: {e}")
        return False


class WhisperTranscriber:
    def __init__(self):
        self.model_size = None
        self.device = None
        self.compute_type = None
        self.model = None
        self.cache_path = os.path.join(os.path.expanduser("~"), ".whisper_model_cache")

    def set_config(self, model_size, device):
        """Sets the configuration for the transcriber and unloads the current model if the config changes."""
        new_compute_type = "float16" if device == "cuda" else "int8"
        
        if model_size != self.model_size or device != self.device:
            print(f"Configuration changed. New settings - Model: {model_size}, Device: {device}")
            self.model_size = model_size
            self.device = device
            self.compute_type = new_compute_type
            if self.model:
                print("Unloading old model from memory.")
                del self.model
                self.model = None

    def is_model_downloaded(self, model_size):
        """Checks if a model is available locally by trying to load it without network access."""
        if not are_dependencies_installed():
            return False
        
        from faster_whisper import WhisperModel
        try:
            WhisperModel(model_size, download_root=self.cache_path, local_files_only=True)
            return True
        except Exception:
            return False

    def download_model(self, model_size):
        """Downloads and initializes a model, making it the active model."""
        if not are_dependencies_installed():
            print("Cannot download model, dependencies are not installed.")
            return False
            
        if self.device is None:
            print("Cannot download model, device not configured.")
            return False

        from faster_whisper import WhisperModel
        print(f"Downloading model '{model_size}' for device '{self.device}'... This may take a while.")
        try:
            new_model = WhisperModel(
                model_size,
                device=self.device,
                compute_type=self.compute_type,
                download_root=self.cache_path
            )
            print(f"Model '{model_size}' downloaded successfully and is now active.")
            if self.model:
                del self.model
            self.model = new_model
            self.model_size = model_size # Ensure the current size is updated
            return True
        except Exception as e:
            print(f"Failed to download or initialize model '{model_size}': {e}")
            return False

    def initialize_model(self):
        """Loads the configured model into memory if it's not already loaded."""
        if not are_dependencies_installed():
            print("Cannot initialize model, dependencies are not installed.")
            return

        from faster_whisper import WhisperModel
        if self.model is None and self.model_size and self.device:
            print("Model not loaded. Attempting to initialize...")
            if self.is_model_downloaded(self.model_size):
                print(f"Loading model '{self.model_size}' for device '{self.device}'...")
                try:
                    self.model = WhisperModel(
                        self.model_size,
                        device=self.device,
                        compute_type=self.compute_type,
                        download_root=self.cache_path,
                        local_files_only=True
                    )
                    print("Model initialized successfully.")
                except Exception as e:
                    print(f"Failed to initialize model: {e}")
                    self.model = None
            else:
                print(f"Model '{self.model_size}' is not downloaded. Please download it via the settings panel.")

    def transcribe_audio(self, audio_data):
        if not are_dependencies_installed():
            return "Error: Local transcription libraries are not installed."

        from faster_whisper import WhisperModel
        if self.model is None:
            print("Transcriber not initialized. Cannot transcribe.")
            return "Error: Model not loaded. Please configure it in the settings."

        if audio_data.size == 0:
            print("No audio data to transcribe.")
            return ""
        print("Transcribing audio...")
        try:
            segments, info = self.model.transcribe(audio_data, beam_size=5)
            print(f"Detected language '{info.language}' with probability {info.language_probability}")
            transcribed_text = "".join(segment.text for segment in segments)
            print(f"Transcription complete: {transcribed_text}")
            return transcribed_text.strip()
        except Exception as e:
            print(f"An error occurred during transcription: {e}")
            return "" 