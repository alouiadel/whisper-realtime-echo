"""Service for handling Whisper model transcription in a background thread."""
import threading
from faster_whisper import WhisperModel

class WhisperService:
    """Service for processing audio files with Faster Whisper model."""
    
    def __init__(self, on_status_update, on_result, on_error, on_complete):
        """Initialize service with callback functions.
        
        Args:
            on_status_update: Callback for status updates
            on_result: Callback for successful transcription
            on_error: Callback for error handling
            on_complete: Callback when process completes
        """
        self.on_status_update = on_status_update
        self.on_result = on_result
        self.on_error = on_error
        self.on_complete = on_complete
    
    def transcribe(self, file_path, model_name, device, use_vad=True, vad_parameters=None, language=None, task="transcribe"):
        """Transcribe audio file using specified Whisper model.
        
        Args:
            file_path: Path to audio file
            model_name: Whisper model name to use
            device: Device to run model on (cpu/cuda)
            use_vad: Whether to use VAD filter to remove silence
            vad_parameters: Custom VAD parameters dict (optional)
            language: Language code to use for transcription (optional)
            task: Task to perform (transcribe or translate)
        """
        def _transcribe_thread():
            try:
                self.on_status_update(f"Loading model '{model_name}'...")
                
                compute_type = "float16" if device == "cuda" else "float32"
                device_type = device if device == "cuda" else "cpu"
                
                model = WhisperModel(model_name, device=device_type, compute_type=compute_type)
                
                vad_status = " with VAD filter" if use_vad else ""
                if task == "translate":
                    self.on_status_update(f"Translating audio to English{vad_status}...")
                else:
                    self.on_status_update(f"Transcribing audio{vad_status}...")
                
                lang = None if language == "auto" else language
                
                segments, _ = model.transcribe(
                    file_path,
                    vad_filter=use_vad,
                    vad_parameters=vad_parameters,
                    language=lang,
                    task=task
                )
                
                transcript = " ".join([segment.text for segment in segments])
                
                self.on_result(transcript)
                if task == "translate":
                    self.on_status_update("Translation complete!")
                else:
                    self.on_status_update("Transcription complete!")
                self.on_complete()
            except Exception as e:
                self.on_error(str(e))
                self.on_complete()

        threading.Thread(
            target=_transcribe_thread,
            daemon=True
        ).start() 