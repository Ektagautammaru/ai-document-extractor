# Sample Documents for Testing

I've created several sample document files that you can use to test the Document Extractor application:

## 📄 Available Sample Files

### 1. `sample_document.txt`
A comprehensive personal information form containing:
- Name, Email, Phone
- Date of Birth
- Address and ZIP Code
- Company and Job Title
- Website
- Amounts and ID Numbers
- Dates

### 2. `sample_resume.txt`
A professional resume/CV format with:
- Contact information
- Employment history
- Education details
- Company and position information
- Financial expectations

### 3. `sample_invoice.txt`
An invoice/billing document with:
- Customer information
- Company details
- Dates and amounts
- Payment information
- Contact details

### 4. `sample_application.txt`
A job application form containing:
- Applicant personal information
- Identification numbers
- Current employment details
- Application dates
- Salary expectations

## 🧪 How to Test

1. **Run the application:**
   ```bash
   uv run python run.py
   ```

2. **Select a sample file:**
   - Click "Select Document"
   - Navigate to the project folder
   - Choose any of the sample files (e.g., `sample_document.txt`)

3. **Extract information:**
   - Click "Extract & Fill"
   - Review the extracted data in the form fields
   - Edit if needed

4. **Save/Export:**
   - Use "Save as TXT", "Export CSV", or "Export JSON" buttons

## 📝 What Gets Extracted

Each sample file contains different types of information to test various extraction patterns:

- ✅ Names (various formats)
- ✅ Email addresses
- ✅ Phone numbers (multiple formats)
- ✅ Addresses
- ✅ Dates (various formats)
- ✅ Companies
- ✅ Job titles
- ✅ Amounts/Money
- ✅ ID numbers (SSN, Passport, etc.)
- ✅ Websites
- ✅ ZIP codes

## 💡 Tips

- Try different sample files to see how extraction works with different document structures
- Test with "Use AI Extraction" enabled (if you have an API key) vs regex mode
- Compare extraction accuracy between AI and regex modes
- Test the OCR feature with scanned documents (if you have any)

## 📍 File Location

All sample files are located in the project root directory:
```
H:\Python Project\
├── sample_document.txt
├── sample_resume.txt
├── sample_invoice.txt
└── sample_application.txt
```

Happy testing! 🚀

