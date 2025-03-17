import whisper
import threading

class WhisperService:
    def __init__(self, on_status_update, on_result, on_error, on_complete):
        self.on_status_update = on_status_update
        self.on_result = on_result
        self.on_error = on_error
        self.on_complete = on_complete
    
    def transcribe(self, file_path, model_name, device):
        def _transcribe_thread():
            try:
                self.on_status_update(f"Loading model '{model_name}'...")
                
                model = whisper.load_model(model_name, device=device)
                
                self.on_status_update("Transcribing audio...")
                
                result = model.transcribe(file_path)
                
                self.on_result(result["text"])
                self.on_status_update("Transcription complete!")
                self.on_complete()
            except Exception as e:
                self.on_error(str(e))
                self.on_complete()

        threading.Thread(
            target=_transcribe_thread,
            daemon=True
        ).start() 