import unittest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from core.models import Course, Location, Session, QRCode, Attendance

User = get_user_model()

class UserModelTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='testpassword123',
            user_type='admin'
        )
        
        self.lecturer_user = User.objects.create_user(
            username='lecturer_test',
            email='lecturer@test.com',
            password='testpassword123',
            user_type='lecturer'
        )
        
        self.student_user = User.objects.create_user(
            username='student_test',
            email='student@test.com',
            password='testpassword123',
            user_type='student',
            matric_number='STU/2023/001'
        )
    
    def test_user_creation(self):
        """Test that users are created with correct attributes"""
        self.assertEqual(self.admin_user.user_type, 'admin')
        self.assertEqual(self.lecturer_user.user_type, 'lecturer')
        self.assertEqual(self.student_user.user_type, 'student')
        self.assertEqual(self.student_user.matric_number, 'STU/2023/001')
    
    def test_user_str_representation(self):
        """Test the string representation of User model"""
        self.assertEqual(str(self.admin_user), 'admin_test (Admin)')
        self.assertEqual(str(self.lecturer_user), 'lecturer_test (Lecturer)')
        self.assertEqual(str(self.student_user), 'student_test (Student)')

class CourseModelTest(TestCase):
    def setUp(self):
        self.lecturer = User.objects.create_user(
            username='lecturer_test',
            email='lecturer@test.com',
            password='testpassword123',
            user_type='lecturer'
        )
        
        self.course = Course.objects.create(
            code='CSC101',
            title='Introduction to Computer Science',
            description='Basic concepts of computer science',
            lecturer=self.lecturer
        )
    
    def test_course_creation(self):
        """Test that course is created with correct attributes"""
        self.assertEqual(self.course.code, 'CSC101')
        self.assertEqual(self.course.title, 'Introduction to Computer Science')
        self.assertEqual(self.course.lecturer, self.lecturer)
    
    def test_course_str_representation(self):
        """Test the string representation of Course model"""
        self.assertEqual(str(self.course), 'CSC101 - Introduction to Computer Science')

class LocationModelTest(TestCase):
    def setUp(self):
        self.location = Location.objects.create(
            name='Computer Lab',
            building='Science Block',
            room_number='SB-101',
            latitude=7.6192,
            longitude=5.2527,
            radius=50
        )
    
    def test_location_creation(self):
        """Test that location is created with correct attributes"""
        self.assertEqual(self.location.name, 'Computer Lab')
        self.assertEqual(self.location.building, 'Science Block')
        self.assertEqual(self.location.room_number, 'SB-101')
        self.assertEqual(float(self.location.latitude), 7.6192)
        self.assertEqual(float(self.location.longitude), 5.2527)
        self.assertEqual(self.location.radius, 50)
    
    def test_location_str_representation(self):
        """Test the string representation of Location model"""
        self.assertEqual(str(self.location), 'Computer Lab - Science Block SB-101')

class SessionModelTest(TestCase):
    def setUp(self):
        self.lecturer = User.objects.create_user(
            username='lecturer_test',
            email='lecturer@test.com',
            password='testpassword123',
            user_type='lecturer'
        )
        
        self.course = Course.objects.create(
            code='CSC101',
            title='Introduction to Computer Science',
            lecturer=self.lecturer
        )
        
        self.location = Location.objects.create(
            name='Computer Lab',
            building='Science Block',
            room_number='SB-101',
            latitude=7.6192,
            longitude=5.2527,
            radius=50
        )
        
        self.session = Session.objects.create(
            course=self.course,
            location=self.location,
            date=timezone.now().date(),
            start_time=timezone.now().time(),
            end_time=(timezone.now() + timedelta(hours=2)).time(),
            is_active=True
        )
    
    def test_session_creation(self):
        """Test that session is created with correct attributes"""
        self.assertEqual(self.session.course, self.course)
        self.assertEqual(self.session.location, self.location)
        self.assertTrue(self.session.is_active)
    
    def test_session_str_representation(self):
        """Test the string representation of Session model"""
        expected_str = f"{self.course.code} - {self.session.date} ({self.session.start_time} to {self.session.end_time})"
        self.assertEqual(str(self.session), expected_str)

