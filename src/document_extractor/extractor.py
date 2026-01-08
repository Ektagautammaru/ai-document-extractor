"""
AI-Powered Information Extractor using LangChain + Gemini
Converts unstructured text into structured JSON
"""

import os
from typing import Dict, Optional, Tuple
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.prompts import ChatPromptTemplate
    from langchain.output_parsers import PydanticOutputParser
except ImportError:
    # Fallback for different langchain versions
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import PydanticOutputParser
    except ImportError:
        raise ImportError(
            "langchain-google-genai is required for AI extraction. "
            "Install it with: pip install langchain-google-genai"
        )
from pydantic import BaseModel, Field
import json


class ExtractedInfo(BaseModel):
    """Pydantic model for structured extraction"""
    name: Optional[str] = Field(None, description="Full name of the person")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    address: Optional[str] = Field(None, description="Full address")
    date_of_birth: Optional[str] = Field(None, description="Date of birth")
    company: Optional[str] = Field(None, description="Company name")
    job_title: Optional[str] = Field(None, description="Job title or position")
    date: Optional[str] = Field(None, description="Any relevant date")
    amount: Optional[str] = Field(None, description="Monetary amount")
    id_number: Optional[str] = Field(None, description="ID number, SSN, passport number, etc.")
    website: Optional[str] = Field(None, description="Website URL")
    zip_code: Optional[str] = Field(None, description="ZIP or postal code")


