# Contributing to Automated Job Tracker

Thank you for your interest in contributing!  
We welcome bug reports, feature requests, documentation improvements, and code contributions. This is my first open source project, so if you find anything that can improve (from code to documentation), please feel free to follow the guide below to contribute.

## How to Contribute

1. **Fork the repository**  
   Click the "Fork" button at the top right of this page.

2. **Clone your fork**
   ```sh
   git clone https://github.com/your-username/automated-job-tracker.git
   cd automated-job-tracker
   ```

3. **Create a new branch**
   ```sh
   git checkout -b feature/your-feature-name
   ```

4. **Install dependencies**
   ```sh
   python -m venv venv
   venv\Scripts\activate  # On Windows
   pip install -r requirements.txt
   ```

5. **Make your changes**

6. **Lint and format your code**
   ```sh
   make format
   make lint
   ```

7. **Run tests**
   ```sh
   python manage.py test
   ```

8. **Commit and push**
   ```sh
   git add .
   git commit -m "Describe your change"
   git push origin feature/your-feature-name
   ```

9. **Open a Pull Request**  
   Go to GitHub and open a pull request from your branch.

---

## Code Style

- Follow [PEP8](https://www.python.org/dev/peps/pep-0008/) conventions.
- Use [Black](https://black.readthedocs.io/en/stable/) for formatting.
- Use [isort](https://pycqa.github.io/isort/) for import sorting.
- Lint with [flake8](https://flake8.pycqa.org/).

## Reporting Issues

- Use [GitHub Issues](https://github.com/your-username/automated-job-tracker/issues) to report bugs or request features.
- Please provide as much detail as possible.

## Security

If you discover a security vulnerability, please email the maintainer directly instead of opening a public issue.

---

Thank you for helping make this a better project !!!