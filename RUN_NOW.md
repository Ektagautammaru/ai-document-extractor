# How to Run the Project Now

## 🚀 Quick Start

### Step 1: Run the Application

Open your terminal/PowerShell in the project directory and run:

```bash
uv run python run.py
```

**OR** if you prefer:

```bash
uv run python -m src.document_extractor
```

## 📋 Step-by-Step Instructions

1. **Open Terminal/PowerShell**
   - Navigate to: `H:\Python Project`

2. **Run the command:**
   ```bash
   uv run python run.py
   ```

3. **Wait for GUI to open**
   - A window titled "Document Information Extractor" should appear

4. **Test the fixes:**
   - Click "Select Document"
   - Choose `sample_invoice.txt` (or any sample file)
   - Click "Extract & Fill"
   - Review the results - they should be more accurate now!

## ✅ What You Should See

When you run the application:
- GUI window opens
- Console shows: "Note: GOOGLE_API_KEY not found..." (if no API key)
- Application works with regex extraction (offline mode)

## 🧪 Testing the Fixes

Try extracting from `sample_invoice.txt` - you should see:
- ✅ Name: "Robert James Williams" (not concatenated)
- ✅ Email: "robert.williams@customer.com" 
- ✅ Date: "12/01/2024"
- ✅ Date of Birth: Empty (correct!)
- ✅ Job Title: Empty (correct!)

## 💡 Tips

- **If the window doesn't open:** Check the terminal for error messages
- **To stop the application:** Close the GUI window or press Ctrl+C in terminal
- **To use AI extraction:** Set up API key in `.env` file (optional)

## 🔄 Restarting

If you make changes to the code:
1. Close the application
2. Run the command again: `uv run python run.py`

---

**Ready to go!** Just run: `uv run python run.py`

