# Settlex

Settlex is a Django application for managing settlement statements.

## Prerequisites
- Python 3.10 or later
- [virtualenv](https://virtualenv.pypa.io/) or `venv`

## Setup
1. Clone this repository.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running Tests
Run the Django test suite with:
```bash
python manage.py test
```

## Environment Variables
Create a `.env` file in the project root and define any required environment
variables. At a minimum the application expects a `SECRET_KEY` value:
```bash
SECRET_KEY=your-secret-key
```