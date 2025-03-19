# 🎙️ Realtime Whisper Flet

A modern GUI for OpenAI's Whisper speech recognition model using Flet framework.

## ✨ Features

- 🔊 Transcribe audio files with a beautiful UI
- 🎤 Record audio directly and transcribe it
- 🌍 Choose between English-only and multilingual models
- 📏 Select model size with VRAM/speed indicators
- 💻 GPU (CUDA) or CPU processing
- 📊 Real-time transcription status
- 🧩 Modular, maintainable codebase
- 📋 Copy transcription results to clipboard

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

## 🎧 Supported Audio Formats

Whisper leverages ffmpeg to process audio, supporting a wide range of formats:
- Audio files: wav, mp3, m4a, ogg, flac, opus, amr
- Video files: mp4 (and other video formats with audio tracks)

## 🧰 Requirements

- Python 3.9-3.11
- Flet
- OpenAI Whisper
- SoundDevice, SoundFile (for audio recording)
- CUDA-compatible GPU (optional, for faster processing)

## 🙏 Credits

This project is powered by [OpenAI's Whisper](https://github.com/openai/whisper), a state-of-the-art automatic speech recognition system. The Whisper model was trained on a large dataset of diverse audio and is capable of multilingual speech recognition, translation, and language identification. 