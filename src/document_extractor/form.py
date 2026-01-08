"""
Form Filler Module
Creates and manages a GUI form for displaying and editing extracted information
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, Optional
import json
import csv
import os
import re


class FormFiller:
    """GUI form for displaying and editing extracted information"""
    
    def __init__(self, use_ai: bool = True):
        """
        Initialize the form window
        
        Args:
            use_ai: Whether to use AI extraction (default: True, falls back to regex if API key not available)
        """
        self.root = tk.Tk()
        self.root.title("Document Information Extractor")
        self.root.geometry("1200x700")  # Wider window for split layout
        self.root.minsize(600, 500)  # Minimum size
        self.root.resizable(True, True)  # Allow resizing
        
        # Center the window on screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        self.fields = {}
        self.entries = {}
        self.checkboxes = {}  # Store checkboxes for each field
        self.extraction_metadata = {}  # Store extraction details (line numbers, source text)
        self.structured_lines = []  # list of {'page', 'line', 'text'} for source resolution
        self.use_ai = use_ai
        self.selected_file = None
        self.extracted_text = None
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)  # Left panel
        main_frame.columnconfigure(1, weight=1)  # Right panel
        main_frame.rowconfigure(2, weight=1)
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="Document Selection", padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Button(file_frame, text="Select Document", command=self._select_file).grid(row=0, column=0, padx=(0, 10))
        self.file_label = ttk.Label(file_frame, text="No file selected", foreground="gray")
        self.file_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Create split container for form and details panel
        split_container = ttk.Frame(main_frame)
        split_container.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        split_container.columnconfigure(0, weight=1)
        split_container.columnconfigure(1, weight=1)
        split_container.rowconfigure(0, weight=1)
        
        self.use_ocr_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Use OCR (for scanned documents)", 
                       variable=self.use_ocr_var).grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        
        self.use_ai_var = tk.BooleanVar(value=self.use_ai)
        ttk.Checkbutton(options_frame, text="Use AI Extraction (requires API key)", 
                       variable=self.use_ai_var).grid(row=0, column=1, sticky=tk.W)
        
        # LEFT PANEL: Form fields with checkboxes
        left_panel = ttk.Frame(split_container)
        left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(0, weight=1)
        
        # Form fields frame with scrollbar
        form_container = ttk.Frame(left_panel)
        form_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        form_container.columnconfigure(0, weight=1)
        form_container.rowconfigure(0, weight=1)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(form_container)
        scrollbar = ttk.Scrollbar(form_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        form_frame = ttk.LabelFrame(scrollable_frame, text="Extracted Information", padding="10")
        form_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        form_frame.columnconfigure(2, weight=1)
        
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Define form fields
        self.field_labels = [
            ("Name", "name"),
            ("Email", "email"),
            ("Phone", "phone"),
            ("Address", "address"),
            ("Date of Birth", "date_of_birth"),
            ("Company", "company"),
            ("Job Title", "job_title"),
            ("Date", "date"),
            ("Amount", "amount"),
            ("ID Number", "id_number"),
            ("Website", "website"),
            ("ZIP Code", "zip_code"),
        ]
        
        # Create form fields with checkboxes
        for idx, (label, key) in enumerate(self.field_labels):
            # Checkbox
            checkbox_var = tk.BooleanVar(value=False)
            checkbox = ttk.Checkbutton(
                form_frame, 
                variable=checkbox_var,
                command=self._update_extraction_details_display
            )
            checkbox.grid(row=idx, column=0, sticky=tk.W, pady=5, padx=(0, 5))
            self.checkboxes[key] = checkbox_var
            
            # Label
            ttk.Label(form_frame, text=f"{label}:").grid(row=idx, column=1, sticky=tk.W, pady=5, padx=(0, 10))
            
            # Entry field
            entry = ttk.Entry(form_frame, width=50)
            entry.grid(row=idx, column=2, sticky=(tk.W, tk.E), pady=5)
            self.entries[key] = entry
        
        # RIGHT PANEL: Extraction details
        right_panel = ttk.LabelFrame(split_container, text="Extraction Details", padding="10")
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=1)
        
        # Text widget with scrollbar for details
        details_text_frame = ttk.Frame(right_panel)
        details_text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        details_text_frame.columnconfigure(0, weight=1)
        details_text_frame.rowconfigure(0, weight=1)
        
        self.details_text = tk.Text(
            details_text_frame, 
            wrap=tk.WORD, 
            width=40, 
            height=20,
            font=("Courier", 10),
            bg="#f5f5f5",
            relief=tk.SUNKEN,
            borderwidth=1
        )
        details_scrollbar = ttk.Scrollbar(details_text_frame, orient="vertical", command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=details_scrollbar.set)
        
        self.details_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        details_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Initial message in details panel
        self.details_text.insert("1.0", "Click a checkbox next to any field to see source line...")
        self.details_text.config(state=tk.DISABLED)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text="Extract & Fill", command=self._on_extract).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self._clear_form).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Save as TXT", command=self._save_txt).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Export CSV", command=self._export_csv).grid(row=0, column=3, padx=5)
        ttk.Button(button_frame, text="Export JSON", command=self._export_json).grid(row=0, column=4, padx=5)
        
        # Status bar
        self.status_label = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def _select_file(self):
        """Open file dialog to select document"""
        file_path = filedialog.askopenfilename(
            title="Select Document",
            filetypes=[
                ("All Supported", "*.docx *.txt *.pdf"),
                ("Word Documents", "*.docx"),
                ("Text Files", "*.txt"),
                ("PDF Files", "*.pdf"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            self.selected_file = file_path
            filename = os.path.basename(file_path)
            self.file_label.config(text=filename, foreground="black")
            self._update_status(f"File selected: {filename}")
    
    def _on_extract(self):
        """Handle extract button click"""
        if not self.selected_file:
            messagebox.showwarning("No File", "Please select a document file first.")
            return
        
        try:
            # Import here to avoid circular imports
            from .parser import DocumentParser
            from .extractor import AIExtractor
            from .extractor_regex import RegexExtractor
            
            self._update_status("Extracting text from document...")
            parser = DocumentParser(self.selected_file, use_ocr=self.use_ocr_var.get())
            text, metadata = parser.extract_text()
            
            if not text:
                messagebox.showerror("Error", "Failed to extract text from document.")
                return
            
            self.extracted_text = text
            # Build structured_lines for robust source resolution (page, line, text)
            self.structured_lines = []
            current_page = None
            page_line_counter = 0
            for raw in (text or "").splitlines():
                # Detect page markers like '--- Page N ---'
                m = re.match(r'^---\s*Page\s*(\d+)\s*---', raw)
                if m:
                    try:
                        current_page = int(m.group(1))
                    except Exception:
                        current_page = None
                    page_line_counter = 0
                    continue

                if not raw.strip():
                    continue

                page_line_counter += 1
                self.structured_lines.append({
                    'page': current_page,
                    'line': page_line_counter,
                    'text': raw.strip()
                })

            self._update_status(f"Text extracted. Pages: {metadata.get('total_pages', 'N/A')}. Extracting information...")
            
            # Choose extraction method
            use_ai = self.use_ai_var.get()
            extracted_data = {}
            
            if use_ai:
                try:
                    extractor = AIExtractor()
                    # Use AI extraction with metadata
                    extracted_data, ai_metadata = extractor.extract_all_with_metadata(text)
                    if extracted_data:
                        self._update_status("Information extracted using AI!")
                        # Store AI-generated metadata
                        self._store_ai_extraction_metadata(extracted_data, ai_metadata)
                    else:
                        raise ValueError("AI extraction returned empty results")
                except ValueError as e:
                    # API key not available or empty results, fall back to regex
                    error_msg = str(e)
                    if "API key" in error_msg.lower() or "GOOGLE_API_KEY" in error_msg:
                        self._update_status("AI extraction unavailable (no API key). Using regex fallback...")
                    else:
                        self._update_status("AI extraction returned no results. Using regex fallback...")
                    extractor = RegexExtractor(text)
                    extracted_data = extractor.extract_all()
                    # No metadata for regex extraction
                    self.extraction_metadata = {}
                except Exception as e:
                    error_msg = str(e)
                    self._update_status(f"AI extraction error: {error_msg[:50]}... Using regex fallback...")
                    extractor = RegexExtractor(text)
                    extracted_data = extractor.extract_all()
                    # No metadata for regex extraction
                    self.extraction_metadata = {}
            else:
                extractor = RegexExtractor(text)
                extracted_data = extractor.extract_all()
                self._update_status("Information extracted using regex patterns!")
                # No metadata for regex extraction
                self.extraction_metadata = {}
            
            # Fill form with extracted data
            self._fill_form(extracted_data)
            messagebox.showinfo("Success", "Information extracted and form filled successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self._update_status(f"Error: {str(e)}")
    
    def _store_ai_extraction_metadata(self, extracted_data: Dict[str, Optional[str]], ai_metadata: Dict[str, Dict]):
        """Store AI-generated extraction metadata including source lines"""
        self.extraction_metadata = {}

        for key, value in extracted_data.items():
            if value:
                # Get metadata from AI response
                field_metadata = ai_metadata.get(key, {})
                source_entry = field_metadata.get('source_line', None)

                resolved = None
                # If AI provided a numbered index like '12' or '12: ...', try to map to structured_lines
                if source_entry:
                    # If it's an int or all-digits string, treat as line index in the flattened text
                    if isinstance(source_entry, int) or (isinstance(source_entry, str) and source_entry.strip().isdigit()):
                        try:
                            idx = int(source_entry) - 1
                            if 0 <= idx < len(self.structured_lines):
                                resolved = self.structured_lines[idx]
                        except Exception:
                            resolved = None
                    else:
                        # If it's a string, strip numbering prefix and try to match exact text in structured_lines
                        candidate = re.sub(r'^\s*\d+:\s*', '', str(source_entry)).strip()
                        # Try exact match first, then substring matches (both directions)
                        for row in self.structured_lines:
                            row_text = row.get('text', '') or ''
                            if candidate and candidate.lower() == row_text.lower():
                                resolved = row
                                break
                        if not resolved and candidate:
                            for row in self.structured_lines:
                                row_text = row.get('text', '') or ''
                                if candidate.lower() in row_text.lower() or row_text.lower() in candidate.lower():
                                    resolved = row
                                    break

                # If still not resolved, try to find by value
                if not resolved:
                    resolved = self._find_source_row_for_value(value)

                # Prepare metadata fields
                if resolved:
                    src_page = resolved.get('page')
                    src_line_no = resolved.get('line')
                    src_text = resolved.get('text')
                else:
                    src_page = None
                    src_line_no = None
                    src_text = 'Not found'

                self.extraction_metadata[key] = {
                    'value': value,
                    'source_page': src_page,
                    'source_line_no': src_line_no,
                    'source_text': src_text,
                    'field_name': next((label for label, k in self.field_labels if k == key), key)
                }

    def _find_source_line_in_text(self, value: str) -> Optional[str]:
        # Deprecated: use _find_source_row_for_value which returns structured row dict.
        row = self._find_source_row_for_value(value)
        if not row:
            return None
        # Format for backward compatibility: return line text
        return row.get('text')

    def _find_source_row_for_value(self, value: str) -> Optional[dict]:
        """Locate the structured row (page,line,text) that best matches the provided value."""
        if not self.structured_lines or not value:
            return None

        lowered = value.strip().lower()

        # Exact substring match on row text
        for row in self.structured_lines:
            if lowered in row['text'].lower():
                return row

        # Digits-only match (phone numbers, ids, zip)
        digits_only = re.sub(r'[^0-9]', '', value)
        if digits_only:
            for row in self.structured_lines:
                if digits_only in re.sub(r'[^0-9]', '', row['text']):
                    return row

            # If no direct digits match, try converting spelled-out digits in rows (e.g., 'Nine Zero Zero Zero One')
            digit_word_map = {
                'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
                'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9'
            }
            for row in self.structured_lines:
                # build digit string from words like 'Nine Zero Zero One'
                words = re.findall(r"[A-Za-z]+", row['text'])
                if not words:
                    continue
                converted = ''.join(digit_word_map.get(w.lower(), '') for w in words)
                if converted and digits_only in converted:
                    return row

        # Partial token match: first up to 3 words
        tokens = value.strip().split()
        if tokens:
            search = ' '.join(tokens[:min(3, len(tokens))]).lower()
            for row in self.structured_lines:
                if search in row['text'].lower():
                    return row

        return None
    
    def _update_extraction_details_display(self):
        """Update extraction details display based on selected checkboxes"""
        # Clear previous content
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete("1.0", tk.END)
        
        # Get all checked fields
        checked_fields = []
        for key, checkbox_var in self.checkboxes.items():
            if checkbox_var.get():
                checked_fields.append(key)
        
        # If no checkboxes are selected, show default message
        if not checked_fields:
            self.details_text.insert("1.0", "Click a checkbox next to any field to see source line...")
            self.details_text.config(state=tk.DISABLED)
            return
        
        # Build source line for all selected fields
        details_list = []
        
        for field_key in checked_fields:
            if field_key in self.extraction_metadata:
                metadata = self.extraction_metadata[field_key]
                value = metadata.get('value', '')
                field_name = metadata.get('field_name', field_key)

                src_text = metadata.get('source_text') if isinstance(metadata, dict) else None
                src_page = metadata.get('source_page') if isinstance(metadata, dict) else None
                src_line_no = metadata.get('source_line_no') if isinstance(metadata, dict) else None

                if src_text and src_text != 'Not found':
                    if src_page is not None or src_line_no is not None:
                        details_list.append(f"{field_name}: {value}\nPage: {src_page} Line: {src_line_no}\nText: {src_text}")
                    else:
                        details_list.append(f"{field_name}: {value}\nSource: {src_text}")
                else:
                    details_list.append(f"{field_name}: {value}\nSource: Not found")
            else:
                # No metadata available for this field
                label = next((label for label, k in self.field_labels if k == field_key), field_key)
                val = self.entries.get(field_key).get() if self.entries.get(field_key) else ''
                details_list.append(f"{label}: {val}\nSource: Not found")
        
        # Display source line only, one per line
        combined_details = "\n".join(details_list)
        self.details_text.insert("1.0", combined_details)
        self.details_text.config(state=tk.DISABLED)
    
    def _fill_form(self, data: Dict[str, Optional[str]]):
        """Fill form fields with extracted data"""
        # Clear all fields first to remove old data
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        
        # Ensure all checkboxes are unchecked (do not auto-select any)
        for checkbox_var in self.checkboxes.values():
            checkbox_var.set(False)
        
        # Fill with new extracted data
        for key, entry in self.entries.items():
            value = data.get(key, "")
            if value:
                entry.insert(0, str(value))
    
    def _clear_form(self):
        """Clear all form fields"""
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        for checkbox_var in self.checkboxes.values():
            checkbox_var.set(False)
        self.extracted_text = None
        self.extraction_metadata = {}
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete("1.0", tk.END)
        self.details_text.insert("1.0", "Click a checkbox next to any field to see source line...")
        self.details_text.config(state=tk.DISABLED)
        self._update_status("Form cleared")
    
    def _get_form_data(self) -> Dict[str, str]:
        """Get current form data"""
        data = {}
        for key, entry in self.entries.items():
            value = entry.get().strip()
            if value:
                label = next((label for label, k in self.field_labels if k == key), key)
                data[label] = value
        return data
    
    def _save_txt(self):
        """Save form data to a text file"""
        data = self._get_form_data()
        
        if not data:
            messagebox.showwarning("No Data", "No data to save.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Form Data",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    for label, value in data.items():
                        f.write(f"{label}: {value}\n")
                messagebox.showinfo("Success", f"Data saved to {file_path}")
                self._update_status(f"Data saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {str(e)}")
    
    def _export_csv(self):
        """Export form data to CSV"""
        data = self._get_form_data()
        
        if not data:
            messagebox.showwarning("No Data", "No data to export.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Form Data",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Field", "Value"])
                    for label, value in data.items():
                        writer.writerow([label, value])
                messagebox.showinfo("Success", f"Data exported to {file_path}")
                self._update_status(f"Data exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def _export_json(self):
        """Export form data to JSON"""
        data = self._get_form_data()
        
        if not data:
            messagebox.showwarning("No Data", "No data to export.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Form Data",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Success", f"Data exported to {file_path}")
                self._update_status(f"Data exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def _update_status(self, message: str):
        """Update status bar"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()