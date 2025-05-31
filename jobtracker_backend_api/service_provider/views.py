import os
import requests, jwt
import logging
from celery.result import AsyncResult
from django.utils import timezone
from django.conf import settings
# from django.contrib.auth.models import Group, User
from django.shortcuts import redirect
from urllib.parse import urlencode
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions, viewsets, status
from .tasks import fetch_emails_task
from .models import JobApplied, FetchLog, User, GoogleSheet
from .email_services import get_emails, extract_email_data
from .googlesheet_services import add_job_to_sheet, get_sheet_id
from .serializers import JobAppliedSerializer, FetchLogSerializer, GoogleSheetSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse


class GoogleOAuthLoginRedirect(APIView):
    def get(self, request):
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            "client_id": settings.GOOGLE_API_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_API_REDIRECT_URI,
            "response_type": "code",
            "scope": settings.GOOGLE_API_SCOPE,
            "access_type": "offline",
            "prompt": "consent"
        }
        url = f"{base_url}?{urlencode(params)}"
        return redirect(url)

class GoogleOAuthCallback(APIView):
    def set_jwt_cookies(self, response, user):
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        print(f"Generated access token: {access_token}")
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,  # Set to False for localhost/testing
            samesite="None",  # or "Strict"
            max_age=3600  # 1 hour
        )
        return response

    def get(self, request):
        code = request.query_params.get("code")
        if not code:
            return Response({"error": "Missing code"}, status=400)

        token_res = requests.post(os.environ["GOOGLE_API_TOKEN_URI"], data={
            "code": code,
            "client_id": settings.GOOGLE_API_CLIENT_ID,
            "client_secret": settings.GOOGLE_API_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_API_REDIRECT_URI,
            "grant_type": "authorization_code",
        }).json()

        print(token_res)

        google_access_token = token_res.get("access_token")
        google_refresh_token = token_res.get("refresh_token")
        id_token = token_res.get("id_token")
        print("Google access token:", google_access_token)

        if not google_access_token:
            return Response({"error": "Failed to get token"}, status=400)

        userinfo = requests.get(
            os.environ["GOOGLE_API_USER_INFO_URI"],
            headers={"Authorization": f"Bearer {google_access_token}"}
        ).json()

        print("User info:", userinfo)
        print("User access token:", google_access_token)
        email = userinfo["email"]

        user, _ = User.objects.get_or_create(email=email)
        user.google_access_token = google_access_token
        user.google_refresh_token = google_refresh_token
        user.token_expiry = timezone.now() + timezone.timedelta(seconds=token_res["expires_in"])
        user.last_login = timezone.now()
        user.save()

        # Generate JWT
        response = redirect(os.environ["FRONTEND_REDIRECT_URL"])
        return self.set_jwt_cookies(response, user)
    
class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def list(self, request, *args, **kwargs):
        return Response({
            "email": request.user.email,
            "first_time_user": len(FetchLog.objects.filter(user=request.user)) == 0,
            "sheet_id": request.user.google_sheet_id,
        })
    
    @action(detail=False, methods=['post'])
    def update_user_sheet_id(self, request):
        """
        Custom action to update Google Sheet ID.
        """
        user = request.user
        sheet_url = request.data.get('google_sheet_url')
        user.google_sheet_id = get_sheet_id(sheet_url)
        user.save()
        return Response({'status': 'updated', 'google_sheet_id': user.google_sheet_id})
    


class JobAppliedViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows job applications to be viewed or edited.
    """
    queryset = JobApplied.objects.all().order_by('-id')
    serializer_class = JobAppliedSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get', 'post'])
    def fetch_emails(self, request):
        """
        Custom action to fetch emails from external source.
        """
        task = fetch_emails_task.delay(request.user.id)
        return Response({"task_id": task.id})

    @action(detail=False, methods=['post', 'get'])
    def update_all_to_google_sheet(self, request):
        """
        Custom action to update all emails to Google Sheets.
        """
        # For all jobs in the database, add them to the Google Sheet
        jobs = JobApplied.objects.all()
        job_list = []
        for job in jobs:
            # Assuming job.job_title, job.company, and job.status are the fields to be added
            job_list.append({
                "job_title": job.job_title,
                "company": job.company,
                "status": job.status,
                "row_number": job.row_number
            })
        add_job_to_sheet(request, job_list, request.user.google_sheet_id)
        return Response({"status": "All emails updated to Google Sheets."})

class FetchLogViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows the last fetch date to be viewed or edited.
    """
    permission_classes = [IsAuthenticated]
    queryset = FetchLog.objects.all().order_by('-last_fetch_date')
    serializer_class = FetchLogSerializer
    
    @action(detail=False, methods=['post'])
    def add_log(self, request):
        """
        Custom action to add a fetch log for the authenticated user at a specified time.
        Expects 'last_fetch_date' in ISO 8601 format in the request data.
        """
        last_fetch_date_str = request.data.get('last_fetch_date')
        if not last_fetch_date_str:
            return Response({'error': 'last_fetch_date is required'}, status=400)
        last_fetch_date = timezone.datetime.fromisoformat(last_fetch_date_str)
        print(f"Parsed last_fetch_date: {last_fetch_date}")
        if not last_fetch_date:
            return Response({'error': 'Invalid datetime format'}, status=400)
        fetch_log = FetchLog.objects.create(
            user=request.user,
            last_fetch_date=last_fetch_date
        )
        return Response({'status': 'fetch log added', 'id': fetch_log.id})
class TaskStatusView(APIView):
    def get(self, request, task_id):
        result = AsyncResult(task_id)
        return Response({"status": result.status})