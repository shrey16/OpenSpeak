from openai import OpenAI
import tempfile
import os
import soundfile as sf

class CloudTranscriber:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("API key is missing.")
        self.client = OpenAI(api_key=api_key)

    def transcribe_audio(self, audio_data, samplerate=16000):
        if audio_data.size == 0:
            print("No audio data to transcribe.")
            return ""

        print("Transcribing audio via OpenAI API...")
        try:
            # OpenAI API requires a file path, so we write to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_audio_file:
                sf.write(tmp_audio_file.name, audio_data, samplerate)
                
                with open(tmp_audio_file.name, "rb") as audio_file:
                    transcription = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                
            os.remove(tmp_audio_file.name) # Clean up the temporary file
            
            print(f"Cloud transcription complete: {transcription.text}")
            return transcription.text.strip()
            
        except Exception as e:
            print(f"An error occurred during cloud transcription: {e}")
            # This could be due to an invalid API key, network issues, etc.
            return f"Error: {e}" 