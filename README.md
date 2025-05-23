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

### Fetch Emails
To fetch unread recruiter emails from Gmail, use the custom action in the EmailViewSet:

```sh
curl -X POST http://localhost:8000/emails/fetch_emails/
```

### View Emails
To view the emails, visit the <code> /emails/ </code> endpoint:

```sh
curl http://localhost:8000/emails/
```

### Post a New Email
To post a new email, send a POST request to <code> /emails/ </code>:

```sh
curl -X POST http://localhost:8000/emails/ -d "sender=test@example.com&subject=Job Title: Software Engineer at TechCorp - Application Status: Applied&body=Dear Applicant, We are pleased to inform you that your application for the position of Software Engineer at TechCorp has been received. Your application status is currently Applied.&received_at=2025-02-01T00:00:00Z"
```

### Clear Emails
To clear all email records from the database, use the custom action provided in the <code>EmailViewSet</code>. Send a POST request to <code>/emails/clear/</code>

```sh
curl -X POST http://localhost:8000/emails/clear/
```

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

