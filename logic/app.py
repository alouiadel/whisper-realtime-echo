"""Main application logic for Whisper Transcription App."""
import flet as ft
from ui.theme_lang import AppThemeLang
from ui.app_ui import configure_page, create_header
from ui.model_selection import ModelSelector
from ui.transcription_ui import (
    create_file_section, 
    create_result_section, 
    create_controls_section, 
    create_model_section
)
from ui.clipboard_history_ui import create_history_dialog
from logic.whisper_service import WhisperService
from logic.audio_recorder import AudioRecorder
from logic.clipboard_history import ClipboardHistory
from logic.live_transcription import LiveTranscription
import threading

def WhisperApp(page: ft.Page):
    """Main application initialization and UI setup."""
    configure_page(page)
    
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    
    header = create_header()
    
    clipboard_history = ClipboardHistory()
    
    def on_model_change():
        update_ui_state()
    
    model_selector = ModelSelector(page, on_model_change)
    
    def on_recorder_status(status):
        """Handle recorder status updates."""
        if "error" in status.lower() or "failed" in status.lower():
            status_text.value = status
            status_text.color = AppThemeLang.ERROR_COLOR
            page.update()
        elif "saved" in status:
            status_text.value = "Recording saved"
            status_text.color = AppThemeLang.SUCCESS_COLOR
            page.update()
    
    audio_recorder = AudioRecorder(on_status_update=on_recorder_status)
    
    def start_recording(_):
        """Handle start recording button click."""
        record_button.visible = False
        stop_button.visible = True
        selected_file_path.value = ""
        selected_file_name.value = "Recording..."
        transcribe_button.disabled = True
        audio_recorder.start_recording()
        page.update()
    
    def stop_recording(_):
        """Handle stop recording button click."""
        record_button.visible = True
        stop_button.visible = False
        file_path = audio_recorder.stop_recording()
        if file_path:
            selected_file_path.value = file_path
            selected_file_name.value = "Recorded Audio"
            update_ui_state()
        else:
            selected_file_name.value = "No file selected"
        page.update()
    
    file_section, selected_file_path, selected_file_name, record_button, stop_button = create_file_section(
        file_picker, 
        lambda: update_ui_state(),
        start_recording,
        stop_recording
    )
    
    model_section, vram_card, speed_card = create_model_section(model_selector)
    
    results_section, result_text, copy_button, history_button = create_result_section()
    
    controls_section, transcribe_button, progress_ring, status_text, vad_checkbox, translate_checkbox, live_button = create_controls_section()
    
    live_transcription = None
    is_live_active = False
    live_accumulated_text = ""
    
    def on_live_transcription(text):
        """Handle live transcription result."""
        nonlocal live_accumulated_text
        current_text = result_text.value if result_text.value else ""
        result_text.value = current_text + (" " if current_text else "") + text
        copy_button.visible = True
        
        live_accumulated_text += (" " if live_accumulated_text else "") + text
            
        page.update()
    
    def on_live_status(status):
        """Handle live transcription status updates."""
        status_text.value = status
        if "error" in status.lower() or "failed" in status.lower():
            status_text.color = AppThemeLang.ERROR_COLOR
            live_button.text = "Start Live"
            live_button.icon = ft.icons.MIC_NONE
        elif "started" in status.lower():
            status_text.color = AppThemeLang.SUCCESS_COLOR
        elif "stopped" in status.lower():
            status_text.color = AppThemeLang.SUCCESS_COLOR
            live_button.text = "Start Live"
            live_button.icon = ft.icons.MIC_NONE
        else:
            status_text.color = AppThemeLang.WARNING_COLOR
        page.update()
    
    def on_live_error(error):
        """Handle live transcription errors."""
        status_text.value = f"Error: {error}"
        status_text.color = AppThemeLang.ERROR_COLOR
        live_button.text = "Start Live"
        live_button.icon = ft.icons.MIC_NONE
        page.update()
    
    def toggle_live_transcription(_):
        """Toggle live transcription on/off."""
        nonlocal live_transcription, is_live_active, live_accumulated_text
        
        if not LiveTranscription.is_available():
            status_text.value = "Error: sounddevice library not available"
            status_text.color = AppThemeLang.ERROR_COLOR
            page.update()
            return
        
        model_name = model_selector.get_model_name()
        
        if model_name is None:
            status_text.value = "Invalid model selection"
            status_text.color = AppThemeLang.ERROR_COLOR
            page.update()
            return
        
        if is_live_active:
            if live_transcription:
                live_transcription.stop()
            is_live_active = False
            transcribe_button.disabled = False
            record_button.disabled = False
            progress_ring.visible = False
            
            if live_accumulated_text.strip():
                model_name = model_selector.get_model_name() or ""
                clipboard_history.add_item(live_accumulated_text, model_name)
                live_accumulated_text = ""
        else:
            result_text.value = ""
            live_accumulated_text = ""
            copy_button.visible = False
            progress_ring.visible = True
            
            task = "translate" if translate_checkbox.value else "transcribe"
            language = None if model_selector.language_dropdown.value == "auto" else model_selector.language_dropdown.value
            
            compute_type = "int8"
            
            live_transcription = LiveTranscription(
                on_transcription=on_live_transcription,
                on_status_update=on_live_status,
                on_error=on_live_error,
                model_path=model_name,
                device=model_selector.device_dropdown.value,
                language=language,
                task=task,
                compute_type=compute_type,
                vad_filter=vad_checkbox.value,
            )
            
            success = live_transcription.start()
            
            if success:
                is_live_active = True
                live_button.text = "Stop Live"
                live_button.icon = ft.icons.MIC_OFF
                transcribe_button.disabled = True
                record_button.disabled = True
            else:
                progress_ring.visible = False
            
        page.update()
    
    live_button.on_click = toggle_live_transcription
    
    def translate_checkbox_changed(_):
        if translate_checkbox.value:
            model_selector.language_dropdown.value = "auto"
            model_selector.language_dropdown.disabled = True
        else:
            if model_selector.model_type.value == "multilingual":
                model_selector.language_dropdown.disabled = False
        page.update()
    
    translate_checkbox.on_change = translate_checkbox_changed
    
    def on_history_item_copy(text):
        """Handle when history item is copied."""
        result_text.value = text
        copy_button.visible = True
        status_text.value = "Copied from history!"
        status_text.color = AppThemeLang.SUCCESS_COLOR
        page.update()
        threading.Timer(2.0, reset_status).start()
    
    history_dialog, open_history_dialog = create_history_dialog(
        page, 
        clipboard_history, 
        on_history_item_copy
    )
    
    page.overlay.append(history_dialog)
    
    history_button.on_click = lambda _: open_history_dialog()
    
    def on_status_update(status):
        """Update status text and color based on transcription process."""
        status_text.value = status
        if status == "Transcribing audio..." or status.startswith("Loading model"):
            status_text.color = AppThemeLang.WARNING_COLOR
        elif status == "Transcription complete!":
            status_text.color = AppThemeLang.SUCCESS_COLOR
        page.update()
    
    def on_result(text):
        """Display transcription result in text field."""
        result_text.value = text
        copy_button.visible = bool(text)
        
        if text.strip():
            model_name = model_selector.get_model_name() or ""
            clipboard_history.add_item(text, model_name)
            
        page.update()
    
    def on_error(error):
        """Handle and display errors."""
        result_text.value = f"Error: {error}"
        status_text.value = "Error occurred"
        status_text.color = AppThemeLang.ERROR_COLOR
        page.update()
    
    def on_complete():
        """Clean up UI after transcription is complete."""
        progress_ring.visible = False
        page.update()
    
    def copy_to_clipboard(_):
        """Copy transcription text to clipboard."""
        text = result_text.value
        page.set_clipboard(text)
        status_text.value = "Copied to clipboard!"
        status_text.color = AppThemeLang.SUCCESS_COLOR
        page.update()
        
        if text.strip():
            model_name = model_selector.get_model_name() or ""
            clipboard_history.add_item(text, model_name)
        
        threading.Timer(2.0, reset_status).start()
        
    def reset_status():
        """Reset status text to ready state."""
        status_text.value = "Ready"
        status_text.color = AppThemeLang.SUCCESS_COLOR
        page.update()
    
    copy_button.on_click = copy_to_clipboard
    
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
        
        transcribe_button.disabled = not is_valid_model or not has_file or is_live_active
        
        if not is_valid_model:
            transcribe_button.style.bgcolor = {"": AppThemeLang.PRIMARY_COLOR_TRANSLUCENT}
            transcribe_button.tooltip = "This model is not available in English-only mode"
        elif not has_file:
            transcribe_button.style.bgcolor = {"": AppThemeLang.DISABLED_COLOR}
            transcribe_button.tooltip = "Please select an audio file first"
        else:
            transcribe_button.style.bgcolor = {"": AppThemeLang.PRIMARY_COLOR}
            transcribe_button.tooltip = None
        
        if not is_valid_model:
            status_text.value = "Note: Large and Turbo models are only available in multilingual versions"
            status_text.color = AppThemeLang.WARNING_COLOR
        else:
            status_text.value = "Ready"
            status_text.color = AppThemeLang.SUCCESS_COLOR
        
        translate_checkbox.visible = model_selector.model_type.value == "multilingual"
        if model_selector.model_type.value == "english_only":
            translate_checkbox.value = False
            
        vram_card.content.content.controls[1].value = model_selector.get_memory_info()
        speed_card.content.content.controls[1].value = model_selector.get_speed_info()
        page.update()
    
    def start_transcription(_):
        """Start transcription process with selected model and file."""
        if not selected_file_path.value:
            status_text.value = "Please select an audio file first"
            status_text.color = AppThemeLang.ERROR_COLOR
            page.update()
            return
        
        model_name = model_selector.get_model_name()
        
        if model_name is None:
            status_text.value = "Invalid model selection"
            status_text.color = AppThemeLang.ERROR_COLOR
            page.update()
            return
        
        result_text.value = ""
        copy_button.visible = False
        progress_ring.visible = True
        page.update()
        
        task = "translate" if translate_checkbox.value else "transcribe"
        
        whisper_service.transcribe(
            file_path=selected_file_path.value,
            model_name=model_name,
            device=model_selector.device_dropdown.value,
            use_vad=vad_checkbox.value,
            language=model_selector.language_dropdown.value,
            task=task
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