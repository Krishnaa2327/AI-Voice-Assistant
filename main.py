#!/usr/bin/env python3
"""
AI Voice Assistant - Main Application
A powerful Windows voice assistant with system control, web integration, and productivity features.
"""

import speech_recognition as sr
import datetime
import requests
import json
import os
import webbrowser
import subprocess
import threading
import time
import math
import random
import string
import socket
import shutil
import glob
import re
import tempfile
import sys

# Import configuration
try:
    from config import *
except ImportError:
    print("Warning: config.py not found. Using default settings.")
    # Default configuration if config.py doesn't exist
    ELEVENLABS_API_KEY = "YOUR_ELEVENLABS_API_KEY"
    CUSTOM_VOICE_NAME = "default_voice"
    OPENWEATHER_API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"
    PRIVACY_MODE = False
    WAKE_WORD_MODE = False
    WAKE_WORD = "hey assistant"
    TTS_RATE = 180
    TTS_VOLUME = 0.9
    NOTES_FILE = "quick_notes.txt"
    TODO_FILE = "todo.txt"
    ENERGY_THRESHOLD = 4000
    DYNAMIC_ENERGY_THRESHOLD = True
    LISTEN_TIMEOUT = 5
    PHRASE_TIME_LIMIT = 10

# Auto-install required packages
def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

# Import ElevenLabs
try:
    from elevenlabs import ElevenLabs
except ImportError:
    install_package("elevenlabs")
    from elevenlabs import ElevenLabs

# Import fallback TTS
try:
    import pyttsx3
except ImportError:
    install_package("pyttsx3")
    import pyttsx3

# Import other required packages
try:
    import psutil
except ImportError:
    install_package("psutil")
    import psutil

try:
    import pyautogui
except ImportError:
    install_package("pyautogui")
    import pyautogui

try:
    import pywhatkit
except ImportError:
    install_package("pywhatkit")
    import pywhatkit

try:
    import wikipedia
except ImportError:
    install_package("wikipedia")
    import wikipedia


try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
except ImportError:
    install_package("pycaw")
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL

try:
    import win32api
    import win32gui
    import win32con
    import win32process
except ImportError:
    install_package("pywin32")
    import win32api
    import win32gui
    import win32con
    import win32process

# =============================================================================
# SYSTEM INITIALIZATION
# =============================================================================

# Initialize ElevenLabs client safely
client = None
try:
    if ELEVENLABS_API_KEY != "YOUR_ELEVENLABS_API_KEY":
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
except Exception as e:
    print(f"ElevenLabs initialization failed: {e}")

# Initialize fallback TTS engine
fallback_tts = None
try:
    fallback_tts = pyttsx3.init()
    fallback_tts.setProperty('rate', TTS_RATE)
    fallback_tts.setProperty('volume', TTS_VOLUME)
except Exception as e:
    print(f"Fallback TTS initialization failed: {e}")

# Global variables
active_timers = []
reminders = []
listen_enabled = True

# Voice ID detection
VOICE_ID = None
if client:
    try:
        voices = client.voices.get_all().voices
        for voice in voices:
            if voice.name == CUSTOM_VOICE_NAME:
                VOICE_ID = voice.voice_id
                break
        if VOICE_ID is None:
            print(f"Warning: Voice '{CUSTOM_VOICE_NAME}' not found in your ElevenLabs account. Using fallback TTS.")
    except Exception as e:
        print(f"Error fetching voices from ElevenLabs: {e}. Using fallback TTS.")

# Initialize audio control for volume management
try:
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
except:
    volume = None
    print("Audio control not available")

# =============================================================================
# PERSONALIZATION FEATURES - RANDOMIZED RESPONSES
# =============================================================================

# Greeting responses
GREETINGS = [
    "Hi there! What can I do for you?",
    "Hello! How can I help you today?",
    "Hey! What's up?",
    "Hi! Ready to assist you!",
    "Hello there! What would you like me to do?",
    "Hey! How can I make your day better?"
]

# Confirmation responses
CONFIRMATIONS = [
    "Of course!",
    "Absolutely!",
    "Sure thing!",
    "You got it!",
    "Right away!",
    "On it!",
    "No problem!"
]

# Task completion responses
COMPLETIONS = [
    "Done!",
    "All set!",
    "Task completed!",
    "There you go!",
    "Finished!",
    "Mission accomplished!"
]

