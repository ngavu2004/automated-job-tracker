"""
This module contains parsing services with OpenAI and Ollama LLM, 
dummy extract functions in case both ollama and openai doesnt work.
"""

from parsers import OpenAIExtractor, OllamaExtractor, DummyExtractor

# Define the extract_job_application function
def extract_job_application(subject, body, parser="openai"):
    """Extract job application details from email."""
    if parser == "openai":
        openai_extractor = OpenAIExtractor()
        return openai_extractor.get_response(subject, body)
    elif parser == "ollama":
        ollama_extractor = OllamaExtractor()
        return ollama_extractor.get_response(subject, body)
    else:
        dummy_extractor = DummyExtractor()
        return dummy_extractor.get_response(subject, body)

