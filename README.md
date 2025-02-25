# Automated Job Tracker

The Automated Job Tracker is a Django-based application designed to help users track your job applications automatically by fetching and processing emails from your Gmail account. The application extracts job application data such as job title, company name, and application status from the emails and stores them in a database for easy tracking and management.


## Features

- Fetch unread recruiter emails from Gmail
- Extract job application data (job title, company name, application status) from emails
- Store and manage job application data in a database
- View and edit job application data through a REST API
- Clear email records from the database

## Requirements

- Python 3.8+
- Django 3.2+
- Google API Client Library for Python
- Django REST Framework

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/yourusername/automated-job-tracker.git
   cd automated-job-tracker
   ```

2. Create and activate a virtual environment:

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

4. Set up the Google API credentials:
    - Create a project in the [Google Cloud Console](https://www.google.com/aclk?sa=l&ai=DChcSEwjBio_0rt-LAxU_C6IDHafUFa0YABAAGgJsZQ&co=1&ase=2&gclid=Cj0KCQiA8fW9BhC8ARIsACwHqYq6zTyYIjymWpMaCdTwqhfP_QxG0Vc1w3yyDaxFvmjh9GZpSfpRvxgaAuiaEALw_wcB&sig=AOD64_0ShgNbLJwPBwbC0d634erjqvj_9A&q&nis=4&adurl&ved=2ahUKEwiB84f0rt-LAxWyIBAIHWr6EKkQ0Qx6BAgIEAE).
    - Enable the Gmail API for the project
    - Create OAuth 2.0 credentials and download the JSON file.
    - Save the JSON file as credentials.json in the project root directory.

5. Run the Django migrations:
    ```sh
    python manage.py makemigrations
    python manage.py migrate
    ```

6. Create a superuser for the Django admin interface:
    ```sh
    python manage.py createsuperuser
    ```

7. Start the Django development server:
    ```sh
    python manage.py runserver
    ```

8. Access the application:
    - Open your web browser and navigate to http://127.0.0.1:8000/admin/ to access the Django admin interface.
    - Log in with the superuser account you created.

## Usage

### Fetch email
To fetch unread recruiter emails from Gmail, you can use the custom action provided in the EmailViewSet. Send a POST request to <code> /emails/fetch_emails/ </code>:

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

### Contributing

Contributions are welcome! Please feel free to open an issue or submit a Pull Request.

### License
This project is licensed under the MIT License. See the LICENSE file for more details.


