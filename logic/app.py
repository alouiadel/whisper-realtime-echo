import flet as ft
import os
from ui.theme import AppTheme
from ui.components import create_info_card, create_section_title, create_section_container
from ui.model_selection import ModelSelector
from logic.whisper_service import WhisperService

def WhisperApp(page: ft.Page):
    page.title = "Whisper Transcription App"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 30
    page.window.center()
    page.window_width = 800
    page.window_height = 700
    page.bgcolor = AppTheme.BACKGROUND_COLOR
    
    status_text = ft.Text("Ready", color=AppTheme.SUCCESS_COLOR)
    
    progress_ring = ft.ProgressRing(visible=False, color=AppTheme.SECONDARY_COLOR)
    
    selected_file_path = ft.Text("")
    selected_file_name = ft.Text("No file selected", size=16)
    
    def file_picker_result(e: ft.FilePickerResultEvent):
        if e.files:
            selected_file_path.value = e.files[0].path
            selected_file_name.value = os.path.basename(e.files[0].path)
            update_ui_state()
            page.update()
    
    file_picker = ft.FilePicker(on_result=file_picker_result)
    page.overlay.append(file_picker)
    
    result_text = ft.TextField(
        multiline=True,
        min_lines=10,
        max_lines=20,
        read_only=True,
        border_color=ft.Colors.GREY_700,
        focused_border_color=AppTheme.SECONDARY_COLOR,
        text_size=16,
        expand=True,
    )
    
    transcribe_button = ft.ElevatedButton(
        "Transcribe",
        icon=ft.Icons.PLAY_ARROW,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=AppTheme.PRIMARY_COLOR,
            padding=15,
        ),
        height=50,
    )
    
    vram_card = create_info_card("Required VRAM", "~1 GB", ft.Icons.MEMORY)
    speed_card = create_info_card("Relative Speed", "~7x", ft.Icons.SPEED)
    
    def on_model_change():
        update_ui_state()
    
    model_selector = ModelSelector(page, on_model_change)
    
    def on_status_update(status):
        status_text.value = status
        if status == "Transcribing audio..." or status.startswith("Loading model"):
            status_text.color = AppTheme.WARNING_COLOR
        elif status == "Transcription complete!":
            status_text.color = AppTheme.SUCCESS_COLOR
        page.update()
    
    def on_result(text):
        result_text.value = text
        page.update()
    
    def on_error(error):
        result_text.value = f"Error: {error}"
        status_text.value = "Error occurred"
        status_text.color = AppTheme.ERROR_COLOR
        page.update()
    
    def on_complete():
        progress_ring.visible = False
        page.update()
    
    whisper_service = WhisperService(
        on_status_update=on_status_update,
        on_result=on_result,
        on_error=on_error,
        on_complete=on_complete
    )
    
    def update_ui_state():
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
    
    header = ft.Container(
        content=ft.Text(
            "Whisper Transcription App",
            size=30,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE,
        ),
        margin=ft.margin.only(bottom=20),
    )
    
    file_section = create_section_container(
        ft.Row([
            ft.ElevatedButton(
                "Select Audio File",
                icon=ft.Icons.UPLOAD_FILE,
                on_click=lambda _: file_picker.pick_files(
                    allow_multiple=False,
                    allowed_extensions=["wav", "mp3", "m4a", "ogg"]
                ),
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=AppTheme.PRIMARY_COLOR,
                ),
            ),
            selected_file_name,
        ])
    )
    
    model_section = create_section_container(
        ft.Column([
            create_section_title("Model Settings"),
            ft.Row([
                model_selector.model_type,
                model_selector.model_size,
                model_selector.device_dropdown,
            ]),
            ft.Row([
                vram_card,
                speed_card,
            ]),
        ])
    )
    
    controls_section = create_section_container(
        ft.Row([
            transcribe_button,
            progress_ring,
            status_text,
        ])
    )
    
    results_section = ft.Container(
        content=ft.Column([
            create_section_title("Transcription Result"),
            result_text,
        ]),
        expand=True,
    )
    
    page.add(
        header,
        file_section,
        model_section,
        controls_section,
        results_section,
    )
    
    update_ui_state() 