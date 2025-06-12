import re
import time

from googleapiclient.errors import HttpError


def get_sheet_id(url):
    """Extract the Google Sheet ID from the URL."""
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid Google Sheet URL")


def get_first_sheet_name(service, spreadsheet_id):
    # Get spreadsheet metadata
    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    first_sheet = spreadsheet["sheets"][0]
    print(f"First sheet name: {first_sheet['properties']['title']}")
    return first_sheet["properties"]["title"]


def add_job_to_sheet(service, first_sheet_name, job_list, SPREADSHEET_ID):
    """Add a job to the Google Sheet."""
    #
    try:
        for job in job_list:
            job_title = job.get("job_title")
            company = job.get("company")
            status = job.get("status")
            row_number = job.get("row_number")

            # Define the spreadsheet ID and range
            RANGE_NAME = f"{first_sheet_name}!A{row_number}:C{row_number}"  # Adjust the range as needed

            # Prepare the values to be added
            values = [[job_title, company, status]]
            body = {"values": values}

            # Append the values to the sheet
            result = (
                service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=RANGE_NAME,
                    valueInputOption="RAW",
                    body=body,
                )
                .execute()
            )

            # print(f"{result.get('updates').get('updatedCells')} cells appended.")
            time.sleep(1)
    except HttpError as error:
        print(f"An error occurred: {error}")
