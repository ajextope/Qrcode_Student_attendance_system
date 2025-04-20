# QR-Code Attendance Management System - User Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [System Requirements](#system-requirements)
3. [User Roles](#user-roles)
4. [Getting Started](#getting-started)
5. [Admin Guide](#admin-guide)
6. [Lecturer Guide](#lecturer-guide)
7. [Student Guide](#student-guide)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

## Introduction

The QR-Code Attendance Management System is a web-based application designed for Afe Babalola University to streamline the process of tracking student attendance. The system uses QR codes and geolocation verification to ensure accurate attendance records.

### Key Features

- **QR Code Generation**: Lecturers can generate unique QR codes for each class session
- **Geolocation Verification**: Ensures students are physically present in the classroom
- **Role-Based Access**: Different interfaces for administrators, lecturers, and students
- **Comprehensive Reporting**: Detailed attendance reports and statistics
- **Mobile Responsive**: Works on desktop and mobile devices

## System Requirements

### For Users
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection
- Mobile device with camera (for students scanning QR codes)
- Location services enabled on mobile device

### For Administrators
- All of the above
- Access to the university's IT infrastructure

## User Roles

The system supports three user roles, each with different permissions and capabilities:

### Administrator
- Manage users (add, edit, delete)
- Manage courses and locations
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

## Getting Started

### Registration
1. Navigate to the registration page
2. Fill in your personal details
3. Select your user role (Admin, Lecturer, or Student)
4. For students, enter your matric number
5. Create a secure password
6. Submit the form

### Login
1. Navigate to the login page
2. Enter your username and password
3. Click "Login"

### First-time Setup
After logging in for the first time, you should:
1. Complete your profile information
2. Verify your email address (if required)
3. Familiarize yourself with the dashboard

## Admin Guide

### Managing Users
1. Navigate to the Admin Dashboard
2. Click on "Manage Users"
3. From here, you can:
   - View all users
   - Add new users
   - Edit existing users
   - Delete users

### Managing Courses
1. Navigate to the Admin Dashboard
2. Click on "Manage Courses"
3. From here, you can:
   - View all courses
   - Add new courses
   - Assign lecturers to courses
   - Enroll students in courses

### Managing Locations
1. Navigate to the Admin Dashboard
2. Click on "Manage Locations"
3. From here, you can:
   - View all locations
   - Add new locations with geofencing parameters
   - Edit existing locations
   - Delete locations

### Viewing System Statistics
The Admin Dashboard provides an overview of system statistics, including:
- Total number of users by role
- Total number of courses
- Overall attendance rates
- Recent activity

## Lecturer Guide

### Creating a Session
1. Navigate to the Lecturer Dashboard
2. Click on "Manage Sessions"
3. Click "Create New Session"
4. Select the course, location, date, and time
5. Set the session as active
6. Click "Save"

### Generating QR Codes
1. Navigate to the Lecturer Dashboard
2. Click on "Generate QR Code"
3. Select the active session
4. Set the expiration time (in minutes)
5. Click "Generate QR Code"
6. The QR code will be displayed and can be:
   - Shown on a projector for students to scan
   - Downloaded as an image
   - Shared via URL

### Monitoring Attendance
While the QR code is active, you can:
1. See real-time updates of students who have marked attendance
2. View the verification method used (QR code or geolocation)
3. See the total count of students present

### Viewing Attendance Reports
1. Navigate to the Lecturer Dashboard
2. Click on "Attendance Reports"
3. Filter by:
   - Course
   - Date range
4. View attendance statistics and charts
5. Export reports in CSV or PDF format

## Student Guide

### Enrolling in Courses
Students are typically enrolled in courses by administrators or lecturers. If you need to be enrolled in a course, contact your lecturer or the system administrator.

### Marking Attendance
1. Navigate to the Student Dashboard
2. Click on "Scan QR Code"
3. Allow camera access when prompted
4. Point your camera at the QR code displayed by your lecturer
5. The system will:
   - Verify the QR code
   - Check your geolocation
   - Mark your attendance if all verifications pass

### Viewing Your Attendance
1. Navigate to the Student Dashboard
2. Click on "My Attendance"
3. View your attendance records for all courses
4. Filter by:
   - Course
   - Date range
5. See your attendance statistics and trends

## Troubleshooting

### QR Code Scanning Issues
- Ensure your camera is working properly
- Make sure there is adequate lighting
- Hold your device steady
- Ensure the QR code is fully visible in the camera frame

### Geolocation Issues
- Ensure location services are enabled on your device
- Allow the browser to access your location when prompted
- If indoors, try moving closer to a window for better GPS signal
- Ensure you are within the specified radius of the class location

### Login Issues
- Check that you're using the correct username and password
- If you've forgotten your password, use the "Forgot Password" link
- Clear your browser cache and cookies
- Try using a different browser

## FAQ

### Q: How long are QR codes valid?
A: QR codes are valid for the duration set by the lecturer when generating the code, typically 15 minutes.

### Q: What happens if I'm outside the geofence area?
A: If you're outside the specified radius of the class location, your attendance will not be marked, and you'll receive an error message.

### Q: Can I mark attendance for a past session?
A: No, attendance can only be marked for active sessions with valid QR codes.

### Q: How can I improve my attendance rate?
A: Ensure you arrive at class on time and scan the QR code as soon as it's available.

### Q: What if my device doesn't have a camera?
A: Contact your lecturer or administrator for alternative attendance marking methods.

### Q: Can I see who marked me absent?
A: The system only records when you are present. Absences are determined by the lack of an attendance record.

### Q: How secure is the system?
A: The system uses multiple verification methods (QR codes and geolocation) to ensure only students physically present in class can mark attendance.
