"""
Regex-based Information Extractor (Fallback Mode)
Extracts structured information from text using pattern matching
Works offline without API keys
"""

import re
from typing import Dict, Optional, List


class RegexExtractor:
    """Extracts structured information from text using regex patterns"""
    
    def __init__(self, text: str):
        """
        Initialize the extractor with text
        
        Args:
            text: Raw text extracted from document
        """
        self.text = text
    
    def extract_all(self) -> Dict[str, Optional[str]]:
        """
        Extract all available information from the text
        
        Returns:
            Dictionary containing extracted fields
        """
        return {
            'name': self.extract_name(),
            'email': self.extract_email(),
            'phone': self.extract_phone(),
            'address': self.extract_address(),
            'date_of_birth': self.extract_date_of_birth(),
            'company': self.extract_company(),
            'job_title': self.extract_job_title(),
            'date': self.extract_date(),
            'amount': self.extract_amount(),
            'id_number': self.extract_id_number(),
            'website': self.extract_website(),
            'zip_code': self.extract_zip_code(),
        }
    
    def extract_name(self) -> Optional[str]:
        """Extract person's name"""
        patterns = [
            # Prefer "Full Name" over just "Name"
            r'Full\s+Name[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            r'(?:Name|Name of|Applicant Name|Contact Name)[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            r'^([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'(?:Dear|Hello|Hi)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, self.text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                name = match.group(1).strip()
                # Stop at end of line or before common separators
                name = re.split(r'[,\n\r]', name)[0].strip()
                # Validate name (should have at least 2 words, each starting with capital)
                words = name.split()
                if len(words) >= 2 and all(word[0].isupper() and word.isalpha() for word in words[:2]):
                    # Prefer longer names (Full Name) over shorter ones
                    if len(words) >= 3:
                        return ' '.join(words[:3])
                    return ' '.join(words[:2])
        
        # Try to find capitalized words that look like names in first few lines
        lines = self.text.split('\n')
        for line in lines[:10]:
            line = line.strip()
            # Skip lines that are headers or separators
            if not line or line.startswith('=') or len(line) < 5:
                continue
            words = line.split()
            if len(words) >= 2:
                # Check if first two words look like a name
                if all(word[0].isupper() and word.isalpha() for word in words[:2]):
                    # Make sure it's not a label like "Bill To:" or "Name:"
                    if not any(label in line.lower() for label in ['name:', 'email:', 'phone:', 'address:', 'bill to:', 'invoice']):
                        return ' '.join(words[:2])
        
        return None
    
    def extract_email(self) -> Optional[str]:
        """Extract email address - prefer personal emails over generic ones"""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(pattern, self.text)
        if matches:
            # Prefer emails that are not generic service emails
            personal_keywords = ['customer', 'contact', 'email', 'mail']
            generic_keywords = ['billing', 'support', 'info', 'noreply', 'no-reply', 'admin']
            
            # First, try to find a personal email
            for email in matches:
                email_lower = email.lower()
                # Skip generic service emails
                if any(keyword in email_lower for keyword in generic_keywords):
                    continue
                # Prefer emails with personal keywords or just return first non-generic
                if any(keyword in email_lower for keyword in personal_keywords) or not any(gen in email_lower for gen in generic_keywords):
                    return email
            
            # If no personal email found, return first one
            return matches[0]
        return None
    
    def extract_phone(self) -> Optional[str]:
        """Extract phone number"""
        patterns = [
            r'(?:Phone|Mobile|Tel|Contact|Telephone)[:\s]+([\+]?[\d\s\-\(\)]{10,})',
            r'\b(\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})\b',
            r'\b(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})\b',
            r'\b(\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9})\b',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                phone = match.group(1).strip()
                # Clean and validate
                digits_only = re.sub(r'[^\d+]', '', phone)
                if len(digits_only) >= 10:
                    return phone
        
        return None
    
    def extract_address(self) -> Optional[str]:
        """Extract address"""
        patterns = [
            r'(?:Address|Location|Residence|Mailing Address)[:\s]+([^\n]{10,150})',
            r'(\d+\s+[A-Za-z0-9\s,]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Court|Ct|Way|Place|Pl)[^\n]*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                address = match.group(1).strip()
                # Clean up address
                address = re.sub(r'\s+', ' ', address)
                # Remove common prefixes
                address = re.sub(r'^(Address|Location|Residence)[:\s]+', '', address, flags=re.IGNORECASE)
                if len(address) > 10:
                    return address[:200]  # Limit length
        
        return None
    
    def extract_date_of_birth(self) -> Optional[str]:
        """Extract date of birth - only if explicitly labeled"""
        patterns = [
            r'(?:Date of Birth|DOB|Birth Date|Born|Birthday)[:\s]+(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})',
            r'(?:Date of Birth|DOB|Birth Date)[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
            r'(?:Date of Birth|DOB)[:\s]+(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                dob = match.group(1).strip()
                # Validate it's a reasonable date (not invoice dates, etc.)
                # Check if it's in a reasonable range (1900-2010 for birth dates)
                year_match = re.search(r'(\d{4})', dob)
                if year_match:
                    year = int(year_match.group(1))
                    if 1900 <= year <= 2010:  # Reasonable birth year range
                        return dob
                elif len(dob.split('/')) == 3:
                    # For MM/DD/YYYY format, check year
                    parts = dob.split('/')
                    if len(parts) == 3 and parts[2].isdigit():
                        year = int(parts[2])
                        if 1900 <= year <= 2010:
                            return dob
        
        return None
    
    def extract_company(self) -> Optional[str]:
        """Extract company name"""
        patterns = [
            r'(?:Company|Employer|Organization|Organization Name|Company Name|Employer Name)[:\s]+([A-Za-z0-9\s&.,\-]+)',
            r'(?:Works at|Employed at|Works for)[:\s]+([A-Za-z0-9\s&.,\-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                company = match.group(1).strip()
                # Take first line or first 100 chars
                company = company.split('\n')[0].strip()[:100]
                if len(company) > 2:
                    return company
        
        return None
    
    def extract_job_title(self) -> Optional[str]:
        """Extract job title - only if explicitly present"""
        patterns = [
            r'(?:Job Title|Position|Designation|Title|Role)[:\s]+([A-Za-z\s&/\-]+)',
            r'(?:Works as|Position is|Title is)[:\s]+([A-Za-z\s&/\-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                # Stop at end of line or common separators
                title = re.split(r'[\n\r,;]', title)[0].strip()
                # Remove common prefixes that might be captured
                title = re.sub(r'^(the|a|an)\s+', '', title, flags=re.IGNORECASE)
                if len(title) > 2 and len(title) < 100:
                    return title
        
        return None
    
    def extract_date(self) -> Optional[str]:
        """Extract any date (prefer labeled dates)"""
        patterns = [
            r'(?:Date|Invoice Date|Application Date|Submission Date|Due Date)[:\s]+(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})',
            r'(?:Date|Invoice Date|Application Date)[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
            # Only match unlabeled dates if they're in a date-like context
            r'(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',  # Prefer 4-digit years
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                date_str = match.group(1).strip()
                # Stop at end of line
                date_str = re.split(r'[\n\r]', date_str)[0].strip()
                return date_str
        
        return None
    
    def extract_amount(self) -> Optional[str]:
        """Extract monetary amount"""
        patterns = [
            r'(?:Amount|Total|Price|Cost|Fee|Payment)[:\s]*\$?([\d,]+\.?\d*)',
            r'\$([\d,]+\.?\d*)',
            r'([\d,]+\.?\d*)\s*(?:USD|dollars|Dollars)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def extract_id_number(self) -> Optional[str]:
        """Extract ID number (SSN, passport, etc.)"""
        patterns = [
            r'(?:ID|ID Number|SSN|Social Security|Passport Number|License Number)[:\s]+([A-Z0-9\-]+)',
            r'\b([A-Z]{1,2}\d{6,})\b',
            r'\b(\d{3}-\d{2}-\d{4})\b',  # SSN format
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def extract_website(self) -> Optional[str]:
        """Extract website URL"""
        pattern = r'(?:Website|URL|Web|Site)[:\s]+(https?://[^\s]+|www\.[^\s]+|[a-z0-9-]+\.[a-z]{2,}(?:\.[a-z]{2,})?)'
        match = re.search(pattern, self.text, re.IGNORECASE)
        if match:
            url = match.group(1).strip()
            if not url.startswith('http'):
                url = 'https://' + url
            return url
        return None
    
    def extract_zip_code(self) -> Optional[str]:
        """Extract zip/postal code"""
        patterns = [
            r'\b(\d{5}(?:-\d{4})?)\b',  # US ZIP
            r'(?:ZIP|Postal Code|Postcode)[:\s]+(\d{5,10})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None

