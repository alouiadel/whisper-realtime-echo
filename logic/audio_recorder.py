"""Audio recording functionality using sounddevice."""
import os
import tempfile
import sounddevice as sd
import soundfile as sf
import numpy as np
import threading

class AudioRecorder:
    """Records audio from the microphone and saves it to a file."""
    
    def __init__(self, on_status_update=None):
        """Initialize the recorder.
        
        Args:
            on_status_update: Callback for status updates
        """
        self.sample_rate = 16000
        self.channels = 1
        self.is_recording = False
        self.recording_thread = None
        self.recorded_data = []
        self.on_status_update = on_status_update
        self.temp_file = None
    
    def start_recording(self):
        """Start recording audio from the microphone."""
        if self.is_recording:
            return
        
        self.is_recording = True
        self.recorded_data = []
        
        if self.on_status_update:
            self.on_status_update("Recording started...")
        
        self.recording_thread = threading.Thread(
            target=self._record_thread,
            daemon=True
        )
        self.recording_thread.start()
    
    def stop_recording(self):
        """Stop recording and save the recorded audio to a file.
        
        Returns:
            Path to the recorded audio file
        """
        if not self.is_recording:
            return None
        
        self.is_recording = False
        
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join()
        
        if not self.recorded_data:
            if self.on_status_update:
                self.on_status_update("No audio recorded")
            return None
        
        audio_data = np.concatenate(self.recorded_data, axis=0)
        
        fd, filepath = tempfile.mkstemp(suffix='.wav')
        os.close(fd)
        
        sf.write(filepath, audio_data, self.sample_rate)
        
        self.temp_file = filepath
        
        if self.on_status_update:
            self.on_status_update("Recording saved")
        
        return filepath
    
    def _record_thread(self):
        """Background thread for recording audio."""
        def callback(indata, frames, time, status):
            if status:
                print(f"Recording status: {status}")
            self.recorded_data.append(indata.copy())
        
        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=callback
        ):
            while self.is_recording:
                sd.sleep(100)
    
    def cleanup(self):
        """Remove temporary files."""
        if self.temp_file and os.path.exists(self.temp_file):
            try:
                os.remove(self.temp_file)
                self.temp_file = None
            except Exception as e:
                print(f"Error removing temp file: {e}") 