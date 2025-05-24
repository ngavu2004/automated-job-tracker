from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password="123"):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email))
        user.set_unusable_password()
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    USERNAME_FIELD = 'email'
    email = models.EmailField(unique=True)
    google_access_token = models.CharField(max_length=255)
    google_refresh_token = models.CharField(max_length=255)
    token_expiry = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    google_sheet_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.email

class GoogleSheet(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    id = models.AutoField(primary_key=True)
    sheet_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sheet_id
    
class JobApplied(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    id = models.AutoField(primary_key=True)
    job_title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    sender_email = models.EmailField(null=True)
    row_number = models.IntegerField(null=True)
    def __str__(self):
        return self.job_title
    
class FetchLog(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    id = models.AutoField(primary_key=True)
    last_fetch_date = models.DateTimeField()


    def __str__(self):
        return f"Last fetch date: {self.last_fetch_date}"