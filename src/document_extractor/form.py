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
        self.root.geometry("800x700")
        
        self.fields = {}
        self.entries = {}
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
        main_frame.columnconfigure(1, weight=1)
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
        
        self.use_ocr_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Use OCR (for scanned documents)", 
                       variable=self.use_ocr_var).grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        
        self.use_ai_var = tk.BooleanVar(value=self.use_ai)
        ttk.Checkbutton(options_frame, text="Use AI Extraction (requires API key)", 
                       variable=self.use_ai_var).grid(row=0, column=1, sticky=tk.W)
        
        # Form fields frame with scrollbar
        form_container = ttk.Frame(main_frame)
        form_container.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
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
        form_frame.columnconfigure(1, weight=1)
        
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
        
        # Create form fields
        for idx, (label, key) in enumerate(self.field_labels):
            ttk.Label(form_frame, text=f"{label}:").grid(row=idx, column=0, sticky=tk.W, pady=5, padx=(0, 10))
            entry = ttk.Entry(form_frame, width=60)
            entry.grid(row=idx, column=1, sticky=(tk.W, tk.E), pady=5)
            self.entries[key] = entry
        
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
            self._update_status(f"Text extracted. Pages: {metadata.get('total_pages', 'N/A')}. Extracting information...")
            
            # Choose extraction method
            use_ai = self.use_ai_var.get()
            extracted_data = {}
            
            if use_ai:
                try:
                    extractor = AIExtractor()
                    extracted_data = extractor.extract_all(text)
                    if extracted_data:
                        self._update_status("Information extracted using AI!")
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
                except Exception as e:
                    error_msg = str(e)
                    self._update_status(f"AI extraction error: {error_msg[:50]}... Using regex fallback...")
                    extractor = RegexExtractor(text)
                    extracted_data = extractor.extract_all()
            else:
                extractor = RegexExtractor(text)
                extracted_data = extractor.extract_all()
                self._update_status("Information extracted using regex patterns!")
            
            # Fill form with extracted data
            self._fill_form(extracted_data)
            messagebox.showinfo("Success", "Information extracted and form filled successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self._update_status(f"Error: {str(e)}")
    
    def _fill_form(self, data: Dict[str, Optional[str]]):
        """Fill form fields with extracted data"""
        # Clear all fields first to remove old data
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        
        # Fill with new extracted data
        for key, entry in self.entries.items():
            value = data.get(key, "")
            if value:
                entry.insert(0, str(value))
    
    def _clear_form(self):
        """Clear all form fields"""
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.extracted_text = None
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

