from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Avg, F, Q
import csv
import json
from datetime import datetime, timedelta
from .models import Attendance, Course, Session
import io
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

@login_required
def export_attendance(request):
    """
    View for exporting attendance data in CSV or PDF format
    """
    # Get filter parameters
    format_type = request.GET.get('format', 'csv')
    course_id = request.GET.get('course')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Base queryset
    user = request.user
    if user.user_type == 'lecturer':
        # Lecturers can only export attendance for their courses
        attendances = Attendance.objects.filter(session__course__lecturer=user)
    elif user.user_type == 'student':
        # Students can only export their own attendance
        attendances = Attendance.objects.filter(student=user)
    elif user.user_type == 'admin':
        # Admins can export all attendance records
        attendances = Attendance.objects.all()
    else:
        return HttpResponse("Permission denied", status=403)
    
    # Apply filters
    if course_id:
        attendances = attendances.filter(session__course_id=course_id)
    
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            attendances = attendances.filter(session__date__gte=date_from)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            attendances = attendances.filter(session__date__lte=date_to)
        except ValueError:
            pass
    
    # Order by date
    attendances = attendances.order_by('session__date', 'session__start_time', 'student__username')
    
    # Generate appropriate response based on format
    if format_type == 'csv':
        return export_csv(attendances, user.user_type)
    elif format_type == 'pdf':
        return export_pdf(attendances, user.user_type)
    else:
        return HttpResponse("Unsupported format", status=400)

