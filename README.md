# Document Information Extractor & Form Filler

A powerful Python application that extracts structured information from documents (Word, TXT, PDF) and automatically fills forms using AI-powered extraction or regex patterns.

## 🚀 Features

- **Multi-format Support**: Extract text from Word (.docx), Text (.txt), and PDF (.pdf) files
- **AI-Powered Extraction**: Uses LangChain + Google Gemini for intelligent information extraction
- **Regex Fallback**: Works offline with pattern-based extraction when API key is not available
- **OCR Support**: Extract text from scanned documents and images using Tesseract
- **User-friendly GUI**: Simple graphical interface built with tkinter
- **Data Export**: Save extracted data as TXT, CSV, or JSON
- **Web Automation**: Optional Playwright integration for web form filling
- **Manual Editing**: Edit extracted information before saving

## 📋 Extracted Fields

The application can extract the following information:

- Name
- Email
- Phone Number
- Address
- Date of Birth
- Company
- Job Title
- Dates
- Amounts
- ID Numbers (SSN, Passport, etc.)
- Website URLs
- ZIP/Postal Codes

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Extraction** | PyMuPDF (fitz) | Fast PDF text extraction |
| **Extraction** | python-docx | Word document parsing |
| **Extraction** | pytesseract | OCR for scanned documents |
| **Structuring** | LangChain + Gemini | AI-powered information extraction |
| **Structuring** | Regex Patterns | Offline fallback extraction |
| **GUI** | tkinter | Desktop form interface |
| **Automation** | Playwright | Web form automation (optional) |

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Tesseract OCR (optional, for scanned documents)
  - Windows: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
  - macOS: `brew install tesseract`
  - Linux: `sudo apt-get install tesseract-ocr`

### Setup

1. **Clone or navigate to the project directory**

2. **Install dependencies using uv:**
   ```bash
   uv sync
   ```

   Or install manually:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers (if using web automation):**
   ```bash
   playwright install chromium
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Google Gemini API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```
   
   Get your free API key from: https://makersuite.google.com/app/apikey

## 🎯 Usage

### Running the Application

```bash
# Using uv
uv run python -m document_extractor

# Or directly
python -m document_extractor
```

### GUI Workflow

1. **Select Document**: Click "Select Document" and choose a Word, TXT, or PDF file
2. **Configure Options**:
   - Enable "Use OCR" for scanned documents
   - Enable "Use AI Extraction" for better accuracy (requires API key)
3. **Extract**: Click "Extract & Fill" to extract information and populate the form
4. **Review & Edit**: Review the extracted data and make any necessary edits
5. **Save/Export**: Use the export buttons to save data as TXT, CSV, or JSON

### Command Line Usage

```python
from document_extractor.parser import DocumentParser
from document_extractor.extractor import AIExtractor
from document_extractor.extractor_regex import RegexExtractor

# Parse document
parser = DocumentParser("document.pdf", use_ocr=False)
text, metadata = parser.extract_text()

# Extract information (AI mode)
extractor = AIExtractor(api_key="your_key")
data = extractor.extract_all(text)

# Or use regex fallback
regex_extractor = RegexExtractor(text)
data = regex_extractor.extract_all()
```

### Web Form Automation

```python
from document_extractor.web_automation import WebFormAutomator

# Fill form using selectors
with WebFormAutomator(headless=False) as automator:
    field_mapping = {
        "name": "#name-input",
        "email": "input[name='email']",
    }
    automator.fill_form_by_selectors(
        url="https://example.com/form",
        field_mapping=field_mapping,
        submit_button_selector="#submit-btn"
    )
```

## 📁 Project Structure

```
document-extractor/
├── pyproject.toml              # Project configuration
├── README.md                   # This file
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── src/
│   └── document_extractor/
│       ├── __init__.py
│       ├── main.py            # Application entry point
│       ├── parser.py          # Document parsing (PyMuPDF, python-docx, pytesseract)
│       ├── extractor.py       # AI extraction (LangChain + Gemini)
│       ├── extractor_regex.py # Regex fallback extraction
│       ├── form.py            # tkinter GUI
│       └── web_automation.py  # Playwright automation
└── tests/                      # Unit tests
```

## ⚙️ Configuration

### Environment Variables

- `GOOGLE_API_KEY`: Google Gemini API key for AI extraction (optional)
- `TESSERACT_CMD`: Path to Tesseract executable (if not in PATH)

### Extraction Modes

1. **AI Mode** (Recommended): Uses LangChain + Gemini for accurate extraction
   - Requires API key
   - Better accuracy for unstructured documents
   - Handles context and variations

2. **Regex Mode** (Fallback): Uses pattern matching
   - Works offline
   - No API key needed
   - Good for structured documents

## 🔧 Dependencies

- `pymupdf>=1.23.0` - PDF extraction
- `python-docx>=1.1.0` - Word document parsing
- `pytesseract>=0.3.10` - OCR support
- `langchain>=0.1.0` - LLM framework
- `langchain-google-genai>=1.0.0` - Gemini integration
- `playwright>=1.40.0` - Web automation
- `python-dotenv>=1.0.0` - Environment variables
- `pillow>=10.0.0` - Image processing

## 📝 Notes

- **AI Extraction**: Requires internet connection and API key. Free tier available with generous limits.
- **OCR**: Only needed for scanned documents. Install Tesseract separately.
- **Performance**: PyMuPDF is faster than pdfplumber for PDF extraction.
- **Accuracy**: AI extraction provides better results for unstructured documents.

## 🐛 Troubleshooting

### "GOOGLE_API_KEY not found"
- Set the API key in `.env` file or as environment variable
- The app will automatically fall back to regex extraction

### OCR not working
- Ensure Tesseract is installed and in PATH
- Or set `TESSERACT_CMD` in `.env` file

### Playwright errors
- Run `playwright install chromium` to install browsers
- Ensure you're using the correct selectors for form fields

## 📄 License

This project is open source and available for personal and commercial use.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue on the project repository.

