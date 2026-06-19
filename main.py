"""Whisper Transcription App entry point."""

import flet as ft
from logic.app import WhisperApp

if __name__ == "__main__":
    ft.app(target=WhisperApp)
