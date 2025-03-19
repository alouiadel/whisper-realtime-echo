# this is based on code from : https://github.com/Softcatala/whisper-ctranslate2/blob/main/src/whisper_ctranslate2/live.py
# which is by itself based on code from : https://github.com/Nikorasu/LiveWhisper/blob/main/livewhisper.py

"""Live transcription module using faster-whisper and sounddevice."""
from typing import List, Union, Callable, Optional
import numpy as np
import threading
import multiprocessing
from faster_whisper import WhisperModel

BlockSize = 30
Vocals = [50, 1000]
EndBlocks = 33 * 1
FlushBlocks = 33 * 5

def get_optimal_thread_count():
    """Calculate optimal thread count (70% of available CPU cores)."""
    cpu_count = multiprocessing.cpu_count()
    optimal_threads = max(1, int(cpu_count * 0.7))
    return optimal_threads

try:
    import sounddevice as sd
    sounddevice_available = True
    sounddevice_exception = None
except Exception as e:
    sounddevice_available = False
    sounddevice_exception = e


class LiveTranscription:
    """Live transcription service using microphone input and faster-whisper model."""
    
    def __init__(
        self,
        on_transcription: Callable[[str], None],
        on_status_update: Callable[[str], None],
        on_error: Callable[[str], None],
        model_path: str,
        device: str = "cpu",
        device_index: Union[int, List[int]] = 0,
        compute_type: str = "int8",
        language: str = None,
        task: str = "transcribe",
        threads: int = None,
        threshold: float = 0.1,
        input_device: Optional[int] = None,
        input_device_sample_rate: int = 16000,
        vad_filter: bool = True,
    ):
        """Initialize live transcription.
        
        Args:
            on_transcription: Callback for transcription results
            on_status_update: Callback for status updates
            on_error: Callback for error handling
            model_path: Path or name of the Whisper model
            device: Device to run model on ('cpu' or 'cuda')
            device_index: Device index for CUDA
            compute_type: Compute type ('int8', 'float16', or 'float32')
            language: Language code (None for auto-detection)
            task: Task to perform ('transcribe' or 'translate')
            threads: Number of CPU threads to use (default: 70% of available cores)
            threshold: Voice activity detection threshold
            input_device: Input device index (None for default)
            input_device_sample_rate: Input device sample rate
            vad_filter: Whether to use VAD filter to remove silence
        """
        self.on_transcription = on_transcription
        self.on_status_update = on_status_update
        self.on_error = on_error
        
        self.model_path = model_path
        self.device = device
        self.device_index = device_index
        self.compute_type = compute_type
        self.language = language
        self.task = task
        self.threads = threads if threads is not None else get_optimal_thread_count()
        self.threshold = threshold
        self.input_device = input_device
        self.input_device_sample_rate = input_device_sample_rate
        self.vad_filter = vad_filter
        
        self.running = False
        self.waiting = 0
        self.prevblock = self.buffer = np.zeros((0, 1))
        self.speaking = False
        self.blocks_speaking = 0
        self.buffers_to_process = []
        self.transcribe_model = None
        self._thread = None
    
    @staticmethod
    def is_available():
        """Check if sounddevice is available."""
        return sounddevice_available

    def _is_there_voice(self, indata, frames):
        """Detect if there is voice in the audio data."""
        freq = (
            np.argmax(np.abs(np.fft.rfft(indata[:, 0])))
            * self.input_device_sample_rate
            / frames
        )
        volume = np.sqrt(np.mean(indata**2))
        
        return volume > self.threshold and Vocals[0] <= freq <= Vocals[1]
    
    def _save_to_process(self):
        """Save buffer for processing and reset buffer."""
        self.buffers_to_process.append(self.buffer.copy())
        self.buffer = np.zeros((0, 1))
        self.speaking = False
    
    def callback(self, indata, frames, _time, _status):
        """Audio callback for processing microphone input."""
        if not self.running or not any(indata):
            return
        
        voice = self._is_there_voice(indata, frames)
        
        if not voice and not self.speaking:
            return
        
        if voice:
            if self.waiting < 1:
                self.buffer = self.prevblock.copy()
            
            self.buffer = np.concatenate((self.buffer, indata))
            self.waiting = EndBlocks
            
            if not self.speaking:
                self.blocks_speaking = FlushBlocks
            
            self.speaking = True
        else:
            self.waiting -= 1
            if self.waiting < 1:
                self._save_to_process()
                return
            else:
                self.buffer = np.concatenate((self.buffer, indata))
        
        self.blocks_speaking -= 1
        if self.blocks_speaking < 1:
            self._save_to_process()
    
    def _process_buffers(self):
        """Process audio buffers and transcribe them."""
        try:
            while self.running:
                if len(self.buffers_to_process) > 0:
                    _buffer = self.buffers_to_process.pop(0)
                    try:
                        result = self.transcribe_model.transcribe(
                            _buffer.flatten().astype("float32"),
                            task=self.task,
                            language=self.language,
                            vad_filter=self.vad_filter,
                            beam_size=1,
                            best_of=1,
                            patience=0.7,
                            temperature=[0.0],
                            condition_on_previous_text=False,
                            without_timestamps=True,
                            word_timestamps=False,
                        )
                        
                        segments, _ = result
                        text = " ".join([segment.text for segment in segments])
                        
                        if text.strip():
                            self.on_transcription(text)
                    except Exception as e:
                        self.on_error(f"Transcription error: {str(e)}")
        except Exception as e:
            self.on_error(f"Live transcription error: {str(e)}")
    
    def start(self):
        """Start live transcription."""
        if not sounddevice_available:
            self.on_error("sounddevice library is not available")
            return False
        
        if self.running:
            return True
        
        try:
            self.on_status_update("Initializing live transcription model...")
            
            model_path = self.model_path
            if self.model_path == "tiny.en":
                model_path = "int8_tiny_en"
                self.on_status_update("Using local tiny.en model")
            elif self.model_path == "tiny":
                model_path = "int8_tiny"
                self.on_status_update("Using local tiny model")
            
            self.transcribe_model = WhisperModel(
                model_path,
                device=self.device,
                device_index=self.device_index,
                compute_type=self.compute_type,
                cpu_threads=self.threads,
            )
            
            vad_status = " with VAD filter" if self.vad_filter else ""
            self.on_status_update(f"Live transcription ready (using {self.compute_type}{vad_status}, {self.threads} threads)")
            
            self.running = True
            self.buffer = np.zeros((0, 1))
            self.prevblock = np.zeros((0, 1))
            self.buffers_to_process = []
            
            self._thread = threading.Thread(
                target=self._process_buffers,
                daemon=True
            )
            self._thread.start()
            
            self.stream = sd.InputStream(
                channels=1,
                callback=self.callback,
                blocksize=int(self.input_device_sample_rate * BlockSize / 1000),
                samplerate=self.input_device_sample_rate,
                device=self.input_device,
            )
            self.stream.start()
            
            device_name = sd.query_devices(device=self.input_device or sd.default.device[0])['name']
            self.on_status_update(f"Live transcription started on device: {device_name}")
            return True
        except Exception as e:
            self.running = False
            self.on_error(f"Failed to start live transcription: {str(e)}")
            return False
    
    def stop(self):
        """Stop live transcription."""
        if not self.running:
            return
        
        self.running = False
        
        if hasattr(self, 'stream') and self.stream:
            self.stream.stop()
            self.stream.close()
        
        self.on_status_update("Live transcription stopped") 