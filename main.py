# main.py
import sys
import os

# Add the 'src' directory to the Python path to allow for package imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from openspeak.app import OpenSpeakApp
from openspeak.settings import Settings
import tkinter as tk
from tkinter import messagebox, simpledialog
import subprocess

def run_first_time_setup(settings):
    """
    Shows a first-time setup dialog to the user to configure the transcription engine.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window

    choice = messagebox.askquestion(
        "OpenSpeak First-Time Setup",
        "Welcome to OpenSpeak!\n\n"
        "Please choose your transcription engine:\n\n"
        "Select 'Yes' for Local (GPU) transcription for fast, offline processing.\n"
        "Select 'No' for OpenAI API for cloud-based transcription.",
        icon='question', type='yesno')

    if choice == 'yes':
        settings.set('General', 'engine_type', 'local')
        messagebox.showinfo(
            "GPU Library Installation",
            "OpenSpeak will now download and install the necessary libraries for GPU acceleration. "
            "This is a one-time process and may take several minutes depending on your internet connection.\n\n"
            "Please wait for the process to complete."
        )
        try:
            # We assume installer.py is in the src/openspeak directory
            installer_path = os.path.join(os.path.dirname(__file__), 'src', 'openspeak', 'installer.py')
            subprocess.run([sys.executable, installer_path], check=True)
            settings.set('General', 'gpu_libraries_installed', 'true')
            messagebox.showinfo("Success", "GPU libraries installed successfully! The application will now start.")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            messagebox.showerror("Error", f"Failed to install GPU libraries: {e}\n\nPlease check your internet connection and try again.")
            return False # Indicate failure
    else:
        settings.set('General', 'engine_type', 'openai')
        api_key = simpledialog.askstring("OpenAI API Key", "Please enter your OpenAI API Key:", show='*')
        if api_key:
            settings.set('OpenAI', 'api_key', api_key)
        else:
            messagebox.showwarning("Warning", "No API key provided. You will need to set it later in the settings.")

    settings.set('General', 'first_run_complete', 'true') # Flag to prevent this from running again
    root.destroy()
    return True # Indicate success

if __name__ == "__main__":
    settings = Settings()
    first_run_complete = settings.get('General', 'first_run_complete', fallback='false')

    if first_run_complete != 'true':
        if not run_first_time_setup(settings):
            sys.exit(1) # Exit if setup failed

    # This check is important for PyInstaller to work correctly
    try:
        app = OpenSpeakApp()
        app.run()
    except Exception as e:
        print(f"An error occurred: {e}")
        # Keep the console open to see the error in the packaged app
        input("Press Enter to exit...")