# Error responses
ERROR_RESPONSES = [
    "Hmm, I'm having some trouble with that.",
    "Oops, something went wrong there.",
    "I ran into a little issue.",
    "Sorry, I couldn't complete that task.",
    "That didn't work as expected."
]

# Goodbye responses
GOODBYES = [
    "Goodbye! Have a great day!",
    "See you later!",
    "Take care!",
    "Until next time!",
    "Catch you later!",
    "Bye for now!"
]

def get_random_response(response_list):
    """Get a random response from a list of responses"""
    return random.choice(response_list)

# =============================================================================
# CORE FUNCTIONS
# =============================================================================

def speak(text):
    """Enhanced speak function with privacy mode check and fallback TTS"""
    print(f"Assistant: {text}")
    
    if PRIVACY_MODE:
        print(f"[PRIVACY MODE] Text-only mode")
        return
    
    if not listen_enabled:
        return
        
    # Try ElevenLabs first
    if client and VOICE_ID:
        try:
            audio = client.text_to_speech.convert(
                voice_id=VOICE_ID,
                text=text,
                model_id="eleven_multilingual_v2"
            )
            
            # Save audio to temporary file and play it
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                for chunk in audio:
                    tmp_file.write(chunk)
                tmp_filename = tmp_file.name
            
            # Play using Windows default audio player
            os.system(f'start /min "" "{tmp_filename}"')
            
            # Schedule cleanup after playback (non-blocking)
            def cleanup():
                time.sleep(10)  # Wait for playback to finish
                try:
                    os.remove(tmp_filename)
                except:
                    pass
            
            cleanup_thread = threading.Thread(target=cleanup)
            cleanup_thread.daemon = True
            cleanup_thread.start()
            return
        except Exception as e:
            print(f"ElevenLabs TTS error: {e}")
    
    # Use Windows SAPI for reliable TTS
    try:
        import win32com.client
        sapi = win32com.client.Dispatch('SAPI.SpVoice')
        sapi.Speak(text)
        return
    except Exception as e:
        print(f"Windows SAPI TTS error: {e}")
    
    # Fallback to pyttsx3
    try:
        tts_engine = pyttsx3.init()
        tts_engine.setProperty('rate', TTS_RATE)
        tts_engine.setProperty('volume', TTS_VOLUME)
        tts_engine.say(text)
        tts_engine.runAndWait()
        del tts_engine
        return
    except Exception as e:
        print(f"pyttsx3 TTS error: {e}")
    
    # If all TTS fails, just print
    print("[TTS not available - text only]")

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

# System Control Functions
def set_volume(level):
    """Set system volume (0-100) using endpoint scalar API"""
    if volume:
        try:
            level = max(0, min(100, int(level)))
            volume.SetMasterVolumeLevelScalar(level / 100.0, None)
            return True
        except Exception as e:
            print(f"Volume error (set): {e}")
            return False
    return False

def get_volume():
    """Get current system volume (0-100)"""
    if volume:
        try:
            return int(round(volume.GetMasterVolumeLevelScalar() * 100))
        except Exception as e:
            print(f"Volume error (get): {e}")
            return None
    return None

def mute_volume(desired=None):
    """Toggle mute/unmute. If desired is True/False, set explicitly; otherwise toggle."""
    if volume:
        try:
            current = bool(volume.GetMute())
            new_state = (not current) if desired is None else bool(desired)
            volume.SetMute(new_state, None)
            return True
        except Exception as e:
            print(f"Volume error (mute): {e}")
            return False
    return False

def take_screenshot():
    """Take a screenshot"""
    try:
        screenshot = pyautogui.screenshot()
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        screenshot.save(filename)
        return filename
    except Exception as e:
        return None

def lock_screen():
    """Lock the computer screen"""
    try:
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
        return True
    except:
        return False

