"""Manages clipboard history for transcriptions."""
import os
import json
import datetime
from typing import List, Dict, Any

class ClipboardHistory:
    """Manages a history of clipboard content with persistence."""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize clipboard history manager.
        
        Args:
            data_dir: Directory where history will be stored
        """
        self.data_dir = data_dir
        self.history_file = os.path.join(data_dir, "clipboard_history.json")
        self.history: List[Dict[str, Any]] = []
        self._load_history()
    
    def _load_history(self):
        """Load history from disk."""
        os.makedirs(self.data_dir, exist_ok=True)
        
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except Exception as e:
                print(f"Error loading clipboard history: {e}")
                self.history = []
    
    def _save_history(self):
        """Save history to disk."""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving clipboard history: {e}")
    
    def add_item(self, text: str, model_name: str = "") -> None:
        """Add a new item to clipboard history.
        
        Args:
            text: The transcription text
            model_name: The model used for transcription
        """
        if not text.strip():
            return
            
        timestamp = datetime.datetime.now().isoformat()
        
        history_item = {
            "text": text,
            "model_name": model_name,
            "timestamp": timestamp,
        }
        
        self.history.append(history_item)
        
        if len(self.history) > 50:
            self.history = self.history[-50:]
        
        self._save_history()
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get clipboard history items.
        
        Returns:
            List of history items, most recent first
        """
        return list(reversed(self.history))
    
    def clear_history(self) -> None:
        """Clear all history items."""
        self.history = []
        self._save_history() 