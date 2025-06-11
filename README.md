# AI Text Summarizer

A simple yet powerful desktop app for summarizing large blocks of text using AI. Built with Python and Tkinter, the tool combines multiple NLP features like summarization, sentiment analysis, named entity recognition, keyword extraction, and text-to-speech, all in a clean graphical interface.

## Overview

Reading and digesting long documents can be tedious. This application helps by automatically summarizing text while also giving insights like the overall sentiment, key entities, and readability level. It’s especially useful for students, professionals, and researchers who work with large amounts of content.

## Features

- Summarize text using a transformer model (`facebook/bart-large-cnn`)
- Sentiment analysis: get a quick feel for the tone
- Named Entity Recognition (NER): identify people, places, etc.
- Keyword extraction using YAKE
- Flesch reading ease and grade-level readability scores
- Built-in text-to-speech playback
- Save summaries as .txt or .pdf
- Load external .txt files for input
- Copy summary to clipboard
- Real-time word, character, and reading time stats

## Tech Stack

- Python 3.8+
- Tkinter for GUI
- Hugging Face Transformers (`pipeline`)
- PyTorch backend
- `fpdf` for PDF export
- `pyttsx3` for offline text-to-speech
- `textstat` for readability metrics
- `yake` for keyword extraction

## Installation

Install dependencies with pip:

```bash
pip install transformers torch fpdf pyttsx3 textstat yake
```

Make sure PyTorch is installed with the appropriate version for your system.

## How to Use

1. Run the script:

```bash
python ai_text_summarizer.py
```

2. Paste or load your text.
3. Set minimum and maximum summary length.
4. Click “Summarize” and explore additional features.

## System Requirements

- Windows/Linux/macOS
- 4GB RAM minimum (8GB recommended)
- Internet connection (for downloading transformer models on first use)

## Future Improvements

- Add voice input (speech-to-text)
- Support other languages and translation
- Fine-tune models for specialized domains (e.g., medical, legal)
- Cloud save and web-based version
