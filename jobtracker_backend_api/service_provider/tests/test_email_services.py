from unittest.mock import MagicMock
from django.test import TestCase
import base64

from ..email_services import extract_text_content

class ExtractTextContentTest(TestCase):
    """Test cases for extract_text_content function"""

    def test_plain_text(self):
        part = MagicMock()
        part.get_content_type.return_value = "text/plain"
        part.get.return_value = ""
        part.get_content_charset.return_value = "utf-8"
        part.get_payload.return_value = b"Plain text body"
        self.assertEqual(extract_text_content(part), "Plain text body")