def get_system_info():
    """Get system information"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('C:\\')
        battery = psutil.sensors_battery() if hasattr(psutil, 'sensors_battery') else None
        
        info = {
            'cpu': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available': round(memory.available / (1024**3), 1),
            'disk_percent': round((disk.total - disk.free) / disk.total * 100, 1),
            'battery': battery.percent if battery else None
        }
        return info
    except:
        return None

def get_wifi_info():
    """Get WiFi information"""
    try:
        result = subprocess.run(['netsh', 'wlan', 'show', 'profile'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            profiles = []
            for line in result.stdout.split('\\n'):
                if 'All User Profile' in line:
                    profile = line.split(':')[-1].strip()
                    profiles.append(profile)
            return profiles
    except:
        pass
    return []

# Productivity Functions
def calculate(expression):
    """Safe calculator function"""
    try:
        # Remove any non-mathematical characters for security
        expression = re.sub(r'[^0-9+\\-*/().\\s]', '', expression)
        result = eval(expression)
        return result
    except:
        return None

def convert_units(value, from_unit, to_unit):
    """Simple unit conversion"""
    conversions = {
        ('celsius', 'fahrenheit'): lambda x: (x * 9/5) + 32,
        ('fahrenheit', 'celsius'): lambda x: (x - 32) * 5/9,
        ('pounds', 'kilograms'): lambda x: x * 0.453592,
        ('kilograms', 'pounds'): lambda x: x / 0.453592,
        ('miles', 'kilometers'): lambda x: x * 1.60934,
        ('kilometers', 'miles'): lambda x: x / 1.60934,
        ('feet', 'meters'): lambda x: x * 0.3048,
        ('meters', 'feet'): lambda x: x / 0.3048
    }
    
    key = (from_unit.lower(), to_unit.lower())
    if key in conversions:
        return conversions[key](value)
    return None

def set_timer(minutes, message="Timer finished!"):
    """Set a timer in the background"""
    def timer_function():
        time.sleep(minutes * 60)
        speak(message)
        if message in [t['message'] for t in active_timers]:
            active_timers.remove({'minutes': minutes, 'message': message})
    
    timer_thread = threading.Thread(target=timer_function)
    timer_thread.daemon = True
    timer_thread.start()
    active_timers.append({'minutes': minutes, 'message': message})

def save_note(content):
    """Save a quick note with timestamp"""
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(NOTES_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {content}\\n")
        return True
    except:
        return False

# File Management Functions
def create_folder(folder_name, path="."):
    """Create a new folder"""
    try:
        full_path = os.path.join(path, folder_name)
        os.makedirs(full_path, exist_ok=True)
        return True
    except:
        return False

def delete_file(filename):
    """Safely delete a file"""
    try:
        if os.path.exists(filename):
            os.remove(filename)
            return True
        return False
    except:
        return False

def search_files(pattern, directory="."):
    """Search for files matching a pattern"""
    try:
        matches = glob.glob(os.path.join(directory, f"**/*{pattern}*"), recursive=True)
        return matches[:10]  # Limit to 10 results
    except:
        return []

def create_file(filename, content=""):
    """Create a new file with optional content"""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except:
        return False

# Windows Integration Functions
def minimize_all_windows():
    """Minimize all windows"""
    try:
        pyautogui.hotkey('win', 'm')
        return True
    except:
        return False

def switch_window(app_name):
    """Switch to a specific application window"""
    try:
        def enum_window_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if app_name.lower() in window_title.lower():
                    windows.append((hwnd, window_title))
            return True
        
        windows = []
        win32gui.EnumWindows(enum_window_callback, windows)
        
        if windows:
            win32gui.SetForegroundWindow(windows[0][0])
            return True
        return False
    except:
        return False

def close_application(app_name):
    """Close a specific application"""
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            if app_name.lower() in proc.info['name'].lower():
                proc.terminate()
                return True
        return False
    except:
        return False

# Security Functions
def generate_password(length=12):
    """Generate a secure password"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def check_system_security():
    """Basic system security check"""
    try:
        # Check for suspicious processes
        suspicious_count = 0
        high_cpu_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                if proc.info['cpu_percent'] > 80:
                    high_cpu_processes.append(proc.info['name'])
                    suspicious_count += 1
            except:
                continue
        
        return {
            'high_cpu_processes': high_cpu_processes,
            'suspicious_count': suspicious_count
        }
    except:
        return None


# Web Search Functions
def search_google(query):
    """Search Google using pywhatkit"""
    try:
        pywhatkit.search(query)
        return True
    except:
        return False

def search_wikipedia(query):
    """Search Wikipedia and return summary"""
    try:
        wikipedia.set_lang("en")
        # Try different search approaches
        try:
            summary = wikipedia.summary(query, sentences=2, auto_suggest=True)
            return summary
        except wikipedia.DisambiguationError as e:
            # If multiple pages found, use the first one
            summary = wikipedia.summary(e.options[0], sentences=2)
            return summary
        except wikipedia.PageError:
            # Try searching for pages first
            search_results = wikipedia.search(query, results=3)
            if search_results:
                summary = wikipedia.summary(search_results[0], sentences=2)
                return summary
            return None
    except Exception as e:
        print(f"Wikipedia search error: {e}")
        return None


