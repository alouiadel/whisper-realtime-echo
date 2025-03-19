# 🎙️ Realtime Whisper Flet

A modern GUI for Faster Whisper speech recognition model using Flet framework.

> ⚠️ This application has been tested and confirmed working on Windows. While it may work on other platforms (Linux, macOS), they have not been officially tested.

## ✨ Features

- 🔊 Transcribe audio files with a beautiful UI
- 🎤 Record audio directly and transcribe it
- 🌍 Choose between English-only and multilingual models
- 🗣️ Select language for multilingual models (auto-detect available)
- 🌐 Translate any language to English text
- 📏 Select model size with VRAM/speed indicators
- 💻 GPU (CUDA) or CPU processing
- 📊 Real-time transcription status
- 🧩 Modular, maintainable codebase
- 📋 Copy transcription results to clipboard
- 📜 Access clipboard history of previous transcriptions
- 🌓 Toggle between light and dark themes

## 📋 Model Information

| Size | Parameters | English-only | Multilingual | VRAM | Speed |
|------|------------|--------------|--------------|------|-------|
| tiny | 39 M | ✅ tiny.en | ✅ tiny | ~1 GB | ~10x |
| base | 74 M | ✅ base.en | ✅ base | ~1 GB | ~7x |
| small | 244 M | ✅ small.en | ✅ small | ~2 GB | ~4x |
| medium | 769 M | ✅ medium.en | ✅ medium | ~5 GB | ~2x |
| large | 1550 M | ❌ N/A | ✅ large | ~10 GB | 1x |
| turbo | 809 M | ❌ N/A | ✅ turbo | ~6 GB | ~8x |

> 💡 English-only models typically perform better for English transcription.

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/alouiadel/realtime-whisper-flet.git
cd realtime-whisper-flet

# Install dependencies
pip install -r requirements.txt
```

> 🔥 **For GPU acceleration:** If you want to use CUDA for GPU acceleration, install the appropriate PyTorch version from [PyTorch official installation guide](https://pytorch.org/get-started/locally/)

### Usage

```bash
# Run the application
python main.py
```

1. 📂 Click "Select Audio File" or 🎤 "Start Recording"
2. 🌐 Choose model type (English-only/Multilingual)
3. 📊 Select model size and device
4. ▶️ Click "Transcribe"
5. 📝 View results in real-time
6. 📋 Copy results to clipboard with one click
7. 📜 Access previous transcriptions via the history button
8. 🌓 Toggle between light and dark themes using the button in the top-right corner

## 📝 Notes & Limitations

- **Language Selection**: The language dropdown helps Whisper optimize recognition for specific languages but does not translate content. English audio will still be transcribed as English even when another language is selected.

- **Transcribe vs. Translate**: Whisper supports two modes:
  - **Transcribe**: Converts speech to text in the original language (default)
  - **Translate**: Converts speech from any language to English text (enable with "Translate to English" checkbox)

- **Translation Mode**: When "Translate to English" is selected, the language is automatically set to "Auto-detect" as this provides the best results for translation. Whisper requires language auto-detection for optimal translation to English.

- **Translation Limitations**: Translation may not work reliably for all language combinations. For best translation results, use larger models (large or turbo) and ensure the audio quality is clear. Some languages or accents might require using transcribe mode first, then a separate translation service.

- **System Requirements**: If the app crashes unexpectedly, it may be due to insufficient RAM or VRAM for the selected model size. Try using a smaller model or ensuring your system meets the memory requirements listed in the model table.

## 🎧 Supported Audio Formats

Whisper leverages ffmpeg to process audio, supporting a wide range of formats:
- Audio files: wav, mp3, m4a, ogg, flac, opus, amr
- Video files: mp4 (and other video formats with audio tracks)

## 🧰 Requirements

- Python 3.9-3.11
- Flet
- Faster Whisper (version 1.1.1)
- SoundDevice, SoundFile (for audio recording)
- CUDA-compatible GPU (optional, for faster processing)

## 🙏 Credits

This project is powered by [Faster Whisper](https://github.com/SYSTRAN/faster-whisper), a highly optimized implementation of OpenAI's Whisper. The Whisper model was trained on a large dataset of diverse audio and is capable of multilingual speech recognition, translation, and language identification.

## 📜 Clipboard History

- View, copy, and reuse previous transcriptions
- Transcription history is saved between sessions
- Each entry includes timestamp and model information
- Most recent 50 entries are retained 