def export_csv(attendances, user_type):
    """
    Export attendance data as CSV
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attendance_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    
    # Write header row based on user type
    if user_type == 'student':
        writer.writerow(['Course', 'Date', 'Time', 'Status', 'Verification Method'])
    else:
        writer.writerow(['Student', 'Course', 'Date', 'Time', 'Status', 'Verification Method'])
    
    # Write data rows
    for attendance in attendances:
        status = 'Present' if attendance.is_present else 'Absent'
        verification = attendance.get_verification_method_display()
        
        if user_type == 'student':
            writer.writerow([
                f"{attendance.session.course.code} - {attendance.session.course.title}",
                attendance.session.date,
                attendance.timestamp.strftime('%H:%M:%S'),
                status,
                verification
            ])
        else:
            writer.writerow([
                f"{attendance.student.get_full_name()} ({attendance.student.username})",
                f"{attendance.session.course.code} - {attendance.session.course.title}",
                attendance.session.date,
                attendance.timestamp.strftime('%H:%M:%S'),
                status,
                verification
            ])
    
    return response

def export_pdf(attendances, user_type):
    """
    Export attendance data as PDF
    """
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="attendance_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    
    # Create PDF document
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Add title
    styles = getSampleStyleSheet()
    elements.append(Paragraph("Attendance Report", styles['Title']))
    elements.append(Paragraph(f"Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Prepare data for table
    data = []
    
    # Add header row based on user type
    if user_type == 'student':
        data.append(['Course', 'Date', 'Time', 'Status', 'Verification Method'])
    else:
        data.append(['Student', 'Course', 'Date', 'Time', 'Status', 'Verification Method'])
    
    # Add data rows
    for attendance in attendances:
        status = 'Present' if attendance.is_present else 'Absent'
        verification = attendance.get_verification_method_display()
        
        if user_type == 'student':
            data.append([
                f"{attendance.session.course.code} - {attendance.session.course.title}",
                str(attendance.session.date),
                attendance.timestamp.strftime('%H:%M:%S'),
                status,
                verification
            ])
        else:
            data.append([
                f"{attendance.student.get_full_name()} ({attendance.student.username})",
                f"{attendance.session.course.code} - {attendance.session.course.title}",
                str(attendance.session.date),
                attendance.timestamp.strftime('%H:%M:%S'),
                status,
                verification
            ])
    
    # Create table
    table = Table(data)
    
    # Style the table
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])
    
    # Add alternating row colors
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.add('BACKGROUND', (0, i), (-1, i), colors.lightgrey)
    
    table.setStyle(style)
    elements.append(table)
    
    # Add statistics if there are records
    if attendances:
        elements.append(Spacer(1, 24))
        elements.append(Paragraph("Attendance Statistics", styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        # Calculate statistics
        total_sessions = attendances.values('session').distinct().count()
        present_count = attendances.filter(is_present=True).count()
        total_count = attendances.count()
        attendance_rate = (present_count / total_count * 100) if total_count > 0 else 0
        
        # Add statistics table
        stats_data = [
            ['Total Sessions', str(total_sessions)],
            ['Present Count', str(present_count)],
            ['Total Records', str(total_count)],
            ['Attendance Rate', f"{attendance_rate:.1f}%"]
        ]
        
        stats_table = Table(stats_data, colWidths=[200, 100])
        stats_style = TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ])
        stats_table.setStyle(stats_style)
        elements.append(stats_table)
    
    # Build PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    
    response.write(pdf)
    return response

def get_attendance_statistics(user, course_id=None, date_from=None, date_to=None):
    """
    Calculate attendance statistics for charts and summaries
    """
    # Base queryset for sessions
    if user.user_type == 'lecturer':
        sessions = Session.objects.filter(course__lecturer=user)
    elif user.user_type == 'student':
        sessions = Session.objects.filter(course__students=user)
    elif user.user_type == 'admin':
        sessions = Session.objects.all()
    else:
        return None
    
    # Apply filters
    if course_id:
        sessions = sessions.filter(course_id=course_id)
    
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            sessions = sessions.filter(date__gte=date_from)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            sessions = sessions.filter(date__lte=date_to)
        except ValueError:
            pass
    
    # Get attendance data
    if user.user_type == 'student':
        # For students, get their own attendance
        attendances = Attendance.objects.filter(
            student=user,
            session__in=sessions
        )
        
        # Calculate attendance rate
        total_sessions = sessions.count()
        attended_sessions = attendances.filter(is_present=True).count()
        attendance_rate = (attended_sessions / total_sessions * 100) if total_sessions > 0 else 0
        
        # Get course breakdown
        course_stats = []
        for course in user.enrolled_courses.all():
            course_sessions = sessions.filter(course=course)
            course_total = course_sessions.count()
            if course_total > 0:
                course_attended = attendances.filter(
                    session__course=course,
                    is_present=True
                ).count()
                course_rate = (course_attended / course_total * 100)
                course_stats.append({
                    'code': course.code,
                    'title': course.title,
                    'attendance_rate': course_rate
                })
        
        # Get chart data (attendance over time)
        chart_data = []
        chart_labels = []
        
        # Group by date
        dates = sessions.values('date').distinct().order_by('date')
        for date_obj in dates:
            date = date_obj['date']
            day_sessions = sessions.filter(date=date)
            day_total = day_sessions.count()
            if day_total > 0:
                day_attended = attendances.filter(
                    session__date=date,
                    is_present=True
                ).count()
                attendance_value = day_attended / day_total
                chart_data.append(attendance_value)
                chart_labels.append(date.strftime('%Y-%m-%d'))
        
        return {
            'attendance_rate': attendance_rate,
            'total_sessions': total_sessions,
            'course_stats': course_stats,
            'chart_data': json.dumps(chart_data),
            'chart_labels': json.dumps(chart_labels)
        }
    
    else:
        # For lecturers and admins, get attendance for all students
        attendances = Attendance.objects.filter(session__in=sessions)
        
        # Calculate overall attendance rate
        total_records = attendances.count()
        present_records = attendances.filter(is_present=True).count()
        attendance_rate = (present_records / total_records * 100) if total_records > 0 else 0
        
        # Get chart data (attendance count by date)
        chart_data = []
        chart_labels = []
        
        # Group by date
        dates = sessions.values('date').distinct().order_by('date')
        for date_obj in dates:
            date = date_obj['date']
            count = attendances.filter(
                session__date=date,
                is_present=True
            ).count()
            chart_data.append(count)
            chart_labels.append(date.strftime('%Y-%m-%d'))
        
        return {
            'attendance_rate': attendance_rate,
            'total_sessions': sessions.count(),
            'total_records': total_records,
            'present_records': present_records,
            'chart_data': json.dumps(chart_data),
            'chart_labels': json.dumps(chart_labels)
        }
