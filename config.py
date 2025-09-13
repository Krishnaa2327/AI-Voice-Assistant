"""
Configuration file for AI Voice Assistant
Copy this file and customize with your own API keys and settings.
"""

import os

# =============================================================================
# ELEVENLABS VOICE SETTINGS
# =============================================================================

# Get ElevenLabs API key from environment variable or set directly
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "YOUR_ELEVENLABS_API_KEY")
CUSTOM_VOICE_NAME = os.getenv("CUSTOM_VOICE_NAME", "default_voice")  # Name of your custom voice

# =============================================================================
# API KEYS
# =============================================================================

# OpenWeatherMap API key (get from openweathermap.org)
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "YOUR_OPENWEATHERMAP_API_KEY")



# =============================================================================
# ASSISTANT SETTINGS
# =============================================================================

# Assistant behavior settings
PRIVACY_MODE = False  # Set to True to disable voice output
WAKE_WORD_MODE = False  # Set to True to enable wake word detection
WAKE_WORD = "hey assistant"  # Wake word phrase

# Voice settings
TTS_RATE = 180  # Speech rate for fallback TTS
TTS_VOLUME = 0.9  # Volume level for fallback TTS (0.0 to 1.0)

# =============================================================================
# FEATURE FLAGS
# =============================================================================

# Enable/disable specific features
ENABLE_ELEVENLABS = True
ENABLE_WEATHER = True

# =============================================================================
# SYSTEM SETTINGS
# =============================================================================

# File paths
NOTES_FILE = "quick_notes.txt"
TODO_FILE = "todo.txt"

# Speech recognition settings
ENERGY_THRESHOLD = 4000
DYNAMIC_ENERGY_THRESHOLD = True
LISTEN_TIMEOUT = 5
PHRASE_TIME_LIMIT = 10