class QRCodeModelTest(TestCase):
    def setUp(self):
        self.lecturer = User.objects.create_user(
            username='lecturer_test',
            email='lecturer@test.com',
            password='testpassword123',
            user_type='lecturer'
        )
        
        self.course = Course.objects.create(
            code='CSC101',
            title='Introduction to Computer Science',
            lecturer=self.lecturer
        )
        
        self.location = Location.objects.create(
            name='Computer Lab',
            building='Science Block',
            room_number='SB-101',
            latitude=7.6192,
            longitude=5.2527,
            radius=50
        )
        
        self.session = Session.objects.create(
            course=self.course,
            location=self.location,
            date=timezone.now().date(),
            start_time=timezone.now().time(),
            end_time=(timezone.now() + timedelta(hours=2)).time(),
            is_active=True
        )
        
        self.qrcode = QRCode.objects.create(
            session=self.session,
            expires_at=timezone.now() + timedelta(minutes=15)
        )
    
    def test_qrcode_creation(self):
        """Test that QR code is created with correct attributes"""
        self.assertEqual(self.qrcode.session, self.session)
        self.assertIsNotNone(self.qrcode.uuid)
        self.assertTrue(self.qrcode.is_active)
    
    def test_qrcode_expiration(self):
        """Test QR code expiration functionality"""
        # QR code should not be expired yet
        self.assertFalse(self.qrcode.is_expired())
        
        # Set expiration time to the past
        self.qrcode.expires_at = timezone.now() - timedelta(minutes=1)
        self.qrcode.save()
        
        # QR code should now be expired
        self.assertTrue(self.qrcode.is_expired())

class AttendanceModelTest(TestCase):
    def setUp(self):
        self.lecturer = User.objects.create_user(
            username='lecturer_test',
            email='lecturer@test.com',
            password='testpassword123',
            user_type='lecturer'
        )
        
        self.student = User.objects.create_user(
            username='student_test',
            email='student@test.com',
            password='testpassword123',
            user_type='student',
            matric_number='STU/2023/001'
        )
        
        self.course = Course.objects.create(
            code='CSC101',
            title='Introduction to Computer Science',
            lecturer=self.lecturer
        )
        
        # Add student to course
        self.course.students.add(self.student)
        
        self.location = Location.objects.create(
            name='Computer Lab',
            building='Science Block',
            room_number='SB-101',
            latitude=7.6192,
            longitude=5.2527,
            radius=50
        )
        
        self.session = Session.objects.create(
            course=self.course,
            location=self.location,
            date=timezone.now().date(),
            start_time=timezone.now().time(),
            end_time=(timezone.now() + timedelta(hours=2)).time(),
            is_active=True
        )
        
        self.qrcode = QRCode.objects.create(
            session=self.session,
            expires_at=timezone.now() + timedelta(minutes=15)
        )
        
        self.attendance = Attendance.objects.create(
            student=self.student,
            session=self.session,
            qrcode=self.qrcode,
            verification_method='qrcode',
            is_present=True,
            latitude=7.6192,
            longitude=5.2527
        )
    
    def test_attendance_creation(self):
        """Test that attendance record is created with correct attributes"""
        self.assertEqual(self.attendance.student, self.student)
        self.assertEqual(self.attendance.session, self.session)
        self.assertEqual(self.attendance.qrcode, self.qrcode)
        self.assertEqual(self.attendance.verification_method, 'qrcode')
        self.assertTrue(self.attendance.is_present)
        self.assertEqual(float(self.attendance.latitude), 7.6192)
        self.assertEqual(float(self.attendance.longitude), 5.2527)
    
    def test_attendance_str_representation(self):
        """Test the string representation of Attendance model"""
        expected_str = f"{self.student.username} - {self.session} - Present"
        self.assertEqual(str(self.attendance), expected_str)

class AuthViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'User',
            'user_type': 'student',
            'matric_number': 'STU/2023/002'
        }
        
        self.user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='existingpassword123',
            user_type='student'
        )
    
    def test_register_view_get(self):
        """Test that register view returns correct response for GET request"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
    
    def test_login_view_get(self):
        """Test that login view returns correct response for GET request"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
    
    def test_login_success(self):
        """Test successful login"""
        response = self.client.post(self.login_url, {
            'username': 'existinguser',
            'password': 'existingpassword123'
        })
        self.assertRedirects(response, reverse('student_dashboard'))
    
    def test_login_failure(self):
        """Test login with invalid credentials"""
        response = self.client.post(self.login_url, {
            'username': 'existinguser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
    
    def test_logout(self):
        """Test logout functionality"""
        # Login first
        self.client.login(username='existinguser', password='existingpassword123')
        
        # Then logout
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, reverse('login'))
        
        # Check that user is logged out
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")

if __name__ == '__main__':
    unittest.main()
