# AI Voice Assistant (Windows, Python)

A hands-free desktop assistant for Windows built with Python. Control system settings, manage files, search the web/Wikipedia, open apps, do quick math, set timers, take notes, and more — all by voice. Uses Google Speech Recognition for input and Windows SAPI for TTS (optional ElevenLabs).

## ✨ Features

### 🎙️ Voice Interaction
- Speech recognition via Google Web Speech API
- Text-to-speech using Windows SAPI (default) + optional ElevenLabs
- Optional wake word (e.g., "hey assistant")
- Privacy mode (text-only: no TTS)

### 🖥️ System Control
- Volume control: set/get/mute (e.g., "volume 70", "set volume to 30")
- Screenshot capture
- Lock screen
- System information (CPU, memory, disk, battery)
- Wi‑Fi profiles listing

### 📁 File Management
- Create folders and files
- Search files anywhere under the current directory

### 🌐 Web & Information
- Open websites (smart handling for multi‑word names)
- Google search
- Wikipedia summaries (no API key required)
- Weather info via OpenWeatherMap (API key optional)

### 🛠️ Productivity & Utilities
- Calculator ("calculate 25 times 4")
- Unit conversions ("convert 100 pounds to kilograms")
- Timers ("set timer for 5 minutes")
- Quick notes (saved to quick_notes.txt)
- Secure password generator

### 🪟 Windows Integration
- Minimize all windows
- Switch to/close applications
- Launch common apps (Calculator, Notepad, Chrome, etc.)

## 🚀 Quick Start

1) Clone and enter the folder
```bash
git clone <your-repo-url>
cd AI_Voice_Assistant
```

2) Install dependencies
```bash
pip install -r requirements.txt
```

3) (Optional) Configure keys in `config.py`
- ElevenLabs (for premium TTS)
- OpenWeatherMap (weather features)
- Wake word and privacy settings

4) Run the assistant
```bash
python main.py
```

## ⚙️ Configuration
Edit `config.py` or set environment variables.

- Wake word
```python
WAKE_WORD_MODE = False      # True to require "hey assistant"
WAKE_WORD = "hey assistant"
```

- Privacy mode
```python
PRIVACY_MODE = False        # True = no voice output (text only)
```

- ElevenLabs (optional)
```python
ELEVENLABS_API_KEY = "your_elevenlabs_api_key"
CUSTOM_VOICE_NAME = "your_voice_name"
```

- OpenWeatherMap (optional)
```python
OPENWEATHER_API_KEY = "your_openweathermap_api_key"
```

## 🗣️ Examples
- "hello" / "what time is it"
- "volume 70" / "set volume to 30"
- "take a screenshot" / "lock screen"
- "system info" / "security check"
- "open website youtube" / "search google for python tutorials"
- "what is machine learning"
- "weather in London"
- "create folder Projects" / "create file notes.txt"
- "help" / "stop"

Tip: If you enable the wake word, prefix commands with it, e.g., "hey assistant, what time is it".

## ✅ Requirements
- Windows 10/11
- Python 3.7+
- Microphone for voice input
- Internet for speech recognition and web features

## 📦 Key Dependencies
See `requirements.txt` for the full list. Highlights:
- speechrecognition, pywin32, comtypes
- pycaw, pyautogui, psutil
- requests, wikipedia, pywhatkit
- elevenlabs (optional), pyttsx3 (fallback)

## 🧰 Troubleshooting
- TTS not speaking: ensure Windows audio is available; Windows SAPI is used by default.
- "Sorry, I didn't catch that": try speaking closer to the mic or adjust ENERGY_THRESHOLD in `config.py`.
- Volume control fails: some systems require running the terminal as Administrator.
- Weather not working: set `OPENWEATHER_API_KEY`.
- Wikipedia errors: check your internet or try rephrasing the query.

## 🤝 Contributing
1. Fork the repo
2. Create a feature branch
3. Commit your changes
4. Push and open a Pull Request

## 📄 License
MIT — see `LICENSE`.
