import obsws_python as obs
import threading
import time
import json
import os
import sys
import logging
from typing import Set
import pyaudio
import numpy as np
import keyboard
import wx
from accessible_output3.outputs import auto

class ConfigDialog(wx.Dialog):
    def __init__(self):
        super().__init__(None, title="OBS WebSocket Configuration", 
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        
        self.host = "localhost"
        self.port = 4455
        self.password = ""
        self.use_speech = False
        self.use_tones = True  # Default to True
        
        self.create_widgets()
        self.layout_widgets()
        self.bind_events()
        
        # Center the dialog
        self.Center()
        
    def create_widgets(self):
        """Create the input widgets"""
        # Host input
        self.host_label = wx.StaticText(self, label="Host:")
        self.host_ctrl = wx.TextCtrl(self, value="localhost", size=(200, -1))
        
        # Port input
        self.port_label = wx.StaticText(self, label="Port:")
        self.port_ctrl = wx.SpinCtrl(self, value="4455", min=1, max=65535, size=(100, -1))
        
        # Password input
        self.password_label = wx.StaticText(self, label="Password (optional):")
        self.password_ctrl = wx.TextCtrl(self, value="", style=wx.TE_PASSWORD, size=(200, -1))
        
        # Notification checkboxes (without a label)
        self.speech_checkbox = wx.CheckBox(self, label="Use Speech")
        self.tones_checkbox = wx.CheckBox(self, label="Use Tones")
        
        # Set default values
        self.speech_checkbox.SetValue(False)  # Default to False
        self.tones_checkbox.SetValue(True)    # Default to True
        
        # Buttons with accelerator keys
        self.ok_button = wx.Button(self, wx.ID_OK, "&Save && Connect")
        self.cancel_button = wx.Button(self, wx.ID_CANCEL, "Use &Defaults")
        
        # Set default button
        self.ok_button.SetDefault()
        
    def layout_widgets(self):
        """Layout the widgets using sizers"""
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Add some padding
        main_sizer.Add((0, 10))
        
        # Host row
        host_sizer = wx.BoxSizer(wx.HORIZONTAL)
        host_sizer.Add(self.host_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        host_sizer.Add(self.host_ctrl, 1, wx.EXPAND)
        main_sizer.Add(host_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)
        main_sizer.Add((0, 10))
        
        # Port row
        port_sizer = wx.BoxSizer(wx.HORIZONTAL)
        port_sizer.Add(self.port_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        port_sizer.Add(self.port_ctrl, 0)
        main_sizer.Add(port_sizer, 0, wx.LEFT | wx.RIGHT, 20)
        main_sizer.Add((0, 10))
        
        # Password row
        password_sizer = wx.BoxSizer(wx.HORIZONTAL)
        password_sizer.Add(self.password_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        password_sizer.Add(self.password_ctrl, 1, wx.EXPAND)
        main_sizer.Add(password_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)
        main_sizer.Add((0, 15))
        
        # Checkbox row (without label)
        checkbox_sizer = wx.BoxSizer(wx.HORIZONTAL)
        checkbox_sizer.Add(self.speech_checkbox, 0, wx.RIGHT, 20)
        checkbox_sizer.Add(self.tones_checkbox, 0)
        main_sizer.Add(checkbox_sizer, 0, wx.LEFT | wx.RIGHT, 20)
        main_sizer.Add((0, 15))
        
        # Button row
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.cancel_button, 0, wx.RIGHT, 10)
        button_sizer.Add(self.ok_button, 0)
        main_sizer.Add(button_sizer, 0, wx.ALIGN_RIGHT | wx.LEFT | wx.RIGHT, 20)
        main_sizer.Add((0, 15))
        
        self.SetSizer(main_sizer)
        self.Fit()
        
    def bind_events(self):
        """Bind events"""
        self.Bind(wx.EVT_BUTTON, self.on_ok, self.ok_button)
        self.Bind(wx.EVT_BUTTON, self.on_cancel, self.cancel_button)
        
        # Handle keyboard shortcuts
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)
        
        # Set up accelerator table for Alt+S and Alt+D
        entries = []
        entries.append(wx.AcceleratorEntry(wx.ACCEL_ALT, ord('S'), self.ok_button.GetId()))
        entries.append(wx.AcceleratorEntry(wx.ACCEL_ALT, ord('D'), self.cancel_button.GetId()))
        accel_table = wx.AcceleratorTable(entries)
        self.SetAcceleratorTable(accel_table)
        
    def on_key(self, event):
        """Handle key events"""
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            # Check if neither option is selected
            if not self.speech_checkbox.GetValue() and not self.tones_checkbox.GetValue():
                self.show_error_and_exit()
            else:
                # Use CallAfter to ensure proper cleanup for screen readers
                wx.CallAfter(self.EndModal, wx.ID_CANCEL)
        else:
            event.Skip()
            
    def on_ok(self, event):
        """Handle OK button (Alt+S)"""
        # Validate inputs
        host = self.host_ctrl.GetValue().strip()
        if not host:
            wx.MessageBox("Host cannot be empty", "Error", wx.OK | wx.ICON_ERROR)
            return
            
        # Check if neither notification option is selected
        if not self.speech_checkbox.GetValue() and not self.tones_checkbox.GetValue():
            self.show_error_and_exit()
            return
        
        port = self.port_ctrl.GetValue()
        password = self.password_ctrl.GetValue()
        
        # Store values
        self.host = host
        self.port = port
        self.password = password
        self.use_speech = self.speech_checkbox.GetValue()
        self.use_tones = self.tones_checkbox.GetValue()
        
        self.EndModal(wx.ID_OK)
        
    def on_cancel(self, event):
        """Handle Cancel button (Alt+D) - use defaults"""
        # Check if neither option is selected
        if not self.speech_checkbox.GetValue() and not self.tones_checkbox.GetValue():
            self.show_error_and_exit()
            return
            
        self.host = "localhost"
        self.port = 4455
        self.password = ""
        self.use_speech = self.speech_checkbox.GetValue()
        self.use_tones = self.tones_checkbox.GetValue()
        self.EndModal(wx.ID_CANCEL)
        
    def show_error_and_exit(self):
        """Show error message and exit application"""
        dlg = wx.MessageDialog(
            self,
            "You must select at least one notification option (Speech or Tones).",
            "Error",
            wx.OK | wx.ICON_ERROR
        )
        dlg.ShowModal()
        dlg.Destroy()
        self.EndModal(wx.ID_CLOSE)
        
    def get_config(self):
        """Get the configuration values"""
        return {
            'host': self.host,
            'port': self.port,
            'password': self.password,
            'use_speech': self.use_speech,
            'use_tones': self.use_tones
        }

class OBSSourceMonitor:
    def __init__(self):
        # Initialize speech output
        self.speech = auto.Auto()
        
        # Load configuration
        self.config = self.load_config()
        
        # Apply configuration settings
        self.host = self.config['host']
        self.port = self.config['port']
        self.password = self.config['password']
        self.volume = self.config['volume']
        self.poll_interval = self.config['poll_interval']
        self.max_consecutive_errors = self.config['max_consecutive_errors']
        self.sample_rate = self.config['sample_rate']
        
        # Notification settings
        self.use_speech = self.config.get('use_speech', False)  # Default to False
        self.use_tones = self.config.get('use_tones', True)    # Default to True
        
        # Connection and monitoring state
        self.ws = None
        self.currently_visible_sources: Set[str] = set()
        self.monitoring = False
        self.should_exit = False
        self.exit_tone_played = False
        self.connection_lost = False
        self.consecutive_errors = 0
        self._health_check_counter = 0
        
        # Threading locks
        self.exit_lock = threading.Lock()
        self.monitor_lock = threading.Lock()
        self.audio_lock = threading.Lock()
        self.speech_lock = threading.Lock()
        
        # Audio setup
        self.audio_p = None
        if self.use_tones:
            self._init_audio()
        
        # Setup logging
        self.setup_logging()

    def speak(self, text):
        """Speak text using accessible_output3"""
        if not self.use_speech:
            return
            
        with self.speech_lock:
            try:
                self.speech.speak(text)
            except Exception as e:
                self.logger.error(f"Error speaking text '{text}': {e}")

    def speak_threaded(self, text):
        """Speak text in a background thread"""
        if not self.use_speech:
            return
        threading.Thread(target=lambda: self.speak(text), daemon=True).start()

    def show_config_dialog(self):
        """Show configuration dialog and return config"""
        try:
            app = wx.App()
            dialog = ConfigDialog()
            
            result = dialog.ShowModal()
            config = dialog.get_config()
            
            # Handle the special case where user exited due to no notification options
            if result == wx.ID_CLOSE:
                dialog.Destroy()
                wx.SafeYield()
                app.Destroy()
                sys.exit(0)
            
            dialog.Destroy()
            # Add small delay for screen readers
            wx.SafeYield()
            app.Destroy()
            
            return config, result == wx.ID_OK
            
        except Exception as e:
            print(f"Error showing config dialog: {e}")
            # Fallback to defaults with tones enabled, speech disabled
            return {
                'host': 'localhost',
                'port': 4455,
                'password': '',
                'use_speech': False,
                'use_tones': True
            }, False

    def load_config(self):
        """Load configuration from file with defaults, show dialog if no config exists"""
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
        
        default_config = {
            'host': 'localhost',
            'port': 4455,
            'password': '',
            'volume': 0.4,
            'poll_interval': 0.1,
            'max_consecutive_errors': 3,
            'sample_rate': 44100,
            'hotkey': 'shift+win+f4',
            'fallback_hotkey': 'ctrl+shift+f4',
            'use_speech': False,  # Default to False
            'use_tones': True,    # Default to True
            'tones': {
                'startup': [523, 784],
                'connected': [523, 659, 784],
                'source_shown': 800,
                'source_hidden': 400,
                'error': [400, 300],
                'connection_lost': [500, 400, 300],
                'exit': [659, 523, 392]
            },
            'tone_durations': {
                'startup': [0.12, 0.15],
                'connected': 0.12,
                'source': 0.08,
                'error': 0.08,
                'connection_lost': 0.06,
                'exit': 0.25
            }
        }
        
        config_exists = os.path.exists(config_file)
        
        if config_exists:
            # Load existing config
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    # Merge user config with defaults (deep merge for nested dicts)
                    self._deep_update(default_config, user_config)
            except Exception as e:
                print(f"Error loading config: {e}")
                config_exists = False
        
        if not config_exists:
            # Show configuration dialog
            dialog_config, save_config = self.show_config_dialog()
            
            # Update connection settings from dialog
            default_config['host'] = dialog_config['host']
            default_config['port'] = dialog_config['port']
            default_config['password'] = dialog_config['password']
            default_config['use_speech'] = dialog_config['use_speech']
            default_config['use_tones'] = dialog_config['use_tones']
            
            # Always save config file (whether user pressed Save or Use Defaults)
            self.save_config(config_file, default_config)
        
        return default_config

    def _deep_update(self, base_dict, update_dict):
        """Recursively update nested dictionaries"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value

    def save_config(self, config_file, config):
        """Save configuration to file"""
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def setup_logging(self):
        """Setup logging to file"""
        log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'errors.log')
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.ERROR)
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.ERROR)
        self.logger.addHandler(file_handler)
        self.logger.propagate = False

    def _init_audio(self):
        """Initialize PyAudio once"""
        try:
            self.audio_p = pyaudio.PyAudio()
        except Exception as e:
            print(f"Failed to initialize audio: {e}")
            self.audio_p = None

    def _cleanup_audio(self):
        """Clean up audio resources"""
        if self.audio_p:
            try:
                self.audio_p.terminate()
            except:
                pass
            self.audio_p = None

    def play_tone_blocking(self, frequency, duration=0.1):
        """Play a single tone - blocking version with improved resource management"""
        if not self.use_tones or not self.audio_p:
            if self.use_tones:
                self._init_audio()
                if not self.audio_p:
                    return

        with self.audio_lock:
            stream = None
            try:
                stream = self.audio_p.open(
                    format=pyaudio.paFloat32,
                    channels=1,
                    rate=self.sample_rate,
                    output=True,
                    frames_per_buffer=1024
                )
                
                frames = int(duration * self.sample_rate)
                wave = np.sin(frequency * 2 * np.pi * np.linspace(0, duration, frames))
                
                # Improved fade to prevent clicks
                fade_frames = min(int(0.005 * self.sample_rate), frames // 4)
                if fade_frames > 0:
                    fade_in = np.linspace(0, 1, fade_frames)
                    fade_out = np.linspace(1, 0, fade_frames)
                    wave[:fade_frames] *= fade_in
                    wave[-fade_frames:] *= fade_out
                
                wave = (wave * self.volume).astype(np.float32)
                stream.write(wave.tobytes())
                
            except Exception as e:
                self.logger.error(f"Error playing tone {frequency}Hz: {e}")
            finally:
                if stream:
                    try:
                        stream.stop_stream()
                        stream.close()
                    except:
                        pass

    def play_tone(self, frequency, duration=0.1):
        """Play a tone in background thread"""
        if not self.use_tones:
            return
        threading.Thread(target=lambda: self.play_tone_blocking(frequency, duration), daemon=True).start()

    def play_chord_blocking(self, frequencies, duration=0.15):
        """Play multiple frequencies at once - blocking"""
        if not self.use_tones or not self.audio_p:
            if self.use_tones:
                self._init_audio()
                if not self.audio_p:
                    return

        with self.audio_lock:
            stream = None
            try:
                stream = self.audio_p.open(
                    format=pyaudio.paFloat32,
                    channels=1,
                    rate=self.sample_rate,
                    output=True,
                    frames_per_buffer=1024
                )
                
                frames = int(duration * self.sample_rate)
                wave = np.zeros(frames)
                
                for freq in frequencies:
                    freq_wave = np.sin(freq * 2 * np.pi * np.linspace(0, duration, frames))
                    wave += freq_wave / len(frequencies)
                
                # Improved fade
                fade_frames = min(int(0.01 * self.sample_rate), frames // 4)
                if fade_frames > 0:
                    fade_in = np.linspace(0, 1, fade_frames)
                    fade_out = np.linspace(1, 0, fade_frames)
                    wave[:fade_frames] *= fade_in
                    wave[-fade_frames:] *= fade_out
                
                wave = (wave * self.volume).astype(np.float32)
                stream.write(wave.tobytes())
                
            except Exception as e:
                self.logger.error(f"Error playing chord: {e}")
            finally:
                if stream:
                    try:
                        stream.stop_stream()
                        stream.close()
                    except:
                        pass

    def play_sequence_blocking(self, frequencies, durations, gaps=None):
        """Play a sequence of tones with gaps"""
        if not self.use_tones:
            return
            
        if gaps is None:
            gaps = [0.05] * (len(frequencies) - 1)
        
        for i, (freq, dur) in enumerate(zip(frequencies, durations)):
            self.play_tone_blocking(freq, dur)
            if i < len(gaps):
                time.sleep(gaps[i])

    def play_system_sound(self, sound_type: str):
        """Play system notification sounds based on configuration"""
        try:
            tones = self.config['tones']
            durations = self.config['tone_durations']
            
            if sound_type == "startup":
                if self.use_speech:
                    self.speak("OBS Monitor started")
                if self.use_tones:
                    freqs = tones['startup']
                    durs = durations['startup']
                    self.play_sequence_blocking(freqs, durs)
                
            elif sound_type == "connected":
                if self.use_speech:
                    self.speak("Connected to OBS")
                if self.use_tones:
                    freqs = tones['connected']
                    dur = durations['connected']
                    self.play_chord_blocking(freqs, dur)
                
            elif sound_type == "failed" or sound_type == "failed_blocking":
                if self.use_speech:
                    self.speak("Failed to connect to OBS")
                if self.use_tones:
                    freqs = tones['error']
                    dur = durations['error']
                    self.play_sequence_blocking(freqs, [dur, dur])
                
            elif sound_type == "connection_lost":
                if self.use_speech:
                    self.speak("Connection lost")
                if self.use_tones:
                    freqs = tones['connection_lost']
                    dur = durations['connection_lost']
                    gaps = [0.03, 0.03]
                    self.play_sequence_blocking(freqs, [dur] * len(freqs), gaps)
                
            elif sound_type == "exit":
                if self.use_speech:
                    self.speak("OBS Monitor exiting")
                if self.use_tones:
                    freqs = tones['exit']
                    dur = durations['exit']
                    self.play_chord_blocking(freqs, dur)
                
        except Exception as e:
            self.logger.error(f"Error playing system sound '{sound_type}': {e}")

    def play_source_sound(self, sound_type: str, source_names=None):
        """Play quick tones and speech for source changes with source names"""
        try:
            tones = self.config['tones']
            dur = self.config['tone_durations']['source']
            
            if sound_type == "shown":
                if self.use_speech and source_names:
                    # Announce each source name
                    for source_name in source_names:
                        message = f"{source_name} shown"
                        self.speak_threaded(message)
                if self.use_tones:
                    self.play_tone(tones['source_shown'], dur)
                    
            elif sound_type == "hidden":
                if self.use_speech and source_names:
                    # Announce each source name
                    for source_name in source_names:
                        message = f"{source_name} hidden"
                        self.speak_threaded(message)
                if self.use_tones:
                    self.play_tone(tones['source_hidden'], dur)
                
        except Exception as e:
            self.logger.error(f"Error playing source sound '{sound_type}': {e}")

    def setup_hotkey(self):
        """Setup global hotkey for exit with fallback"""
        try:
            keyboard.add_hotkey(self.config['hotkey'], self.trigger_exit)
        except Exception as e:
            try:
                keyboard.add_hotkey(self.config['fallback_hotkey'], self.trigger_exit)
            except Exception as e2:
                self.logger.error(f"Failed to setup hotkeys: {e}, {e2}")

    def trigger_exit(self):
        """Triggered by hotkey - signals exit"""
        self.should_exit = True

    def play_exit_tone(self):
        """Play exit tone and mark as played"""
        with self.exit_lock:
            if not self.exit_tone_played:
                self.play_system_sound("exit")
                self.exit_tone_played = True

    def exit_program(self):
        """Exit the program gracefully"""
        self.play_exit_tone()
        time.sleep(0.4)
        self.stop_monitoring()

    def is_connection_alive(self):
        """Check if the WebSocket connection is still alive"""
        try:
            if not self.ws:
                return False
            self.ws.get_version()
            return True
        except Exception:
            return False

    def connect_to_obs(self):
        """Connect to OBS WebSocket"""
        try:
            self.ws = obs.ReqClient(host=self.host, port=self.port, password=self.password)
            if self.is_connection_alive():
                return True
            else:
                self.ws = None
                return False
        except Exception as e:
            self.logger.error(f"Failed to connect to OBS: {e}")
            self.ws = None
            return False

    def connect_to_obs_with_retry(self, max_retries=3, retry_delay=2.0, play_sounds=True):
        """Connect with retry logic and exponential backoff"""
        for attempt in range(max_retries):
            try:
                if self.connect_to_obs():
                    if play_sounds:  # Play sound on every successful connection
                        self.play_system_sound("connected")
                    self.consecutive_errors = 0
                    return True
                
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 1.5  # Exponential backoff
                    
            except Exception as e:
                self.logger.error(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 1.5
        
        if play_sounds:
            self.play_system_sound("failed_blocking")
        return False

    def disconnect_from_obs(self):
        """Disconnect from OBS WebSocket"""
        if self.ws:
            try:
                self.ws.disconnect()
            except:
                pass
            finally:
                self.ws = None

    def handle_connection_loss(self):
        """Handle connection loss with reconnection attempt"""
        if self.connection_lost:  # Prevent multiple calls
            return False
            
        self.connection_lost = True
        self.play_system_sound("connection_lost")
        
        # Try to reconnect after a delay
        time.sleep(2.0)
        if not self.should_exit:
            if self.connect_to_obs_with_retry(max_retries=2, play_sounds=True):
                self.connection_lost = False
                self.consecutive_errors = 0
                return True
        return False

    def get_visible_sources(self) -> Set[str]:
        """Get all currently visible sources"""
        visible_sources = set()
        
        try:
            current_scene_response = self.ws.get_current_program_scene()
            current_scene = current_scene_response.current_program_scene_name
            
            scene_items_response = self.ws.get_scene_item_list(current_scene)
            scene_items = scene_items_response.scene_items
            
            for item in scene_items:
                try:
                    item_enabled_response = self.ws.get_scene_item_enabled(
                        current_scene, item['sceneItemId']
                    )
                    
                    if item_enabled_response.scene_item_enabled:
                        visible_sources.add(item['sourceName'])
                except Exception:
                    continue
            
            self.consecutive_errors = 0
            
        except Exception as e:
            self.logger.error(f"Error getting visible sources: {e}")
            raise
        
        return visible_sources

    def monitor_sources(self):
        """Enhanced monitoring loop with connection loss detection and recovery"""
        try:
            self.currently_visible_sources = self.get_visible_sources()
            
            while self.monitoring and not self.should_exit:
                try:
                    # Periodic connection health check
                    self._health_check_counter += 1
                    if self._health_check_counter % 30 == 0:
                        if not self.is_connection_alive():
                            if self.handle_connection_loss():
                                # Successfully reconnected, continue monitoring
                                continue
                            else:
                                # Failed to reconnect, exit monitoring
                                break
                    
                    new_visible_sources = self.get_visible_sources()
                    
                    # Check for changes
                    newly_shown = new_visible_sources - self.currently_visible_sources
                    newly_hidden = self.currently_visible_sources - new_visible_sources
                    
                    if newly_shown:
                        self.play_source_sound("shown", list(newly_shown))
                    
                    if newly_hidden:
                        self.play_source_sound("hidden", list(newly_hidden))
                    
                    self.currently_visible_sources = new_visible_sources
                    self.consecutive_errors = 0
                    
                    time.sleep(self.poll_interval)
                    
                except Exception as e:
                    self.consecutive_errors += 1
                    self.logger.error(f"Error in monitoring (attempt {self.consecutive_errors}): {e}")
                    
                    if self.consecutive_errors >= self.max_consecutive_errors:
                        if self.handle_connection_loss():
                            # Successfully reconnected, reset and continue
                            continue
                        else:
                            # Failed to reconnect, exit monitoring
                            break
                    
                    # Exponential backoff for errors
                    error_delay = min(0.5 * (2 ** (self.consecutive_errors - 1)), 5.0)
                    time.sleep(error_delay)
                    
        except Exception as e:
            self.logger.error(f"Fatal error in monitor_sources: {e}")
            # Don't call handle_connection_loss here to avoid duplicate sounds
            self.connection_lost = True

    def start_monitoring(self):
        """Start monitoring with retry logic"""
        if not self.connect_to_obs_with_retry():
            return False
        
        self.monitoring = True
        self.connection_lost = False
        self.consecutive_errors = 0
        self._health_check_counter = 0
        self.monitor_thread = threading.Thread(target=self.monitor_sources, daemon=True)
        self.monitor_thread.start()
        return True

    def stop_monitoring(self):
        """Stop monitoring with proper cleanup"""
        self.monitoring = False
        self.should_exit = True
        
        # Wait for monitor thread to finish (with timeout)
        if hasattr(self, 'monitor_thread') and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2.0)
        
        self.disconnect_from_obs()
        if self.use_tones:
            self._cleanup_audio()

def main():
    """Main function with improved error handling and reconnection logic"""
    monitor = None
    try:
        monitor = OBSSourceMonitor()
        monitor.play_system_sound("startup")
        monitor.setup_hotkey()
        
        # Initial connection with retries
        if not monitor.start_monitoring():
            sys.exit(1)
        
        try:
            # Main monitoring loop
            while not monitor.should_exit:
                if monitor.connection_lost:
                    # Connection was lost and couldn't be restored
                    # Don't play exit tone here since connection_lost tone was already played
                    monitor.stop_monitoring()
                    sys.exit(1)
                time.sleep(0.1)
            
            # Normal exit (hotkey triggered)
            monitor.exit_program()
            
        except KeyboardInterrupt:
            monitor.exit_program()
            
    except Exception as e:
        logging.error(f"Fatal application error: {e}")
        if monitor:
            try:
                monitor.play_system_sound("failed")
            except:
                pass
        sys.exit(1)
    finally:
        if monitor:
            monitor.stop_monitoring()

if __name__ == "__main__":
    main()