import tkinter as tk

class Indicator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.8)
        
        self.label = tk.Label(self.root, text="IDLE", fg="white", bg="green", font=("Arial", 12, "bold"))
        self.label.pack(ipadx=10, ipady=5)

        # For dragging the window
        self._offset_x = 0
        self._offset_y = 0
        self.label.bind('<ButtonPress-1>', self._start_move)
        self.label.bind('<ButtonRelease-1>', self._stop_move)
        self.label.bind('<B1-Motion>', self._do_move)

        self._position_window()
        self.root.withdraw()

    def _start_move(self, event):
        self._offset_x = event.x
        self._offset_y = event.y

    def _stop_move(self, event):
        self._offset_x = 0
        self._offset_y = 0

    def _do_move(self, event):
        x = self.root.winfo_pointerx() - self._offset_x
        y = self.root.winfo_pointery() - self._offset_y
        self.root.geometry(f'+{x}+{y}')

    def _position_window(self):
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        x = (screen_width // 2) - (window_width // 2)
        y = self.root.winfo_screenheight() - window_height - 60
        self.root.geometry(f"+{x}+{y}")

    def update_state(self, state: str):
        states = {
            "idle": ("IDLE", "green"),
            "listening": ("LISTENING", "red"),
            "thinking": ("THINKING...", "orange")
        }
        
        text, color = states.get(state.lower(), ("UNKNOWN", "grey"))

        if state == "idle":
            self.root.withdraw()
        else:
            self.root.deiconify()
        self.label.config(text=text, bg=color)
        # The window is now draggable, so we no longer force a reposition on update.
        # self._position_window()

    def run_mainloop(self):
        self.root.mainloop()

    def destroy(self):
        self.root.destroy()

if __name__ == '__main__':
    # For testing the indicator independently
    import time
    indicator = Indicator()
    
    print("Testing indicator...")
    time.sleep(2) # Wait for window to be created

    indicator.update_state("listening")
    time.sleep(2)
    indicator.update_state("thinking")
    time.sleep(2)
    indicator.update_state("idle")
    print("Test complete.")
    # In a real app, the main loop would keep this alive.
    # For this test, we'll just exit.
    indicator.root.after(100, indicator.root.destroy) 