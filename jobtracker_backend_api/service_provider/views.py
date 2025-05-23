import os
import requests, jwt
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
from .models import JobApplied, FetchLog, User
from .email_services import get_emails, extract_email_data
from .googlesheet_services import add_job_to_sheet
from .serializers import JobAppliedSerializer, FetchLogSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse


class GoogleOAuthLoginRedirect(APIView):
    def get(self, request):
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            "client_id": settings.GOOGLE_API_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_API_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/spreadsheets",
            "access_type": "offline",
            "prompt": "consent"
        }
        url = f"{base_url}?{urlencode(params)}"
        return redirect(url)

class GoogleOAuthCallback(APIView):
    def set_jwt_cookies(self, response, user):
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,  # only for HTTPS
            samesite="Lax",  # or "Strict"
            max_age=3600  # 1 hour
        )
        return redirect(os.environ["FRONTEND_URL"])
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

        access_token = token_res.get("access_token")
        refresh_token = token_res.get("refresh_token")
        id_token = token_res.get("id_token")


        if not access_token:
            return Response({"error": "Failed to get token"}, status=400)

        userinfo = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        ).json()

        email = userinfo["email"]

        user, created = User.objects.get_or_create(email=email)
        if created:
            user.access_token = access_token
            user.refresh_token = refresh_token
            user.token_expiry = timezone.now() + timezone.timedelta(seconds=token_res["expires_in"])
            user.save()

        # Generate JWT
        response = JsonResponse({"message": "Login successful"})
        return self.set_jwt_cookies(response, user)

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
        get_emails()
        return Response({"status": "Emails fetched and updated."})

    @action(detail=False, methods=['post', 'get'])
    def update_all_to_google_sheet(self, request):
        """
        Custom action to update all emails to Google Sheets.
        """
        # For all jobs in the database, add them to the Google Sheet
        jobs = JobApplied.objects.all()
        for job in jobs:
            # Assuming job.job_title, job.company, and job.status are the fields to be added
            add_job_to_sheet(job.job_title, job.company, job.status, job.row_number)
        return Response({"status": "All emails updated to Google Sheets."})

class FetchLogViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows the last fetch date to be viewed or edited.
    """
    queryset = FetchLog.objects.all().order_by('-last_fetch_date')
    serializer_class = FetchLogSerializer

class UpdateSheetView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        sheet_id = request.data.get('google_sheet_id')
        user.google_sheet_id = sheet_id
        user.save()
        return Response({'status': 'updated', 'google_sheet_id': sheet_id})