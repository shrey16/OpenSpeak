# main.py
# This will be the main entry point for the application.
# It will orchestrate the hotkey listener, audio recorder, transcriber, and text injector. 

import threading
import sys
import os
from pystray import Icon, Menu, MenuItem
from PIL import Image
from queue import Queue

from .audio_recorder import AudioRecorder
from .hotkey_manager import HotkeyManager
from .transcriber import WhisperTranscriber, are_dependencies_installed
from .cloud_transcriber import CloudTranscriber
from .text_injector import inject_text
from .settings import Settings
from .gui import ControlPanel
from .indicator import Indicator

class OpenSpeakApp:
    def __init__(self):
        self.settings = Settings()
        self.indicator = Indicator()
        self.download_queue = Queue()
        
        self.local_transcriber = WhisperTranscriber()
        self.cloud_transcriber = None
        self.local_dependencies_installed = False
        
        self.audio_recorder = AudioRecorder()
        self.hotkey_manager = HotkeyManager(self._handle_hotkey_press, self._handle_hotkey_release)
        
        self.control_panel = ControlPanel(
            self.settings,
            on_close_callback=self.on_settings_closed,
            is_model_downloaded_callback=self.is_model_downloaded,
            download_model_callback=self.start_model_download,
            download_queue=self.download_queue,
            are_local_dependencies_installed=self.are_local_dependencies_installed,
            install_local_dependencies_callback=self.start_local_dependency_installation
        )
        self.control_panel.withdraw() # Start hidden

        self.icon = None
        self.is_recording = False
        
        self.reload_config()

    def reload_config(self):
        print("Reloading configuration...")
        self.settings.load()
        
        # Stop the listener before changing config
        self.hotkey_manager.stop_listening()

        # Check if local dependencies are installed
        self.local_dependencies_installed = are_dependencies_installed()

        # Hotkey config
        mode = self.settings.get_general('hotkey_mode')
        hotkey = self.settings.get_general('hotkey')
        self.hotkey_manager.set_config(hotkey, mode)
        
        # Engine config
        engine_type = self.settings.get_general('engine_type')
        if engine_type == 'local':
            if self.local_dependencies_installed:
                model_size = self.settings.get_local('model_size')
                device = self.settings.get_general('device')
                self.local_transcriber.set_config(model_size, device)
                # Proactively load the model after configuration is set
                self.local_transcriber.initialize_model()
            else:
                print("Local dependencies not found. Please install them via the settings panel.")
                # Ensure model is unloaded if dependencies were uninstalled
                self.local_transcriber.set_config(None, None)

        elif engine_type == 'openai': # openai
            api_key = self.settings.get_openai('api_key')
            if api_key:
                try:
                    self.cloud_transcriber = CloudTranscriber(api_key)
                except ValueError as e:
                    print(e)
                    self.cloud_transcriber = None
            else:
                self.cloud_transcriber = None
        
        # Restart the listener with the new configuration
        self.hotkey_manager.start_listening()

    def on_settings_closed(self):
        self.reload_config()

    def _handle_hotkey_press(self):
        if not self.is_recording:
            self.is_recording = True
            self.indicator.update_state("listening")
            self.audio_recorder.start()

    def _handle_hotkey_release(self):
        if self.is_recording:
            self.is_recording = False
            self.indicator.update_state("thinking")
            audio_data = self.audio_recorder.stop()

            if audio_data.size > 0:
                threading.Thread(target=self._transcribe_and_inject, args=(audio_data,)).start()
            else:
                print("No audio recorded.")
                self.indicator.update_state("idle")

    def _transcribe_and_inject(self, audio_data):
        engine_type = self.settings.get_general('engine_type')
        transcribed_text = ""
        
        if engine_type == 'local' and self.local_transcriber and self.local_dependencies_installed:
            transcribed_text = self.local_transcriber.transcribe_audio(audio_data)
        elif engine_type == 'openai' and self.cloud_transcriber:
            transcribed_text = self.cloud_transcriber.transcribe_audio(audio_data)
        else:
            print(f"Cannot transcribe. Engine '{engine_type}' is not properly configured.")

        if transcribed_text:
            inject_text(" " + transcribed_text)
            
        self.indicator.update_state("idle")

    def is_model_downloaded(self, model_size):
        return self.local_transcriber.is_model_downloaded(model_size)

    def start_model_download(self, model_size, on_complete):
        """Starts a background thread to download a model."""
        # The transcriber is already configured via reload_config,
        # which is called when settings are saved.
        def download_task():
            success = self.local_transcriber.download_model(model_size)
            self.download_queue.put((success, on_complete))

        threading.Thread(target=download_task, daemon=True).start()

    def are_local_dependencies_installed(self):
        return self.local_dependencies_installed

    def start_local_dependency_installation(self, progress_callback):
        """Starts a background thread to install torch and faster-whisper."""
        def install_task():
            success = self.local_transcriber.install_dependencies(progress_callback)
            # After installation, reload the config to initialize the transcriber
            if success:
                self.reload_config()
            # The callback in the GUI will be managed by the progress_callback
            # which can signal completion.

        threading.Thread(target=install_task, daemon=True).start()

    def _open_settings(self):
        # This is called from the pystray thread, so we need to schedule
        # the tkinter operations to run in the main thread.
        def safe_open():
            self.control_panel.deiconify()
            self.control_panel.lift()
            self.control_panel.focus_force()
        self.indicator.root.after(0, safe_open)

    def _quit_action(self):
        print("Quitting application...")
        self.hotkey_manager.stop_listening()
        self.icon.stop()
        # Schedule the indicator's destroy method to be called from the main thread
        if self.indicator:
            self.indicator.root.after(0, self.indicator.destroy)

    def run(self):
        # The listener is now started by reload_config() called in __init__
        menu = Menu(
            MenuItem('Settings', self._open_settings),
            MenuItem('Quit', self._quit_action)
        )
        
        try:
            # Use the provided icon
            icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'os_icon.png')
            image = Image.open(icon_path)
        except FileNotFoundError:
            # Fallback to a generated image if the icon is not found
            print("Icon file not found. Using a default icon.")
            image = Image.new('RGB', (64, 64), color = 'blue')

        self.icon = Icon("OpenSpeak", image, "OpenSpeak", menu)
        
        threading.Thread(target=self.icon.run, daemon=True).start()
        
        print("Application is running. The main thread is now managing the GUI.")
        self.indicator.run_mainloop()

if __name__ == "__main__":
    app = OpenSpeakApp()
    app.run() 