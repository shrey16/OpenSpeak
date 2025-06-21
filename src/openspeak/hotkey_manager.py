import keyboard
import threading

class HotkeyManager:
    def __init__(self, press_callback, release_callback):
        self.press_callback = press_callback
        self.release_callback = release_callback
        
        self.hotkey = "right shift"
        self.hotkey_keys = ["right shift"]
        self.mode = "hold" # "hold" or "toggle"
        
        self._hotkey_pressed = False
        self._toggle_state = False
        self.listener_thread = None

    def _parse_hotkey(self, hotkey_str):
        """Split a hotkey string like 'ctrl+space' into a list of key names."""
        return [k.strip().lower() for k in hotkey_str.split('+') if k.strip()]

    def set_config(self, hotkey, mode):
        self.hotkey = hotkey.strip()
        self.hotkey_keys = self._parse_hotkey(self.hotkey)
        self.mode = mode

    # ---------------- Hold-to-talk logic ----------------
    def _all_keys_pressed(self):
        """Return True if *all* keys in the hotkey combo are currently pressed."""
        return all(keyboard.is_pressed(k) for k in self.hotkey_keys)

    def _handle_hold_mode(self, event):
        # Trigger only on the key-down / key-up of the *last* key in the combo
        primary_key = self.hotkey_keys[-1]
        if event.name != primary_key:
            return

        if event.event_type == keyboard.KEY_DOWN and not self._hotkey_pressed:
            if self._all_keys_pressed():
                self._hotkey_pressed = True
                self.press_callback()
        elif event.event_type == keyboard.KEY_UP and self._hotkey_pressed:
            # any release of primary key ends the hold
            self._hotkey_pressed = False
            self.release_callback()

    # ---------------- Toggle logic ----------------
    def _handle_toggle_mode(self, event):
        primary_key = self.hotkey_keys[-1]
        if event.event_type == keyboard.KEY_DOWN and event.name == primary_key:
            if self._all_keys_pressed():
                if not self._toggle_state:
                    self._toggle_state = True
                    self.press_callback()
                else:
                    self._toggle_state = False
                    self.release_callback()

    # ---------------- Event dispatcher ----------------
    def _key_event_handler(self, event):
        if self.mode == "hold":
            self._handle_hold_mode(event)
        elif self.mode == "toggle":
            self._handle_toggle_mode(event)

    # ------------- Listener control ----------------
    def start_listening(self):
        # Unhook any previous listeners to be safe
        self.stop_listening()
        keyboard.hook(self._key_event_handler)
        print(f"Hotkey listener started. Hotkey: '{self.hotkey}', Mode: '{self.mode}'.")

    def stop_listening(self):
        keyboard.unhook_all()
        self._hotkey_pressed = False
        self._toggle_state = False
        print("Hotkey listener stopped.") 