class AIExtractor:
    """AI-powered extractor using LangChain + Gemini"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AI extractor
        
        Args:
            api_key: Google Gemini API key. If None, will try to get from environment
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "Google API key not found. Please set GOOGLE_API_KEY environment variable "
                "or pass it to the constructor."
            )
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=self.api_key,
            temperature=0,
        )
        
        # Create output parser
        self.output_parser = PydanticOutputParser(pydantic_object=ExtractedInfo)
        
        # Create prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at extracting structured information from documents.
            Extract all relevant information from the provided text and return it in a structured format.
            Only extract information that is clearly present in the text. If a field is not found, set it to null.
            
            {format_instructions}
            """),
            ("human", "Extract information from the following text:\n\n{text}")
        ])
    
    def extract_all(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extract all available information from the text using AI
        
        Args:
            text: Raw text extracted from document
            
        Returns:
            Dictionary containing extracted fields
        """
        try:
            # Limit text length to avoid token limits (keep first 8000 chars)
            if len(text) > 8000:
                text = text[:8000] + "\n\n[Text truncated...]"
            
            # Format the prompt
            formatted_prompt = self.prompt.format_messages(
                text=text,
                format_instructions=self.output_parser.get_format_instructions()
            )
            
            # Get response from LLM
            response = self.llm.invoke(formatted_prompt)
            
            # Parse the response
            parsed_output = self.output_parser.parse(response.content)
            
            # Convert to dictionary
            result = parsed_output.dict()
            
            # Remove None values for cleaner output
            return {k: v for k, v in result.items() if v is not None}
            
        except Exception as e:
            print(f"AI extraction error: {str(e)}")
            # Return empty dict on error
            return {}
    
    def extract_all_with_metadata(self, text: str) -> Tuple[Dict[str, Optional[str]], Dict[str, Dict]]:
        """
        Extract all available information from the text using AI with source line metadata
        
        Args:
            text: Raw text extracted from document
            
        Returns:
            Tuple of (extracted_data_dict, metadata_dict)
            metadata_dict contains: source_line for each field (the exact line from which value was extracted)
        """
        original_text = text
        lines = original_text.split('\n')
        
        try:
            # Limit text length to avoid token limits
            if len(text) > 8000:
                text = text[:8000] + "\n\n[Text truncated...]"
            
            # Create prompt that asks AI to provide source lines
            numbered_text = "\n".join([f"{idx+1}: {line}" for idx, line in enumerate(lines)])
            
            enhanced_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert at extracting structured information from documents.
                
                CRITICAL REQUIREMENT: 
                - If you extract a value for ANY field, you MUST also provide the exact source_line from the document.
                - The source_line must be the complete line content from the document where you found that value.
                - If you do NOT extract a value for a field (set it to null), then you do NOT need to provide a source_line for that field.
                - For EVERY field that has a value in "fields", there MUST be a corresponding entry in "source_lines" with the same key.
                
                Return a JSON object with the following EXACT structure:
                {
                    "fields": {
                        "name": "extracted value or null",
                        "email": "extracted value or null",
                        "phone": "extracted value or null",
                        "address": "extracted value or null",
                        "date_of_birth": "extracted value or null",
                        "company": "extracted value or null",
                        "job_title": "extracted value or null",
                        "date": "extracted value or null",
                        "amount": "extracted value or null",
                        "id_number": "extracted value or null",
                        "website": "extracted value or null",
                        "zip_code": "extracted value or null"
                    },
                    "source_lines": {
                        "name": "exact line from document where name was found",
                        "email": "exact line from document where email was found",
                        ...
                    }
                }
                
                RULES:
                1. Only include fields in "source_lines" that have a non-null value in "fields"
                2. The source_line must be the exact line content from the numbered text provided
                3. If a field value is null, do NOT include it in "source_lines"
                4. If a field has a value, it MUST have a corresponding source_line
                
                Example:
                If you extract name="John Doe" from line "5: Full Name: John Doe", then:
                "fields": {"name": "John Doe", ...}
                "source_lines": {"name": "Full Name: John Doe", ...}
                """),
                ("human", "Extract information from the following numbered text. For EVERY extracted value, you MUST provide the exact source line from which you extracted it. Remember: if you extract a value, you MUST provide its source_line. If you don't extract a value (null), don't provide source_line for it.\n\n{text}")
            ])
            
            # Format the prompt with numbered text
            formatted_prompt = enhanced_prompt.format_messages(text=numbered_text)
            
            # Get response from LLM
            response = self.llm.invoke(formatted_prompt)
            
            # Parse JSON response
            content = response.content.strip()
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            result = json.loads(content.strip())
            
            # Extract fields and source lines
            extracted_data = result.get("fields", {})
            source_lines = result.get("source_lines", {})
            
            # Remove None values from extracted data
            extracted_data = {k: v for k, v in extracted_data.items() if v is not None}
            
            # Build metadata with source lines
            # CRITICAL: For every extracted value, we must have a source_line
            metadata = {}
            for key, value in extracted_data.items():
                # Get source_line from AI response
                source_line = source_lines.get(key, None)
                
                # If AI didn't provide source_line, try to find it in the text
                if not source_line or source_line.strip() == "":
                    # Search for the value in the text lines
                    for line in lines:
                        if value and value.strip().lower() in line.lower():
                            source_line = line.strip()
                            break
                    
                    # If still not found, try partial match
                    if not source_line and value:
                        value_words = value.split()
                        if len(value_words) > 0:
                            search_term = ' '.join(value_words[:min(3, len(value_words))])
                            for line in lines:
                                if search_term.lower() in line.lower():
                                    source_line = line.strip()
                                    break
                
                # Store metadata - if we have a value, we must have a source_line
                if value:
                    metadata[key] = {
                        'source_line': source_line if source_line and source_line.strip() else 'Not found'
                    }
            
            return extracted_data, metadata
            
        except json.JSONDecodeError as e:
            print(f"AI extraction JSON parsing error: {str(e)}")
            # Fallback: use regular extraction and find source lines manually
            try:
                extracted_data = self.extract_all(text)
                if not extracted_data:
                    return {}, {}
                
                metadata = {}
                for key, value in extracted_data.items():
                    if value:
                        source_line = None
                        # Search for the value in the text
                        for line in lines:
                            if value.strip().lower() in line.lower():
                                source_line = line.strip()
                                break
                        
                        # If not found, try partial match
                        if not source_line:
                            value_words = value.split()
                            if len(value_words) > 0:
                                search_term = ' '.join(value_words[:2])
                                for line in lines:
                                    if search_term.lower() in line.lower():
                                        source_line = line.strip()
                                        break
                        
                        metadata[key] = {
                            'source_line': source_line if source_line else 'Not found'
                        }
                
                return extracted_data, metadata
            except Exception as e2:
                print(f"Fallback extraction error: {str(e2)}")
                return {}, {}
                
        except Exception as e:
            print(f"AI extraction with metadata error: {str(e)}")
            # Fallback to regular extraction
            try:
                extracted_data = self.extract_all(text)
                if not extracted_data:
                    return {}, {}
                
                # Generate metadata from text search
                metadata = {}
                for key, value in extracted_data.items():
                    if value:
                        source_line = None
                        for line in lines:
                            if value.strip().lower() in line.lower():
                                source_line = line.strip()
                                break
                        metadata[key] = {
                            'source_line': source_line if source_line else 'Not found'
                        }
                return extracted_data, metadata
            except:
                return {}, {}
    
    def extract_custom(self, text: str, fields: list) -> Dict[str, Optional[str]]:
        """
        Extract specific fields from text
        
        Args:
            text: Raw text extracted from document
            fields: List of field names to extract
            
        Returns:
            Dictionary containing only requested fields
        """
        try:
            if len(text) > 8000:
                text = text[:8000] + "\n\n[Text truncated...]"
            
            fields_str = ", ".join(fields)
            custom_prompt = ChatPromptTemplate.from_messages([
                ("system", f"""Extract only the following fields from the text: {fields_str}
                Return the result as a JSON object with these keys.
                If a field is not found, set it to null."""),
                ("human", "Extract information from:\n\n{text}")
            ])
            
            formatted_prompt = custom_prompt.format_messages(text=text)
            response = self.llm.invoke(formatted_prompt)
            
            # Try to parse JSON from response
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            result = json.loads(content.strip())
            return {k: v for k, v in result.items() if v is not None}
            
        except Exception as e:
            print(f"Custom extraction error: {str(e)}")
            return {}
