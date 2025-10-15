# Bug Fix: MultipleObjectsReturned Error

## Issue

**Error**: `MultipleObjectsReturned('get() returned more than one JobApplied -- it returned 2!')`

**Location**: `jobtracker_backend_api/service_provider/email_services.py` in the `get_emails()` function

## Root Cause

The error occurred when using `get_or_create()` on the `JobApplied` model:

```python
job_applied, created = JobApplied.objects.get_or_create(
    user=user,
    job_title=job_title,
    company=company_name,
    defaults={...}
)
```

**Why it failed**:
- `get_or_create()` internally uses `.get()` which expects 0 or 1 result
- When multiple `JobApplied` records exist with the same `user`, `job_title`, and `company_name`, `.get()` raises `MultipleObjectsReturned`
- This can happen when:
  1. A user receives multiple emails about the same job (status updates)
  2. Duplicate records were created before the fix
  3. The same job posting is sent multiple times

## Solution

Replaced `get_or_create()` with a safer approach using `filter().first()`:

```python
# Try to find existing job application (get most recent one)
job_applied = JobApplied.objects.filter(
    user=user,
    job_title=job_title,
    company=company_name
).order_by('-id').first()

if job_applied:
    # Update existing record with new status
    job_applied.status = application_status
    job_applied.sender_email = sender
    job_applied.save()
    print(f"Updated existing job: {job_title} at {company_name}")
else:
    # Create new record
    job_applied = JobApplied.objects.create(
        user=user,
        job_title=job_title,
        company=company_name,
        status=application_status,
        sender_email=sender,
        row_number=curr_job_count + 1
    )
    curr_job_count += 1
    print(f"Created new job: {job_title} at {company_name}")
```

## Benefits of This Approach

1. **No more crashes**: Handles multiple records gracefully
2. **Always updates the most recent**: Uses `.order_by('-id').first()` to get the latest record
3. **Clear logging**: Prints whether a job was updated or created
4. **Preserves existing data**: Doesn't delete duplicate records

## Cleaning Up Existing Duplicates (Optional)

If you want to remove duplicate records from your database, run this in Django shell:

```python
from jobtracker_backend_api.service_provider.models import JobApplied
from django.db.models import Count

# Find duplicates
duplicates = (
    JobApplied.objects
    .values('user', 'job_title', 'company')
    .annotate(count=Count('id'))
    .filter(count__gt=1)
)

# For each set of duplicates, keep the most recent one
for dup in duplicates:
    jobs = JobApplied.objects.filter(
        user_id=dup['user'],
        job_title=dup['job_title'],
        company=dup['company']
    ).order_by('-id')
    
    # Keep the first (most recent), delete the rest
    jobs_to_delete = jobs[1:]
    for job in jobs_to_delete:
        print(f"Deleting duplicate: {job.job_title} at {job.company} (ID: {job.id})")
        job.delete()
```

## Preventing Future Duplicates (Optional)

To enforce uniqueness at the database level, add a `unique_together` constraint to the model:

```python
# In models.py
class JobApplied(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    job_title = models.CharField(max_length=255, null=True)
    company = models.CharField(max_length=255, null=True)
    status = models.CharField(max_length=255, null=True)
    sender_email = models.EmailField(null=True)
    row_number = models.IntegerField(null=True)
    
    class Meta:
        unique_together = ['user', 'job_title', 'company']
    
    def __str__(self):
        return self.job_title
```

**Note**: Only add this constraint after cleaning up existing duplicates, and only if you want to prevent users from applying to the same job multiple times.

## Testing the Fix

1. Create duplicate records:
```python
from jobtracker_backend_api.service_provider.models import User, JobApplied

user = User.objects.first()
JobApplied.objects.create(user=user, job_title="Software Engineer", company="Tech Corp", status="applied")
JobApplied.objects.create(user=user, job_title="Software Engineer", company="Tech Corp", status="interview")
```

2. Run the email fetch task:
```python
from jobtracker_backend_api.service_provider.tasks import fetch_emails_task
fetch_emails_task.delay(user.id)
```

3. Verify it updates the most recent record instead of crashing

## Related Files

- `jobtracker_backend_api/service_provider/email_services.py` - Contains the fix
- `jobtracker_backend_api/service_provider/models.py` - JobApplied model definition
- `jobtracker_backend_api/service_provider/tasks.py` - Celery task that calls get_emails()

## Date Fixed

October 15, 2025

