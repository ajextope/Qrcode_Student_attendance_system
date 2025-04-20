from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from .models import Course, Session, QRCode, Attendance, Location
from .forms import QRCodeGenerationForm, SessionForm
import qrcode
from io import BytesIO
import base64
from datetime import timedelta
import datetime
import uuid
import json
from core.view_management import user_management, course_management,get_available_students, get_enrolled_students, add_students_to_course, remove_students_from_course, location_management, session_management

def home(request):
    """
    Home page view
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/home.html')

@login_required
def course_list(request):
    """
    View for listing courses
    """
    user = request.user
    if user.user_type == 'lecturer':
        courses = Course.objects.filter(lecturer=user)
    elif user.user_type == 'student':
        courses = user.enrolled_courses.all()
    elif user.user_type == 'admin':
        courses = Course.objects.all()
    else:
        courses = []
    
    return render(request, 'core/course_list.html', {'courses': courses})

@login_required
def generate_qrcode(request):
    """
    View for generating QR codes
    """
    # Check if user is a lecturer
    if request.user.user_type != 'lecturer':
        messages.error(request, "Only lecturers can generate QR codes.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = QRCodeGenerationForm(request.POST, user=request.user)
        if form.is_valid():
            session = form.cleaned_data['session']
            expiration_minutes = form.cleaned_data['expiration_minutes']
            
            # Create QR code
            qr_code = QRCode(
                session=session,
                expires_at=timezone.now() + timedelta(minutes=expiration_minutes)
            )
            qr_code.save()
            
            # Generate QR code URL
            qr_url = request.build_absolute_uri(
                reverse('scan_qrcode') + f'?code={qr_code.uuid}'
            )
            
            # Generate QR code image
            img = qrcode.make(qr_url)
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return render(request, 'core/qrcode_display.html', {
                'qr_code': qr_code,
                'qr_image': img_str,
                'qr_url': qr_url
            })
    else:
        form = QRCodeGenerationForm(user=request.user)
    
    # Get lecturer's sessions
    sessions = Session.objects.filter(
        course__lecturer=request.user,
        is_active=True
    ).order_by('date', 'start_time')
    
    return render(request, 'core/generate_qrcode.html', {
        'form': form,
        'sessions': sessions
    })

@login_required
def scan_qrcode(request):
    """
    View for scanning QR codes
    """
    # Check if user is a student
    if request.user.user_type != 'student':
        messages.error(request, "Only students can scan QR codes for attendance.")
        return redirect('dashboard')
    
    code = request.GET.get('code')
    
    if code:
        try:
            # Try to get the QR code by UUID
            qr_code = QRCode.objects.get(uuid=code)
            
            # Check if QR code is expired
            if qr_code.is_expired():
                return render(request, 'core/scan_qrcode.html', {
                    'error': 'This QR code has expired.'
                })
            
            # Check if student is enrolled in the course
            session = qr_code.session
            course = session.course
            if request.user not in course.students.all():
                return render(request, 'core/scan_qrcode.html', {
                    'error': 'You are not enrolled in this course.'
                })
            
            # Check if attendance already exists
            attendance, created = Attendance.objects.get_or_create(
                student=request.user,
                session=session,
                defaults={
                    'qrcode': qr_code,
                    'verification_method': 'qrcode',
                    'is_present': True
                }
            )
            
            if not created:
                return render(request, 'core/scan_qrcode.html', {
                    'error': 'You have already marked your attendance for this session.'
                })
            
            return render(request, 'core/scan_qrcode.html', {
                'success': True,
                'session': session,
                'course': course
            })
            
        except QRCode.DoesNotExist:
            return render(request, 'core/scan_qrcode.html', {
                'error': 'Invalid QR code.'
            })
    
    return render(request, 'core/scan_qrcode.html')

@login_required
def attendance_list(request):
    """
    View for listing attendance records
    """
    from django.core.paginator import Paginator
    from .attendance_utils import get_attendance_statistics
    
    user = request.user
    
    # Get filter parameters
    course_id = request.GET.get('course')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if user.user_type == 'student':
        # Students can only see their own attendance
        attendances = Attendance.objects.filter(student=user).order_by('-session__date', '-timestamp')
        
        # Apply filters
        if course_id:
            attendances = attendances.filter(session__course_id=course_id)
        
        if date_from:
            try:
                date_from_obj = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
                attendances = attendances.filter(session__date__gte=date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()
                attendances = attendances.filter(session__date__lte=date_to_obj)
            except ValueError:
                pass
        
        # Paginate results
        paginator = Paginator(attendances, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Get statistics
        stats = get_attendance_statistics(user, course_id, date_from, date_to)
        
        context = {
            'attendances': page_obj,
            'is_paginated': True,
            'page_obj': page_obj,
            'enrolled_courses': user.enrolled_courses.all(),
            'selected_course': course_id,
            'date_from': date_from,
            'date_to': date_to
        }
        
        # Add statistics to context
        if stats:
            context.update(stats)
        
        return render(request, 'core/student_attendance.html', context)
    
    elif user.user_type == 'lecturer':
        # Lecturers can see attendance for their courses
        courses = Course.objects.filter(lecturer=user)
        
        # Get session_id from query params
        session_id = request.GET.get('session')
        if session_id:
            try:
                session = Session.objects.get(id=session_id, course__lecturer=user)
                attendances = Attendance.objects.filter(session=session).order_by('student__last_name')
                
                # Paginate results
                paginator = Paginator(attendances, 20)
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)
                
                return render(request, 'core/session_attendance.html', {
                    'session': session,
                    'attendances': page_obj,
                    'is_paginated': True,
                    'page_obj': page_obj
                })
            except Session.DoesNotExist:
                messages.error(request, "Session not found or you don't have permission to view it.")
        
        # Get all attendance records for lecturer's courses
        attendances = Attendance.objects.filter(session__course__lecturer=user).order_by('-session__date', '-timestamp')
        
        # Apply filters
        if course_id:
            attendances = attendances.filter(session__course_id=course_id)
        
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                attendances = attendances.filter(session__date__gte=date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                attendances = attendances.filter(session__date__lte=date_to_obj)
            except ValueError:
                pass
        
        # Paginate results
        paginator = Paginator(attendances, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Get statistics
        stats = get_attendance_statistics(user, course_id, date_from, date_to)
        
        context = {
            'attendances': page_obj,
            'is_paginated': True,
            'page_obj': page_obj,
            'courses': courses,
            'selected_course': course_id,
            'date_from': date_from,
            'date_to': date_to
        }
        
        # Add statistics to context
        if stats:
            context.update(stats)
        
        return render(request, 'core/lecturer_attendance.html', context)
    
    elif user.user_type == 'admin':
        # Admins can see all attendance records
        courses = Course.objects.all()
        
        # Get session_id from query params
        session_id = request.GET.get('session')
        if session_id:
            try:
                session = Session.objects.get(id=session_id)
                attendances = Attendance.objects.filter(session=session).order_by('student__last_name')
                
                # Paginate results
                paginator = Paginator(attendances, 20)
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)
                
                return render(request, 'core/session_attendance.html', {
                    'session': session,
                    'attendances': page_obj,
                    'is_paginated': True,
                    'page_obj': page_obj
                })
            except Session.DoesNotExist:
                messages.error(request, "Session not found.")
        
        # Get all attendance records
        attendances = Attendance.objects.all().order_by('-session__date', '-timestamp')
        
        # Apply filters
        if course_id:
            attendances = attendances.filter(session__course_id=course_id)
        
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                attendances = attendances.filter(session__date__gte=date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                attendances = attendances.filter(session__date__lte=date_to_obj)
            except ValueError:
                pass
        
        # Paginate results
        paginator = Paginator(attendances, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Get statistics
        stats = get_attendance_statistics(user, course_id, date_from, date_to)
        
        context = {
            'attendances': page_obj,
            'is_paginated': True,
            'page_obj': page_obj,
            'courses': courses,
            'selected_course': course_id,
            'date_from': date_from,
            'date_to': date_to
        }
        
        # Add statistics to context
        if stats:
            context.update(stats)
        
        return render(request, 'core/lecturer_attendance.html', context)
    
    # Redirect other user types
    return redirect('dashboard')


@login_required
def check_qrcode_status(request, qrcode_id):
    """
    AJAX view to check QR code status
    """
    try:
        qr_code = QRCode.objects.get(id=qrcode_id)
        
        # Check if user has permission to view this QR code
        if request.user.user_type == 'lecturer' and qr_code.session.course.lecturer != request.user:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        # Get attendance count
        attendance_count = Attendance.objects.filter(qrcode=qr_code).count()
        
        return JsonResponse({
            'is_expired': qr_code.is_expired(),
            'expires_at': qr_code.expires_at.isoformat(),
            'attendance_count': attendance_count
        })
    except QRCode.DoesNotExist:
        return JsonResponse({'error': 'QR code not found'}, status=404)

@login_required
def enrolled_courses(request):
    """
    View for displaying enrolled courses and class schedules for the logged-in student.
    """
    # Get the current student from the request
    student = request.user  # Assuming the user is a student

    # Fetch courses for the student using the correct field name
    courses = Course.objects.filter(students=student)

    # Prepare context data
    context = {
        'courses': courses,
    }

    # Render the template with the context
    return render(request, 'core/enrolled_courses.html', context)