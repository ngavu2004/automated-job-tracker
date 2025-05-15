import yaml
from openai import OpenAI
import re
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
class OpenAIExtractor:
    def __init__(self):
        self.api_key = ''
        # get the open api key
        with open('jobtracker_backend_api/OpenAI_API.yaml', 'r') as file:
            self.api_key = yaml.safe_load(file)

    def get_response(self, email_subject, email_body):
        # Define the client of the OpenAI API
        client = OpenAI(api_key=self.api_key['api_key'])
        
        # Define the prompt
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "developer", 
                    "content": """You are a job applicant checking emails for job application. 
                                When you receive an email, first, you check if the email is a job application email or not.
                                If it is a job application email, you extract the job title, company name and status to JSON. The status can be "applied", "interview", "offer", "rejected" or "not interested".
                                If it is not a job application email, you return "Not a job application email"."""
                },
                {
                    "role": "user", 
                    "content": f"Subject: {email_subject}\nBody: {email_body}"
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "email_schema",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "is_job_application_email": {
                                "type": "boolean"
                            },
                            "job_title": {
                                "type": "string"
                            },
                            "company_name": {
                                "type": "string"
                            },
                            "status": {
                                "type": "string",
                                "enum": ["applied", "interview", "offer", "rejected", "not interested"]
                            },
                            "additionalProperties": False
                        }
                    }
                }
            }
        )

        # Parse the JSON content from the response
        response_content = response.choices[0].message.content
        response_json = json.loads(response_content)
        return response_json
    
class OllamaExtractor:
    def __init__(self, model):
        self.model = model

    def get_response(self, email_subject, email_body):
        return self.model.get_response(email_subject, email_body)
    
class DummyExtractor:
    def __init__(self):
        pass

    def get_response(self, email_subject, email_body):
        return "Dummy Company"