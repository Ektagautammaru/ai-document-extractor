"""
AI-Powered Information Extractor using LangChain + Gemini
Converts unstructured text into structured JSON
"""

import os
from typing import Dict, Optional
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

