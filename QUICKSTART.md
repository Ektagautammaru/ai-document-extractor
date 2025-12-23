# Quick Start Guide

## Installation Steps

1. **Install dependencies:**
   ```bash
   uv sync
   ```
   Or with pip:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up API key (optional but recommended):**
   - Copy `.env.example` to `.env`
   - Get your free Google Gemini API key from: https://makersuite.google.com/app/apikey
   - Add it to `.env`:
     ```
     GOOGLE_API_KEY=your_api_key_here
     ```

3. **Install Playwright browsers (optional, for web automation):**
   ```bash
   playwright install chromium
   ```

4. **Run the application:**
   ```bash
   python run.py
   ```
   Or:
   ```bash
   python -m src.document_extractor
   ```

## First Use

1. Click "Select Document" and choose a Word, PDF, or TXT file
2. Enable "Use AI Extraction" if you have an API key (recommended)
3. Enable "Use OCR" if your document is scanned
4. Click "Extract & Fill"
5. Review and edit the extracted information
6. Save or export your data

## Troubleshooting

- **No API key?** The app will automatically use regex extraction (works offline)
- **OCR not working?** Install Tesseract OCR separately
- **Import errors?** Make sure all dependencies are installed with `uv sync`

