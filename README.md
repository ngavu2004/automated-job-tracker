# Automated Job Tracker

The Automated Job Tracker is a Django-based application that helps you track your job applications automatically by fetching and processing emails from your Gmail account. It extracts job application data such as job title, company name, and application status from emails and stores them in a PostgreSQL database for easy tracking and management.

---

## Features

- Fetch unread recruiter emails from Gmail
- Extract job application data (job title, company name, application status) from emails
- Store and manage job application data in a PostgreSQL database
- View and edit job application data through a REST API
- Clear email records from the database
- Integrate with Google Sheets for job data storage
- OpenAI API integration for advanced processing

---

## Requirements

- Python 3.8+
- Django 3.2+
- Google API Client Library for Python
- Django REST Framework
- PostgreSQL database

---

## Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/yourusername/automated-job-tracker.git
    cd automated-job-tracker
    ```

2. **Create and activate a virtual environment:**
    ```sh
    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3. **Install the required packages:**
    ```sh
    pip install -r requirements.txt
    ```

4. **Configure environment variables:**

    Create a `.env` file in the project root with the following content (already provided in your repo):

    ```properties
    # Django setting secret keys
    SECRET_KEY="your-django-secret-key"

    # AWS PostgreSQL Backend Configuration
    DB_ENGINE=django.db.backends.postgresql_psycopg2
    DB_NAME=postgres
    DB_USER=postgres
    DB_PASSWORD=your-db-password
    DB_HOST=your-db-host.amazonaws.com
    DB_PORT=5432

    # Google Cloud API Credentials
    GOOGLE_API_CLIENT_ID="your-google-client-id"
    GOOGLE_API_PROJECT_ID="your-google-project-id"
    GOOGLE_API_AUTH_URI="https://accounts.google.com/o/oauth2/auth"
    GOOGLE_API_TOKEN_URI="https://oauth2.googleapis.com/token"
    GOOGLE_API_AUTH_PROVIDER_X509_CERT_URL="https://www.googleapis.com/oauth2/v1/certs"
    GOOGLE_API_CLIENT_SECRET="your-google-client-secret"
    GOOGLE_API_REDIRECT_URI="http://localhost"

    # OpenAI API Key
    OPENAI_API_KEY="your-openai-api-key"

    # Spreadsheet ID to store job data
    SPREADSHEET_ID="your-google-sheet-id"
    ```

    > **Note:** Do not commit your [.env](http://_vscodecontentref_/0) file to version control.

5. **Google API Setup:**

    - Create a project in the [Google Cloud Console](https://console.cloud.google.com/).
    - Enable the Gmail API for the project.
    - Create OAuth 2.0 credentials and copy the values into your [.env](http://_vscodecontentref_/1) file as shown above.
    - The application will automatically generate [credentials.json](http://_vscodecontentref_/2) from your [.env](http://_vscodecontentref_/3) file if it does not exist.

6. **Run Django migrations:**
    ```sh
    python manage.py makemigrations
    python manage.py migrate
    ```

7. **Create a superuser for the Django admin interface:**
    ```sh
    python manage.py createsuperuser
    ```

8. **Start the Django development server:**
    ```sh
    python manage.py runserver
    ```

9. **Access the application:**
    - Go to [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) and log in with your superuser account.

---

## Front End

- Open the terminal, type `cd frontend`, then run `npm start`. You will be automatically redirected to the web browser.

---

## Usage

Here’s a sample **API documentation section** you can add to your README.md for your Django backend:

---

## API Endpoints

### Authentication

#### `GET /auth/google/login/`
Redirects the user to Google OAuth login.

#### `GET /auth/google/callback/`
Handles the OAuth callback from Google, creates/updates the user, and sets the JWT cookie.

---

### Users

#### `GET /users/`
Returns the authenticated user's info.
- **Requires:** JWT authentication (cookie)
- **Response:**
    ```json
    {
      "email": "user@example.com",
      "first_time_user": true,
      "sheet_id": "your-google-sheet-id"
    }
    ```

#### `POST /users/update_user_sheet_id/`
Update the user's Google Sheet ID.
- **Body:** `{ "google_sheet_url": "<sheet_url>" }`
- **Response:** `{ "status": "updated", "google_sheet_id": "<id>" }`

#### `POST /users/remove_sheet_id/`
Remove (set to null) the user's Google Sheet ID.
- **Response:** `{ "status": "removed", "google_sheet_id": null }`

---

### Jobs

#### `GET /jobs/`
List all jobs for the authenticated user.

#### `POST /jobs/`
Create a new job application.

#### `GET /jobs/fetch_emails/` or `POST /jobs/fetch_emails/`
Trigger fetching emails for job applications (runs as a background task).
- **Response:** `{ "task_id": "<celery_task_id>" }`

---

### Fetch Logs

#### `GET /fetch_logs/`
List fetch logs for the authenticated user.

#### `POST /fetch_logs/add_log/`
Add a fetch log for the authenticated user.
- **Body:** `{ "last_fetch_date": "2024-06-01T12:34:56Z" }`
- **Response:** `{ "status": "fetch log added", "id": 123 }`

---

### Task Status

#### `GET /task_status/<task_id>/`
Check the status of a background task.
- **Response:** `{ "status": "PENDING" }` (or `STARTED`, `SUCCESS`, `FAILURE`, etc.)

---

### Notes

- All endpoints (except `/auth/google/login/` and `/auth/google/callback/`) require authentication via JWT in a cookie (`access_token`).
- For CORS, ensure your frontend origin is allowed in the backend settings.

---

Let me know if you want more details or example requests for any endpoint!

## Contributing

Contributions are welcome! Please feel free to open an issue or submit a Pull Request.

## Developing

This part is for me, the main dev who often forget to checkout a new branch before making any changes.

### <code>Main</code> branch
This branch is when you are super sure everything is working well, testing is good, the server is up, API key is hidden, git ignore is set up properly.

ONLY WHEN YOU ASK YOURSELF 100 TIMES THAT YOU ARE SURE THEN YOU CAN PUSH TO THIS BRANCH. Otherwise, please keep it as is (or I will go back in time and eat all the tiramisu in your fridge).

### <code>Dev</code> branch
When you are quite sure, just merge to this and see how things goes.

### <code>feature-name</code> branch
When you want to develop a new feature, check out from dev and create a new branch with that feature name
```sh
git checkout -b feature-name dev
```

After finish developing, merge your branch back to dev
```sh
git checkout dev
git merge --no-ff feature-name
```

When you think everything is good, is okay (Please double check, I beg you). Then you can push to remote dev branch
```sh
git push origin dev
git push origin feature-name
```

That's it. Again, please dont mess with <code>main</code> branch anymore.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

