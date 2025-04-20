# QR-Code Attendance Management System

A Django-based attendance management system using QR codes and geolocation verification for Afe Babalola University.

## Features

- QR code generation for class sessions
- Geolocation verification to ensure students are physically present
- Role-based access (Admin, Lecturer, Student)
- Comprehensive attendance reporting and statistics
- Mobile-responsive design with Bootstrap 5

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Run migrations:
   ```
   python manage.py migrate
   ```
6. Create a superuser:
   ```
   python manage.py createsuperuser
   ```
7. Run the development server:
   ```
   python manage.py runserver
   ```
8. Access the application at http://127.0.0.1:8000/

## Project Structure

```
qr_attendance/
├── accounts/                  # User authentication app
│   ├── admin.py              # Admin configuration
│   ├── forms.py              # User forms
│   ├── models.py             # User model
│   ├── urls.py               # Authentication URLs
│   └── views.py              # Authentication views
├── core/                      # Main application
│   ├── admin.py              # Admin configuration
│   ├── attendance_utils.py   # Attendance utilities
│   ├── forms.py              # Core forms
│   ├── location_api.py       # Geolocation API
│   ├── models.py             # Core models
│   ├── tests.py              # Unit tests
│   ├── urls.py               # Core URLs
│   └── views.py              # Core views
├── docs/                      # Documentation
│   └── user_documentation.md # User guide
├── media/                     # User uploaded files
├── static/                    # Static files
│   ├── css/                  # CSS files
│   ├── img/                  # Image files
│   └── js/                   # JavaScript files
├── templates/                 # HTML templates
│   ├── accounts/             # Authentication templates
│   ├── core/                 # Core templates
│   └── base.html             # Base template
├── attendance_system/         # Project settings
│   ├── settings.py           # Django settings
│   ├── urls.py               # Project URLs
│   └── wsgi.py               # WSGI configuration
├── manage.py                  # Django management script
└── requirements.txt           # Project dependencies
```

## User Roles

### Admin
- Manage users, courses, and locations
- View all attendance records
- Generate system-wide reports

### Lecturer
- Create and manage class sessions
- Generate QR codes for attendance
- View attendance records for their courses
- Export attendance reports

### Student
- Scan QR codes to mark attendance
- View their own attendance records
- See attendance statistics for enrolled courses

## License

This project is licensed under the MIT License - see the LICENSE file for details.