def listen_for_command():
    """Enhanced listening function with wake word and privacy mode support"""
    global listen_enabled
    
    if PRIVACY_MODE:
        user_input = input("[PRIVACY MODE] Type your command: ")
        return user_input.lower() if user_input else None
    
    r = sr.Recognizer()
    r.energy_threshold = ENERGY_THRESHOLD
    r.dynamic_energy_threshold = DYNAMIC_ENERGY_THRESHOLD
    
    with sr.Microphone() as source:
        if WAKE_WORD_MODE:
            print(f"Listening for '{WAKE_WORD}'...")
        else:
            print("\nListening...")
        
        try:
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=LISTEN_TIMEOUT, phrase_time_limit=PHRASE_TIME_LIMIT)
        except sr.WaitTimeoutError:
            return None
    
    try:
        print("Processing...")
        query = r.recognize_google(audio, language='en-us')
        print(f"You said: '{query}'")
        
        # Wake word detection
        if WAKE_WORD_MODE:
            if WAKE_WORD.lower() in query.lower():
                # Remove wake word from command
                query = query.lower().replace(WAKE_WORD.lower(), "").strip()
                if query:
                    return query
                else:
                    speak(get_random_response(GREETINGS))
                    return "activated"
            else:
                return None  # Ignore commands without wake word
        
        return query.lower()
        
    except sr.UnknownValueError:
        if not WAKE_WORD_MODE:
            print("Sorry, I didn't catch that.")
        return None
    except sr.RequestError as e:
        print(f"Speech recognition error: {e}")
        return None

def continuous_listen():
    """Continuous listening mode for wake word detection"""
    global listen_enabled
    
    while listen_enabled:
        try:
            command = listen_for_command()
            if command:
                process_command(command)
            time.sleep(0.1)  # Small delay to prevent excessive CPU usage
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error in continuous listening: {e}")
            time.sleep(1)

