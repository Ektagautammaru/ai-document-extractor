# How to Run the Document Extractor Project

## ✅ Setup Complete!

All dependencies have been installed. You're ready to run the application!

## 🚀 Running the Application

### Option 1: Using the run script (Easiest)
```bash
uv run python run.py
```

### Option 2: Using Python module
```bash
uv run python -m src.document_extractor
```

### Option 3: Direct Python (if virtual environment is activated)
```bash
python run.py
```

## 📝 Optional: Set Up API Key (Recommended)

For better extraction accuracy with AI, set up your Google Gemini API key:

1. **Get a free API key:**
   - Visit: https://makersuite.google.com/app/apikey
   - Sign in with your Google account
   - Create a new API key

2. **Create `.env` file:**
   - Copy `.env.example` to `.env`
   - Or create a new `.env` file in the project root
   - Add your API key:
     ```
     GOOGLE_API_KEY=your_actual_api_key_here
     ```

**Note:** The app works without an API key too! It will automatically use regex-based extraction (works offline).

## 🎯 Using the Application

1. **Launch the app** using one of the commands above
2. **Click "Select Document"** and choose a Word (.docx), PDF (.pdf), or Text (.txt) file
3. **Configure options:**
   - ✅ Check "Use AI Extraction" if you have an API key (better accuracy)
   - ✅ Check "Use OCR" if your document is scanned
4. **Click "Extract & Fill"** to extract information
5. **Review and edit** the extracted data
6. **Save or Export** your data (TXT, CSV, or JSON)

## 🔧 Troubleshooting

- **No API key?** The app will automatically use regex extraction (works offline)
- **Import errors?** Make sure you're using `uv run` or have activated the virtual environment
- **GUI not opening?** Check if tkinter is available (usually comes with Python)

## 📦 What's Installed

✅ All Python dependencies  
✅ Playwright browsers (for web automation)  
✅ Ready to use!

---

**Quick Start Command:**
```bash
uv run python run.py
```

