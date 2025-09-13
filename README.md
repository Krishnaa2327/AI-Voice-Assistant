# AI Voice Assistant

A powerful Windows voice assistant built with Python that can control your system, manage files, search the web, and much more.

## Features

### 🎙️ Voice Interaction
- Speech recognition using Google Web Speech API
- Text-to-speech with ElevenLabs integration and pyttsx3 fallback
- Wake word detection mode
- Privacy mode for text-only operation

### 🖥️ System Control
- Volume control (set, get, mute/unmute)
- Screenshot capture
- Screen lock
- System information (CPU, memory, disk, battery)
- WiFi profile management

### 📁 File Management
- Create folders and files
- Search for files
- File operations with voice commands

### 🌐 Web Integration
- Smart website opening with multi-word support
- Google search integration
- Wikipedia search with summaries
- Weather information (with API key)

### 🎵 Media Control
- Application launching and management
- Window control and switching

### 🛠️ Productivity Tools
- Mathematical calculations
- Unit conversions
- Timer functionality
- Quick note-taking
- Password generation

### 🔒 Security Features
- System security checks
- Password generation
- Privacy mode toggle

## Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd AI_Voice_Assistant
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your API keys in `config.py` (see Configuration section)

4. Run the assistant:
```bash
python main.py
```

## Configuration

Create a `config.py` file or set environment variables:

### ElevenLabs (Optional)
```python
ELEVENLABS_API_KEY = "your_elevenlabs_api_key"
CUSTOM_VOICE_NAME = "your_voice_name"
```

### OpenWeatherMap (Optional)
```python
OPENWEATHER_API_KEY = "your_openweathermap_api_key"
```


## Usage

### Voice Commands Examples

#### System Control
- "Set volume to 50"
- "Take a screenshot"
- "Lock screen"
- "System info"

#### Productivity
- "Calculate 25 times 4"
- "Convert 100 pounds to kilograms"
- "Set timer for 5 minutes"
- "Note remember to call mom"

#### Web & Information
- "Open website youtube"
- "Open website chat gpt"
- "Search Google for Python tutorials"
- "What is machine learning"
- "Weather in New York"

#### File Management
- "Create folder Projects"
- "Search for file report"
- "Create file test.txt"

#### Applications
- "Open calculator"
- "Open notepad"
- "Switch to Chrome"

## Supported Websites

The assistant recognizes many common websites with multi-word names:
- Chat GPT → https://chat.openai.com
- YouTube → https://www.youtube.com
- Google Drive → https://drive.google.com
- And many more...

## Requirements

- Windows 10/11
- Python 3.7+
- Microphone for voice input
- Internet connection for speech recognition and web features

## Dependencies

See `requirements.txt` for full list. Key dependencies:
- speechrecognition
- pyttsx3
- elevenlabs (optional)
- pycaw
- pyautogui
- psutil
- requests

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Common Issues

1. **Microphone not working**: Check Windows microphone permissions
2. **Volume control fails**: Run as administrator or check audio device permissions
3. **ElevenLabs not working**: Verify API key and voice name
4. **Speech recognition errors**: Check internet connection

### Support

For issues and questions, please create an issue on GitHub.