def process_command(command):
    """Process voice commands with comprehensive feature support"""
    if not command or command == "activated":
        return
    
    global PRIVACY_MODE, listen_enabled
    
    # =========================================================================
    # CORE COMMANDS
    # =========================================================================
    
    # Exit commands
    if any(word in command for word in ['stop', 'goodbye', 'good bye', 'exit', 'quit']):
        speak(get_random_response(GOODBYES))
        return "exit"
    
    # Greeting commands
    elif any(word in command for word in ['hello', 'hi', 'hey']) and len(command.split()) <= 2:
        speak(get_random_response(GREETINGS))
    
    # Time commands
    elif 'time' in command:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"{get_random_response(CONFIRMATIONS)} The current time is {current_time}.")
    
    # =========================================================================
    # SYSTEM CONTROL COMMANDS
    # =========================================================================
    
    # Volume control - Enhanced to handle multiple formats
    elif 'volume' in command:
        if 'mute' in command or 'unmute' in command:
            if mute_volume():
                speak(f"{get_random_response(CONFIRMATIONS)} Volume toggled.")
            else:
                speak(get_random_response(ERROR_RESPONSES))
        elif 'what is the volume' in command or 'current volume' in command:
            vol = get_volume()
            if vol is not None:
                speak(f"The current volume is {vol} percent.")
            else:
                speak("I couldn't check the volume level.")
        else:
            # Handle volume setting - multiple formats supported
            try:
                volume_match = re.search(r'\d+', command)
                if volume_match:
                    level = int(volume_match.group())
                    if 0 <= level <= 100:
                        if set_volume(level):
                            speak(f"{get_random_response(CONFIRMATIONS)} Volume set to {level} percent.")
                        else:
                            speak(get_random_response(ERROR_RESPONSES))
                    else:
                        speak("Please specify a volume between 0 and 100.")
                else:
                    speak("Please specify a volume level, for example: volume 50 or set volume to 75.")
            except:
                speak("I couldn't understand the volume level.")
    
    # Screenshot
    elif 'screenshot' in command or 'take a screenshot' in command:
        filename = take_screenshot()
        if filename:
            speak(f"{get_random_response(COMPLETIONS)} Screenshot saved as {filename}.")
        else:
            speak(get_random_response(ERROR_RESPONSES))
    
    # Lock screen
    elif 'lock screen' in command or 'lock computer' in command:
        speak(f"{get_random_response(CONFIRMATIONS)} Locking the screen now.")
        lock_screen()
    
    # System information
    elif 'system info' in command or 'system information' in command or 'how is my computer' in command:
        info = get_system_info()
        if info:
            response = f"Here's your system status: "
            response += f"CPU usage is at {info['cpu']}%, "
            response += f"memory usage is at {info['memory_percent']}%, "
            if info['battery']:
                response += f"battery is at {info['battery']}%, "
            response += f"and disk usage is at {info['disk_percent']}%."
            speak(response)
        else:
            speak("I couldn't retrieve system information.")
    
    # WiFi information
    elif 'wifi' in command or 'wi-fi' in command:
        profiles = get_wifi_info()
        if profiles:
            speak(f"I found {len(profiles)} WiFi profiles: {', '.join(profiles[:3])}.")
        else:
            speak("I couldn't find any WiFi profiles.")
    
    # =========================================================================
    # PRODUCTIVITY COMMANDS
    # =========================================================================
    
    # Calculator
    elif any(word in command for word in ['calculate', 'math', 'plus', 'minus', 'multiply', 'divide', 'equals']):
        # Extract mathematical expression
        math_expression = re.sub(r'(calculate|math|what is|equals to)', '', command).strip()
        math_expression = math_expression.replace('plus', '+').replace('minus', '-')
        math_expression = math_expression.replace('multiply', '*').replace('times', '*')
        math_expression = math_expression.replace('divide', '/').replace('divided by', '/')
        
        result = calculate(math_expression)
        if result is not None:
            speak(f"The result is {result}.")
        else:
            speak("I couldn't calculate that. Please check your expression.")
    
    # Unit conversion
    elif 'convert' in command:
        try:
            # Parse conversion command (e.g., "convert 100 pounds to kilograms")
            parts = command.split()
            if 'to' in parts:
                to_index = parts.index('to')
                value = float(parts[parts.index('convert') + 1])
                from_unit = parts[parts.index('convert') + 2]
                to_unit = parts[to_index + 1]
                
                result = convert_units(value, from_unit, to_unit)
                if result is not None:
                    speak(f"{value} {from_unit} is {result:.2f} {to_unit}.")
                else:
                    speak("I don't know how to convert those units.")
        except:
            speak("I couldn't understand the conversion. Please try again.")
    
    # Timer
    elif 'timer' in command:
        try:
            minutes_match = re.search(r'(\\d+)\\s*minute', command)
            if minutes_match:
                minutes = int(minutes_match.group(1))
                message = f"Timer for {minutes} minutes is up!"
                set_timer(minutes, message)
                speak(f"{get_random_response(CONFIRMATIONS)} Timer set for {minutes} minutes.")
            else:
                speak("Please specify how many minutes for the timer.")
        except:
            speak("I couldn't set the timer. Please try again.")
    
    # Quick notes
    elif 'note' in command or 'remember' in command:
        note_content = command.replace('note', '').replace('remember', '').strip()
        if save_note(note_content):
            speak(f"{get_random_response(CONFIRMATIONS)} Note saved.")
        else:
            speak(get_random_response(ERROR_RESPONSES))
    
    # =========================================================================
    # FILE MANAGEMENT COMMANDS
    # =========================================================================
    
    # Create folder
    elif 'create folder' in command:
        folder_name = command.replace('create folder', '').strip()
        if create_folder(folder_name):
            speak(f"{get_random_response(COMPLETIONS)} Folder '{folder_name}' created.")
        else:
            speak(get_random_response(ERROR_RESPONSES))
    
    # Search files
    elif 'search for file' in command or 'find file' in command:
        pattern = command.replace('search for file', '').replace('find file', '').strip()
        files = search_files(pattern)
        if files:
            speak(f"I found {len(files)} files: {', '.join([os.path.basename(f) for f in files[:3]])}.")
        else:
            speak(f"No files found matching '{pattern}'.")
    
    # Create file
    elif 'create file' in command:
        filename = command.replace('create file', '').strip()
        if create_file(filename):
            speak(f"{get_random_response(COMPLETIONS)} File '{filename}' created.")
        else:
            speak(get_random_response(ERROR_RESPONSES))
    
    # =========================================================================
    # WINDOWS INTEGRATION COMMANDS
    # =========================================================================
    
    # Minimize windows
    elif 'minimize all windows' in command or 'minimise all windows' in command:
        if minimize_all_windows():
            speak(f"{get_random_response(COMPLETIONS)} All windows minimized.")
        else:
            speak(get_random_response(ERROR_RESPONSES))
    
    # Switch to application
    elif 'switch to' in command:
        app_name = command.replace('switch to', '').strip()
        if switch_window(app_name):
            speak(f"{get_random_response(CONFIRMATIONS)} Switched to {app_name}.")
        else:
            speak(f"I couldn't find {app_name}.")
    
    # Close application
    elif 'close' in command and any(word in command for word in ['application', 'app', 'program']):
        app_name = command.replace('close', '').replace('application', '').replace('app', '').replace('program', '').strip()
        if close_application(app_name):
            speak(f"{get_random_response(COMPLETIONS)} {app_name} closed.")
        else:
            speak(f"I couldn't close {app_name}.")
    
    # =========================================================================
    # WEB SEARCH COMMANDS
    # =========================================================================
    
    # Google search
    elif 'search google for' in command or 'google' in command:
        query = command.replace('search google for', '').replace('google', '').strip()
        if search_google(query):
            speak(f"{get_random_response(CONFIRMATIONS)} Searching Google for {query}.")
        else:
            speak(get_random_response(ERROR_RESPONSES))
    
    # Wikipedia search
    elif 'wikipedia' in command or 'what is' in command:
        query = command.replace('wikipedia', '').replace('what is', '').strip()
        summary = search_wikipedia(query)
        if summary:
            speak(f"Here's what I found: {summary}")
        else:
            speak(f"I couldn't find information about {query} on Wikipedia.")
    
    # =========================================================================
    # SECURITY & PRIVACY COMMANDS
    # =========================================================================
    
    # Generate password
    elif 'generate password' in command:
        try:
            length_match = re.search(r'(\\d+)', command)
            length = int(length_match.group(1)) if length_match else 12
            password = generate_password(length)
            speak(f"I've generated a {length} character password. Check the screen for details.")
            print(f"Generated password: {password}")
        except:
            password = generate_password()
            speak("I've generated a 12 character password. Check the screen for details.")
            print(f"Generated password: {password}")
    
    # Security check
    elif 'security check' in command or 'check security' in command:
        security_info = check_system_security()
        if security_info:
            if security_info['suspicious_count'] > 0:
                speak(f"I found {security_info['suspicious_count']} processes using high CPU.")
            else:
                speak("Your system appears to be running normally.")
        else:
            speak("I couldn't perform a security check.")
    
    # Privacy mode toggle
    elif 'privacy mode' in command:
        if 'on' in command or 'enable' in command:
            PRIVACY_MODE = True
            speak("Privacy mode enabled. I'll use text input only.")
        elif 'off' in command or 'disable' in command:
            PRIVACY_MODE = False
            speak("Privacy mode disabled. Voice interaction restored.")
        else:
            PRIVACY_MODE = not PRIVACY_MODE
            status = "enabled" if PRIVACY_MODE else "disabled"
            speak(f"Privacy mode {status}.")
    
    # =========================================================================
    # WEATHER COMMANDS
    # =========================================================================
    
    elif 'weather' in command:
        if OPENWEATHER_API_KEY == "YOUR_OPENWEATHERMAP_API_KEY":
            speak("Weather functionality requires an API key. Please add your OpenWeatherMap API key to the configuration.")
        elif 'in' in command:
            city = command.split('in')[-1].strip()
            base_url = "http://api.openweathermap.org/data/2.5/weather?"
            complete_url = base_url + "appid=" + OPENWEATHER_API_KEY + "&q=" + city + "&units=metric"
            try:
                response = requests.get(complete_url)
                weather_data = response.json()
                if weather_data.get("cod") == 200:
                    main_data = weather_data["main"]
                    temperature = main_data["temp"]
                    weather_desc = weather_data["weather"][0]["description"]
                    humidity = main_data["humidity"]
                    speak(f"The weather in {city}: {temperature} degrees celsius with {weather_desc}. Humidity is {humidity} percent.")
                else:
                    speak(f"I couldn't find the weather for {city}.")
            except Exception as e:
                speak("I'm having trouble connecting to the weather service.")
        else:
            speak("Which city's weather would you like to know?")
    
    # =========================================================================
    # TO-DO LIST COMMANDS
    # =========================================================================
    
    elif 'add' in command and 'to do list' in command:
        task = command.split('add')[-1].replace('to do list', '').replace('to my to do list', '').strip()
        try:
            with open(TODO_FILE, "a", encoding="utf-8") as f:
                f.write(task + "\\n")
            speak(f"{get_random_response(CONFIRMATIONS)} I've added '{task}' to your list.")
        except Exception as e:
            speak(get_random_response(ERROR_RESPONSES))
    
    elif 'read my to do list' in command or 'show me my to do list' in command:
        try:
            with open(TODO_FILE, "r", encoding="utf-8") as f:
                tasks = f.readlines()
            if not tasks:
                speak("Your to-do list is empty!")
            else:
                response = "Here are your tasks: "
                for i, task in enumerate(tasks[:5]):  # Limit to 5 tasks
                    response += f"{i+1}: {task.strip()}. "
                speak(response)
        except FileNotFoundError:
            speak("You don't have a to-do list yet.")
    
    # =========================================================================
    # APPLICATION OPENING COMMANDS
    # =========================================================================
    
    elif 'open website' in command:
        website = command.replace('open website', '').strip()
        
        # Dictionary of common multi-word websites and their URLs
        website_mapping = {
            'chat gpt': 'https://chat.openai.com',
            'chatgpt': 'https://chat.openai.com',
            'open ai': 'https://openai.com',
            'openai': 'https://openai.com',
            'you tube': 'https://www.youtube.com',
            'youtube': 'https://www.youtube.com',
            'face book': 'https://www.facebook.com',
            'facebook': 'https://www.facebook.com',
            'linked in': 'https://www.linkedin.com',
            'linkedin': 'https://www.linkedin.com',
            'git hub': 'https://github.com',
            'github': 'https://github.com',
            'stack overflow': 'https://stackoverflow.com',
            'google': 'https://www.google.com',
            'gmail': 'https://mail.google.com',
            'google mail': 'https://mail.google.com',
            'google drive': 'https://drive.google.com',
            'google docs': 'https://docs.google.com',
            'whats app': 'https://web.whatsapp.com',
            'whatsapp': 'https://web.whatsapp.com',
            'twitter': 'https://twitter.com',
            'x': 'https://x.com',
            'instagram': 'https://www.instagram.com',
            'reddit': 'https://www.reddit.com',
            'amazon': 'https://www.amazon.com',
            'netflix': 'https://www.netflix.com',
            'spotify': 'https://open.spotify.com',
            'twitch': 'https://www.twitch.tv',
            'discord': 'https://discord.com/app',
            'microsoft teams': 'https://teams.microsoft.com',
            'teams': 'https://teams.microsoft.com',
            'zoom': 'https://zoom.us',
            'slack': 'https://slack.com',
            'notion': 'https://www.notion.so',
            'wikipedia': 'https://www.wikipedia.org',
            'wiki': 'https://www.wikipedia.org'
        }
        
        # Check if it's a known website
        website_lower = website.lower()
        if website_lower in website_mapping:
            speak(f"{get_random_response(CONFIRMATIONS)} Opening {website}.")
            webbrowser.open(website_mapping[website_lower])
        else:
            # For unknown websites, remove spaces and try to form a URL
            website_clean = website.replace(' ', '').lower()
            speak(f"{get_random_response(CONFIRMATIONS)} Opening {website} website.")
            webbrowser.open(f"https://www.{website_clean}.com")
    
    elif 'open' in command:
        app = command.replace('open', '').strip()
        
        # Dictionary of common applications and their executables
        app_mapping = {
            'notepad': 'notepad',
            'calculator': 'calc',
            'paint': 'mspaint',
            'word': 'winword',
            'microsoft word': 'winword',
            'excel': 'excel',
            'microsoft excel': 'excel',
            'powerpoint': 'powerpnt',
            'microsoft powerpoint': 'powerpnt',
            'chrome': 'chrome',
            'google chrome': 'chrome',
            'firefox': 'firefox',
            'edge': 'msedge',
            'microsoft edge': 'msedge',
            'file explorer': 'explorer',
            'explorer': 'explorer',
            'command prompt': 'cmd',
            'cmd': 'cmd',
            'powershell': 'powershell',
            'task manager': 'taskmgr',
            'control panel': 'control',
            'settings': 'ms-settings:',
            'vs code': 'code',
            'visual studio code': 'code'
        }
        
        app_lower = app.lower()
        
        # Check if it's a known application
        if app_lower in app_mapping:
            speak(f"{get_random_response(CONFIRMATIONS)} Opening {app}.")
            try:
                subprocess.Popen(f'start {app_mapping[app_lower]}', shell=True)
            except:
                speak(f"I couldn't open {app}. It might not be installed.")
        else:
            # For unknown apps, try as-is
            speak(f"{get_random_response(CONFIRMATIONS)} Opening {app}.")
            try:
                subprocess.call(['start', '', f'{app}.exe'], shell=True)
            except Exception as e:
                speak(f"I had trouble opening {app}.")
    
    
    # =========================================================================
    # HELP COMMAND
    # =========================================================================
    
    elif 'help' in command or 'commands' in command:
        # Short spoken response
        spoken_help = "I can help you with system control like volume and screenshots, productivity tools like calculator and timer, file management, web search, opening applications, and much more. Check your screen for detailed examples."
        speak(spoken_help)
        
        # Detailed text help for screen
        help_text = """
        Here are some things I can help you with:
        
        System Control:
        • "Set volume to 50" - Control system volume
        • "Take a screenshot" - Capture your screen
        • "Lock screen" - Lock your computer
        • "System info" - Get system performance data
        
        Productivity:
        • "Calculate 25 times 4" - Math calculations
        • "Convert 100 pounds to kilograms" - Unit conversions
        • "Set timer for 5 minutes" - Background timers
        • "Note remember to call mom" - Quick notes
        
        File Management:
        • "Create folder Projects" - Make new folders
        • "Search for file report" - Find files
        • "Create file test.txt" - Make new files
        
        Web & Information:
        • "Search Google for Python tutorials" - Web search
        • "What is machine learning" - Wikipedia search
        • "Weather in New York" - Weather information
        
        Windows Control:
        • "Minimize all windows" - Window management
        • "Switch to Chrome" - Application switching
        • "Close application notepad" - Close programs
        
        Security:
        • "Generate password 16" - Secure passwords
        • "Security check" - System monitoring
        • "Privacy mode on" - Toggle privacy mode
        
        Say "stop" or "goodbye" to exit.
        """
        print(help_text)
    
    # =========================================================================
    # UNKNOWN COMMAND HANDLING
    # =========================================================================
    
    else:
        responses = [
            "I'm not sure how to help with that.",
            "Could you rephrase that?",
            "I didn't understand. Can you try again?",
            "That's not something I can do yet.",
            "I'm still learning. Could you try a different command?"
        ]
        speak(random.choice(responses))

