import os
from django.test import TestCase

class EnvVarTest(TestCase):
    def test_google_env_vars_exist(self):
        self.assertIsNotNone(os.getenv("GOOGLE_API_CLIENT_ID"))
        self.assertIsNotNone(os.getenv("GOOGLE_API_CLIENT_SECRET"))