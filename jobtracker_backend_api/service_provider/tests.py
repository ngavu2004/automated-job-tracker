from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import JobApplied

User = get_user_model()

# ==================== MODEL TESTS ====================


class JobAppliedModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )

    def test_create_job_applied(self):
        job = JobApplied.objects.create(
            user=self.user,
            job_title="Software Engineer",
            company="Tech Corp",
            status="applied",
        )
        self.assertEqual(job.user, self.user)
        self.assertEqual(job.job_title, "Software Engineer")
        self.assertEqual(job.company, "Tech Corp")
        self.assertEqual(job.status, "applied")