# =============================================================================
# MAIN PROGRAM
# =============================================================================

def main():
    """Main program function"""
    global listen_enabled
    
    print("\n" + "="*60)
    print("       AI Voice Assistant")
    print("="*60)
    print("Available features:")
    print("• System Control (volume, screenshots, lock screen)")
    print("• Productivity (calculator, timer, notes)")
    print("• File Management (create, search, organize)")
    print("• Web Search (Google, Wikipedia)")
    print("• Windows Integration (window management)")
    print("• Security Features (password generator, system check)")
    print("• Weather Information")
    print("• And much more!")
    print("\nSay 'help' for command examples or 'stop' to exit.")
    print("="*60 + "\n")
    
    if not VOICE_ID:
        print("Warning: ElevenLabs voice not configured. Using fallback TTS.")
    
    # Initial greeting
    greeting_messages = [
        "Hello! AI Voice Assistant is online and ready to help!",
        "Hi there! I'm your AI Voice Assistant!",
        "Hey! AI Assistant here, ready to make your day more productive!"
    ]
    speak(random.choice(greeting_messages))
    
    # Main interaction loop
    try:
        if WAKE_WORD_MODE:
            print(f"\nWake word mode enabled. Say '{WAKE_WORD}' followed by your command.")
            continuous_listen()
        else:
            while listen_enabled:
                command = listen_for_command()
                if command:
                    result = process_command(command)
                    if result == "exit":
                        break
                        
    except KeyboardInterrupt:
        speak("Goodbye! Thanks for using AI Voice Assistant!")
    except Exception as e:
        print(f"An error occurred: {e}")
        speak("I encountered an error. Goodbye for now.")
    
    print("\nAI Voice Assistant shutdown complete.")

if __name__ == "__main__":
    main()
