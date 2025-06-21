# audio_recorder.py
# This module will handle recording audio from the microphone. 

import sounddevice as sd
import numpy as np
import queue

class AudioRecorder:
    def __init__(self, samplerate=16000, channels=1):
        self.samplerate = samplerate
        self.channels = channels
        self.stream = None
        self.q = queue.Queue()

    def _callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, flush=True)
        self.q.put(indata.copy())

    def start(self):
        if self.stream is not None:
            return  # Already recording

        self.q = queue.Queue()
        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=self.channels,
            callback=self._callback,
            dtype='float32'  # faster-whisper expects float32
        )
        self.stream.start()
        print("Recording started...")

    def stop(self):
        if self.stream is None:
            return np.array([]) # Not recording

        self.stream.stop()
        self.stream.close()
        self.stream = None
        print("Recording stopped.")

        # Drain the queue and concatenate
        audio_blocks = []
        while not self.q.empty():
            audio_blocks.append(self.q.get())
        
        if not audio_blocks:
            return np.array([], dtype=np.float32)

        return np.concatenate(audio_blocks, axis=0).flatten() 