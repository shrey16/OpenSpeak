# OpenSpeak: Free, Open-Source Voice-to-Text for Windows

![OpenSpeak Logo](src/openspeak/assets/os_icon.png)

**OpenSpeak is a free, powerful, and privacy-focused dictation tool that brings seamless voice typing to any application on your Windows PC. Powered by OpenAI's Whisper, it offers fast, accurate speech-to-text transcription.**

---

## Why Choose OpenSpeak?

*   🎤 **Universal Voice Typing**: Dictate in Microsoft Word, Notepad, your web browser, and anywhere else you can type.
*   🔒 **You Control Your Data**: Choose between two powerful transcription engines:
    *   **Local Transcription**: Runs 100% offline for maximum privacy. Requires a one-time download of transcription libraries from within the app. Supports GPU (NVIDIA/CUDA) for a significant speed boost.
    *   **OpenAI API**: Uses the latest `whisper-1` model for cutting-edge accuracy via the cloud.
*   🚀 **Flexible & Fast**: Activate via "Hold-to-Talk" for quick commands or "Toggle-to-Talk" for longer dictation.
*   ⚙️ **Simple & Smart Setup**: No complex installation required. The app guides you on first launch to choose your transcription engine. If you select "Local", the necessary libraries (~2.5 GB) are downloaded and installed automatically.
*   👀 **Movable Status Indicator**: A draggable on-screen indicator always shows the app's current status (Idle, Listening, Thinking).
*   ❤️ **Free & Open Source**: OpenSpeak is completely free and built by the community. No ads, no subscriptions.

---

## Quick Start (CPU-only)

1. Install Python 3.10+ and Git
2. Clone the repo and create a virtual-env
```powershell
 git clone https://github.com/your-username/openspeak.git
 cd openspeak
 python -m venv venv
 .\venv\Scripts\activate
```
3. Install **runtime** requirements (CPU versions):
```powershell
pip install -r requirements.txt
```
4. Run
```powershell
python main.py
```

> ℹ️  If you later want GPU acceleration, open the Settings window and click **Install Dependencies** under the Local tab – the correct PyTorch + CUDA wheels will be downloaded automatically.

### Administrator privileges
Global hotkey capture on Windows sometimes needs Administrator rights. If your chosen hotkey is not detected, **run PowerShell / the `.exe` as Administrator** and try again.

### Troubleshooting
| Problem | Fix |
|---------|-----|
| Hotkey not captured | Use a non-reserved combo (`Ctrl+Shift+S`, `F10`, etc.) or run as Admin |
| Mic not detected | Check Windows Privacy Settings → Microphone |
| Local model download slow | Make sure you have at least 3 GB free disk & stable internet |

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 