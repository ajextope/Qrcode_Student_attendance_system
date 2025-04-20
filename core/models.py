from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

class Course(models.Model):
    # Existing fields...
    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    lecturer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='courses',
        limit_choices_to={'user_type': 'lecturer'}
    )
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='enrolled_courses',
        limit_choices_to={'user_type': 'student'},
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)  # Add this line

    def __str__(self):
        return f"{self.code} - {self.title}"
    
    class Meta:
        ordering = ['code']


class Location(models.Model):
    """
    Model for locations within Afe Babalola University
    """
    name = models.CharField(max_length=100)
    building = models.CharField(max_length=100)
    room_number = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    radius = models.IntegerField(default=50, help_text="Radius in meters for geofencing")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.building} {self.room_number or ''}"
    
    class Meta:
        unique_together = ['building', 'room_number']

class Session(models.Model):
    """
    Model for class sessions
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sessions')
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.course.code} - {self.date} ({self.start_time} to {self.end_time})"
    
    class Meta:
        ordering = ['-date', 'start_time']

class QRCode(models.Model):
    """
    Model for QR codes generated for attendance
    """
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='qrcodes')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"QR Code for {self.session} - Expires: {self.expires_at}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def save(self, *args, **kwargs):
        # Set expiration time to 15 minutes from creation if not specified
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=15)
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']

class Attendance(models.Model):
    """
    Model for tracking student attendance
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='attendances',
        limit_choices_to={'user_type': 'student'}
    )
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='attendances')
    qrcode = models.ForeignKey(QRCode, on_delete=models.SET_NULL, null=True, related_name='attendances')
    timestamp = models.DateTimeField(auto_now_add=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    is_present = models.BooleanField(default=True)
    verification_method = models.CharField(
        max_length=20,
        choices=[
            ('qrcode', 'QR Code'),
            ('manual', 'Manual Entry'),
            ('geolocation', 'Geolocation')
        ],
        default='qrcode'
    )
    
    def __str__(self):
        return f"{self.student.username} - {self.session} - {'Present' if self.is_present else 'Absent'}"
    
    class Meta:
        unique_together = ['student', 'session']
        ordering = ['-timestamp']
