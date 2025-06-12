from openai import OpenAI
import os
import json

class OpenAIExtractor:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")

    def get_response(self, email_subject, email_body):
        # Define the client of the OpenAI API
        client = OpenAI(api_key=self.api_key)
        
        # Define the prompt
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "developer", 
                    "content": """You are a job applicant checking emails for job application status. 
                                When you receive an email, first, you check if the email is a job application status update email or not.
                                If it is a job application email, you extract the job title, company name and status to JSON. The status can be "applied", "interview", "offer", or "rejected".
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
                                "enum": ["applied", "interview", "offer", "rejected"]
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