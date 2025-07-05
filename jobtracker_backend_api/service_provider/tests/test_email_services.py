import unittest
from unittest.mock import Mock, patch
from django.test import TestCase
import base64

from ..email_services import extract_text_content

class ExtractTextContentTest(TestCase):
    """Test cases for extract_text_content function"""

    def test_extract_plain_text_body(self):
        """Test extracting text from plain text email body"""
        message = {
            'payload': {
                'body': {
                    'data': base64.urlsafe_b64encode(b'This is a plain text email').decode()
                },
                'mimeType': 'text/plain'
            }
        }
        
        result = extract_text_content(message)
        self.assertEqual(result, 'This is a plain text email')

    def test_extract_html_body_with_text_conversion(self):
        """Test extracting text from HTML email body"""
        html_content = '<html><body><h1>Job Application</h1><p>Dear candidate, thank you for applying to our <strong>Software Engineer</strong> position.</p></body></html>'
        message = {
            'payload': {
                'body': {
                    'data': base64.urlsafe_b64encode(html_content.encode()).decode()
                },
                'mimeType': 'text/html'
            }
        }
        
        result = extract_text_content(message)
        self.assertIn('Job Application', result)
        self.assertIn('Software Engineer', result)
        self.assertNotIn('<html>', result)  # HTML tags should be stripped
        self.assertNotIn('<p>', result)

    def test_extract_from_multipart_text_plain(self):
        """Test extracting text from multipart email with text/plain part"""
        message = {
            'payload': {
                'parts': [
                    {
                        'mimeType': 'text/plain',
                        'body': {
                            'data': base64.urlsafe_b64encode(b'This is the plain text part').decode()
                        }
                    },
                    {
                        'mimeType': 'text/html',
                        'body': {
                            'data': base64.urlsafe_b64encode(b'<p>This is HTML</p>').decode()
                        }
                    }
                ]
            }
        }
        
        result = extract_text_content(message)
        self.assertEqual(result, 'This is the plain text part')

    def test_extract_from_multipart_html_when_no_plain(self):
        """Test extracting from HTML when no plain text available"""
        message = {
            'payload': {
                'parts': [
                    {
                        'mimeType': 'application/pdf',
                        'body': {'data': 'pdf_content'}
                    },
                    {
                        'mimeType': 'text/html',
                        'body': {
                            'data': base64.urlsafe_b64encode(b'<div>HTML only content</div>').decode()
                        }
                    }
                ]
            }
        }
        
        result = extract_text_content(message)
        self.assertIn('HTML only content', result)