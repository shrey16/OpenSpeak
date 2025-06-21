# text_injector.py
# This module will handle injecting the transcribed text into the active window. 

import keyboard
import time

def inject_text(text):
    if not text:
        return
        
    # Add a small delay to ensure the user has released the hotkey
    # and the target window has focus.
    time.sleep(0.1)
    
    print(f"Injecting text: {text}")
    try:
        # keyboard.write is generally more reliable than clipboard methods
        # and works in more applications.
        keyboard.write(text)
    except Exception as e:
        print(f"Failed to inject text: {e}")
        # A fallback to clipboard could be implemented here in a real app. 