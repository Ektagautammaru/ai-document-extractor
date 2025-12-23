"""
Main Application Entry Point
Document Information Extractor and Form Filler
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from .form import FormFiller


def main():
    """Main function to start the application"""
    # Load environment variables
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        # Try to load from current directory
        load_dotenv()
    
    # Check if AI extraction is available
    use_ai = os.getenv("GOOGLE_API_KEY") is not None
    
    if not use_ai:
        print("Note: GOOGLE_API_KEY not found. AI extraction will not be available.")
        print("The application will use regex-based extraction instead.")
        print("To enable AI extraction, set GOOGLE_API_KEY in .env file.\n")
    
    # Create and run the GUI application
    app = FormFiller(use_ai=use_ai)
    app.run()


if __name__ == "__main__":
    main()

