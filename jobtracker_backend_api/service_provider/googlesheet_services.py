import os
import base64
import re
import time
import pandas as pd
from datetime import datetime, timezone
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .parsers import OpenAIExtractor
from .authenticate import get_googlesheet_service
from .models import JobApplied, FetchLog

def get_sheet_id(url):
    """Extract the Google Sheet ID from the URL."""
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid Google Sheet URL")

def add_job_to_sheet(service, user, job_list, SPREADSHEET_ID):
    """Add a job to the Google Sheet."""
    try:
        for job in job_list:
            job_title = job.get("job_title")
            company = job.get("company")
            status = job.get("status")
            row_number = job.get("row_number")

            # Define the spreadsheet ID and range
            RANGE_NAME = f"Sheet1!A{row_number}:C{row_number}"  # Adjust the range as needed

            # Prepare the values to be added
            values = [[job_title, company, status]]
            body = {
                'values': values
            }

            # Append the values to the sheet
            result = service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=RANGE_NAME,
                valueInputOption="RAW",
                body=body
            ).execute()

            # print(f"{result.get('updates').get('updatedCells')} cells appended.")
            time.sleep(1)
    except HttpError as error:
        print(f"An error occurred: {error}")