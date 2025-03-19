"""Main application logic for Whisper Transcription App."""
import flet as ft
from ui.theme import AppTheme
from ui.app_ui import configure_page, create_header
from ui.model_selection import ModelSelector
from ui.transcription_ui import (
    create_file_section, 
    create_result_section, 
    create_controls_section, 
    create_model_section
)
from logic.whisper_service import WhisperService

def WhisperApp(page: ft.Page):
    """Main application initialization and UI setup."""
    configure_page(page)
    
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    
    header = create_header()
    
    def on_model_change():
        update_ui_state()
    
    model_selector = ModelSelector(page, on_model_change)
    
    file_section, selected_file_path, _ = create_file_section(
        file_picker, 
        lambda: update_ui_state()
    )
    
    model_section, vram_card, speed_card = create_model_section(model_selector)
    
    results_section, result_text = create_result_section()
    
    controls_section, transcribe_button, progress_ring, status_text = create_controls_section()
    
    def on_status_update(status):
        """Update status text and color based on transcription process."""
        status_text.value = status
        if status == "Transcribing audio..." or status.startswith("Loading model"):
            status_text.color = AppTheme.WARNING_COLOR
        elif status == "Transcription complete!":
            status_text.color = AppTheme.SUCCESS_COLOR
        page.update()
    
    def on_result(text):
        """Display transcription result in text field."""
        result_text.value = text
        page.update()
    
    def on_error(error):
        """Handle and display errors."""
        result_text.value = f"Error: {error}"
        status_text.value = "Error occurred"
        status_text.color = AppTheme.ERROR_COLOR
        page.update()
    
    def on_complete():
        """Clean up UI after transcription is complete."""
        progress_ring.visible = False
        page.update()
    
    whisper_service = WhisperService(
        on_status_update=on_status_update,
        on_result=on_result,
        on_error=on_error,
        on_complete=on_complete
    )
    
    def update_ui_state():
        """Update UI elements based on current model and file selection."""
        is_valid_model = model_selector.is_valid_model()
        has_file = bool(selected_file_path.value)
        
        transcribe_button.disabled = not is_valid_model or not has_file
        
        if not is_valid_model:
            transcribe_button.style.bgcolor = {"": "#6200EE80"}
            transcribe_button.tooltip = "This model is not available in English-only mode"
        elif not has_file:
            transcribe_button.style.bgcolor = {"": AppTheme.DISABLED_COLOR}
            transcribe_button.tooltip = "Please select an audio file first"
        else:
            transcribe_button.style.bgcolor = {"": AppTheme.PRIMARY_COLOR}
            transcribe_button.tooltip = None
        
        if not is_valid_model:
            status_text.value = "Note: Large and Turbo models are only available in multilingual versions"
            status_text.color = AppTheme.WARNING_COLOR
        else:
            status_text.value = "Ready"
            status_text.color = AppTheme.SUCCESS_COLOR
        
        vram_card.content.content.controls[1].value = model_selector.get_memory_info()
        speed_card.content.content.controls[1].value = model_selector.get_speed_info()
        page.update()
    
    def start_transcription(e):
        """Start transcription process with selected model and file."""
        if not selected_file_path.value:
            status_text.value = "Please select an audio file first"
            status_text.color = AppTheme.ERROR_COLOR
            page.update()
            return
        
        model_name = model_selector.get_model_name()
        
        if model_name is None:
            status_text.value = "Invalid model selection"
            status_text.color = AppTheme.ERROR_COLOR
            page.update()
            return
        
        result_text.value = ""
        progress_ring.visible = True
        page.update()
        
        whisper_service.transcribe(
            file_path=selected_file_path.value,
            model_name=model_name,
            device=model_selector.device_dropdown.value
        )
    
    transcribe_button.on_click = start_transcription
    
    page.add(
        header,
        file_section,
        model_section,
        controls_section,
        results_section,
    )
    
    update_ui_state() 