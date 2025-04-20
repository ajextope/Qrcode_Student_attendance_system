from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from core.models import Course, Location ,Session # Adjust the import based on your Course model location
from accounts.models import User  # Adjust the import based on your User model location
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils import timezone
from datetime import datetime, timedelta


@login_required
def user_management(request):
    """
    View for managing users, including listing, filtering, and CRUD operations.
    """
    # Handle filtering and searching
    user_type = request.GET.get('user_type', '')
    search_query = request.GET.get('search', '')

    # Filter users based on user type and search query
    users = User.objects.all()
    if user_type:
        users = users.filter(user_type=user_type)
    if search_query:
        users = users.filter(
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query) | 
            Q(email__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(users, 10)  # Show 10 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # User statistics
    total_users = User.objects.count()
    admin_count = User.objects.filter(user_type='admin').count()
    lecturer_count = User.objects.filter(user_type='lecturer').count()
    student_count = User.objects.filter(user_type='student').count()

    context = {
        'users': page_obj,
        'total_users': total_users,
        'admin_count': admin_count,
        'lecturer_count': lecturer_count,
        'student_count': student_count,
        'selected_type': user_type,
        'search_query': search_query,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }

    # Handle user creation, editing, and deletion
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            # Create a new user
            username = request.POST.get('username')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            user_type = request.POST.get('user_type')
            password = request.POST.get('password')
            is_active = request.POST.get('is_active') == 'on'

            user = User(
                username=username,
                # Ensure username is unique
                
                first_name=first_name,
                last_name=last_name,
                email=email,
                user_type=user_type,
                is_active=is_active
            )
            user.set_password(password)
            user.save()
            messages.success(request, "User created successfully.")
            return redirect('user_management')

        elif action == 'update':
            # Update an existing user
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, id=user_id)
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email')
            user.user_type = request.POST.get('user_type')
            user.is_active = request.POST.get('is_active') == 'on'
            
            # Update password if provided
            password = request.POST.get('password')
            if password:
                user.set_password(password)
            
            user.save()
            messages.success(request, "User updated successfully.")
            return redirect('user_management')

        elif action == 'delete':
            # Delete a user
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, id=user_id)
            user.delete()
            messages.success(request, "User deleted successfully.")
            return redirect('user_management')

    return render(request, 'accounts/management/user_management.html', context)

@login_required
def course_management(request):
    """
    View for managing courses, including listing, filtering, and CRUD operations.
    """
    # Handle filtering and searching
    selected_lecturer = request.GET.get('lecturer', '')
    search_query = request.GET.get('search', '')

    # Filter courses based on lecturer and search query
    courses = Course.objects.all()
    if selected_lecturer:
        courses = courses.filter(lecturer_id=selected_lecturer)
    if search_query:
        courses = courses.filter(
            Q(code__icontains=search_query) | 
            Q(title__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(courses, 10)  # Show 10 courses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get all lecturers for the filter
    lecturers = User.objects.filter(user_type='lecturer')

    # Course statistics
    total_courses = Course.objects.count()
    active_courses = Course.objects.filter(is_active=True).count()
    total_enrollments = sum(course.students.count() for course in courses)

    context = {
        'courses': page_obj,
        'lecturers': lecturers,
        'total_courses': total_courses,
        'active_courses': active_courses,
        'total_enrollments': total_enrollments,
        'selected_lecturer': selected_lecturer,
        'search_query': search_query,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }

    # Handle course creation, updating, and deletion
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            # Create a new course
            code = request.POST.get('code')
            title = request.POST.get('title')
            description = request.POST.get('description')
            lecturer_id = request.POST.get('lecturer_id')
            is_active = request.POST.get('is_active') == 'on'

            course = Course(
                code=code,
                title=title,
                description=description,
                lecturer_id=lecturer_id,
                is_active=is_active
            )
            course.save()
            messages.success(request, "Course created successfully.")
            return redirect('course_management')

        elif action == 'update':
            # Update an existing course
            course_id = request.POST.get('course_id')
            course = get_object_or_404(Course, id=course_id)
            course.code = request.POST.get('code')
            course.title = request.POST.get('title')
            course.description = request.POST.get('description')
            course.lecturer_id = request.POST.get('lecturer_id')
            course.is_active = request.POST.get('is_active') == 'on'
            course.save()
            messages.success(request, "Course updated successfully.")
            return redirect('course_management')

        elif action == 'delete':
            # Delete a course
            course_id = request.POST.get('course_id')
            course = get_object_or_404(Course, id=course_id)
            course.delete()
            messages.success(request, "Course deleted successfully.")
            return redirect('course_management')
        elif action == 'update_students':
            enrolled_students_ids = request.POST.getlist('enrolled_students_ids[]')  # Get the list of student IDs
            course_id = request.POST.get('course_id')
            print(f'Enrolled Students IDs Received: {enrolled_students_ids}') 
            if not course_id:
                messages.error(request, 'Course ID is required.')
                return redirect('course_management')  # Redirect if course_id is missing

            course = get_object_or_404(Course, id=course_id)
            course.students.clear()  # Clear all enrolled students

            try:
                # Convert IDs to integers and filter users
                enrolled_students_ids = [int(student_id) for student_id in enrolled_students_ids if student_id.isdigit()]
                
                # Fetch users to add
                users_to_add = User.objects.filter(id__in=enrolled_students_ids)
                print(f'Users to be added: {[user.id for user in users_to_add]}')  # Log user IDs
                print(f'Count of Users to Add: {users_to_add.count()}')  # Log count
                
                # Add selected students
                if users_to_add.exists():
                    course.students.add(*users_to_add)
                    print('Students added successfully.')
                else:
                    print('No valid users to add.')

                # Refresh the course instance
                course.refresh_from_db()  # Refresh the course instance
                print(f'Enrolled Students Count: {course.students.count()}')  # Check count again

            except Exception as e:
                messages.error(request, f'An error occurred while updating students: {e}')
                return redirect('course_management')

            messages.success(request, 'Students updated successfully.')
            return redirect('course_management')  # Redirect after processing


    return render(request, 'core/management/course_management.html', context)


User = get_user_model()

def get_available_students(request, course_id):
    """
    API view to get all students who are not enrolled in the specified course.
    """
    course = get_object_or_404(Course, id=course_id)
    enrolled_students = course.students.all()
    
    # Get all students not enrolled in the course
    available_students = User.objects.exclude(id__in=enrolled_students.values_list('id', flat=True)).filter(user_type='student')

    student_data = [{'id': student.id, 'name': student.get_full_name()} for student in available_students]
    
    return JsonResponse({'students': student_data})

def get_enrolled_students(request, course_id):
    """
    API view to get all students enrolled in the specified course.
    """
    course = get_object_or_404(Course, id=course_id)
    enrolled_students = course.students.all()
    
    student_data = [{'id': student.id, 'name': student.get_full_name()} for student in enrolled_students]
    
    return JsonResponse({'students': student_data})

def add_students_to_course(request):
    """
    API view to add selected students to a course.
    """
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        student_ids = request.POST.getlist('student_ids[]')
        
        course = get_object_or_404(Course, id=course_id)
        students = User.objects.filter(id__in=student_ids)
        
        course.students.add(*students)  # Add students to the course
        return JsonResponse({'success': True, 'message': 'Students added successfully.'})

def remove_students_from_course(request):
    """
    API view to remove selected students from a course.
    """
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        student_ids = request.POST.getlist('student_ids[]')
        
        course = get_object_or_404(Course, id=course_id)
        students = User.objects.filter(id__in=student_ids)
        
        course.students.remove(*students)  # Remove students from the course
        return JsonResponse({'success': True, 'message': 'Students removed successfully.'})


# Note: Ensure that the URLs for these views are properly configured in your Django app's urls.py file.
def location_management(request):
    # Get filter parameters
    status = request.GET.get('status')
    search_query = request.GET.get('search', '')

    # Base queryset
    locations = Location.objects.all()

    # Apply filters
    if status:
        if status == 'active':
            locations = locations.filter(is_active=True)
        elif status == 'inactive':
            locations = locations.filter(is_active=False)

    if search_query:
        locations = locations.filter(Q(name__icontains=search_query))

    # Pagination
    paginator = Paginator(locations, 10)  # Show 10 locations per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Context data
    context = {
        'locations': page_obj,
        'total_locations': locations.count(),
        'active_locations': locations.filter(is_active=True).count(),
        'total_sessions': 0,  # Replace with actual session count if applicable
        'status': status,
        'search_query': search_query,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }

    # Handle form submissions for create, update, delete
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            # Create a new location
            Location.objects.create(
                name=request.POST['name'],
                latitude=request.POST['latitude'],
                longitude=request.POST['longitude'],
                radius=request.POST['radius'],
                is_active='is_active' in request.POST
            )
            return redirect('location_management')

        elif action == 'update':
            # Update an existing location
            location_id = request.POST['location_id']
            location = Location.objects.get(id=location_id)
            location.name = request.POST['name']
            location.latitude = request.POST['latitude']
            location.longitude = request.POST['longitude']
            location.radius = request.POST['radius']
            location.is_active = 'is_active' in request.POST
            location.save()
            return redirect('location_management')

        elif action == 'delete':
            # Delete a location
            location_id = request.POST['location_id']
            Location.objects.filter(id=location_id).delete()
            return redirect('location_management')

    return render(request, 'core/management/location_management.html', context)

    #session  management

@login_required
def session_management(request):
    # Get all filter parameters from the request
    selected_course = request.GET.get('course', '')
    selected_location = request.GET.get('location', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    status = request.GET.get('status', '')
    
    # Get all courses taught by the current lecturer or all courses if admin
    if request.user.user_type == 'lecturer':
        courses = Course.objects.filter(lecturer=request.user, is_active=True)
    else:
        courses = Course.objects.filter(is_active=True)
    
    # Get all active locations
    locations = Location.objects.filter(is_active=True)
    
    # Start with base queryset
    sessions = Session.objects.select_related('course', 'location').annotate(
        attendance_count=Count('attendances')
    )
    
    # Apply filters
    if selected_course:
        sessions = sessions.filter(course_id=selected_course)
    if selected_location:
        sessions = sessions.filter(location_id=selected_location)
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            sessions = sessions.filter(date__gte=date_from_obj)
        except ValueError:
            pass
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            sessions = sessions.filter(date__lte=date_to_obj)
        except ValueError:
            pass
    
    # Apply status filter
    today = timezone.now().date()
    now = timezone.now().time()
    
    if status == 'active':
        sessions = sessions.filter(is_active=True)
    elif status == 'inactive':
        sessions = sessions.filter(is_active=False)
    elif status == 'upcoming':
        sessions = sessions.filter(
            is_active=True,
            date__gt=today
        ).filter(
            Q(date=today, start_time__gt=now) | Q(date__gt=today))
    elif status == 'past':
        sessions = sessions.filter(
            Q(date__lt=today) | Q(date=today, end_time__lt=now)
        )
    
    # Order sessions by date and time
    sessions = sessions.order_by('-date', 'start_time')
    
    # Pagination
    paginator = Paginator(sessions, 25)  # Show 25 sessions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Handle POST requests (create, update, delete)
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            # Handle session creation
            course_id = request.POST.get('course_id')
            location_id = request.POST.get('location_id')
            date = request.POST.get('date')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            is_active = request.POST.get('is_active') == 'on'
            recurring = request.POST.get('recurring') == 'on'
            
            try:
                course = Course.objects.get(id=course_id)
                location = Location.objects.get(id=location_id)
                
                # Validate date and times
                date_obj = datetime.strptime(date, '%Y-%m-%d').date()
                start_time_obj = datetime.strptime(start_time, '%H:%M').time()
                end_time_obj = datetime.strptime(end_time, '%H:%M').time()
                
                if end_time_obj <= start_time_obj:
                    messages.error(request, 'End time must be after start time.')
                    return redirect('session_management')
                
                if recurring:
                    # Handle recurring sessions
                    repeat_until = request.POST.get('repeat_until')
                    weekdays = request.POST.getlist('weekdays')
                    
                    if not weekdays:
                        messages.error(request, 'Please select at least one weekday for recurring sessions.')
                        return redirect('session_management')
                    
                    repeat_until_obj = datetime.strptime(repeat_until, '%Y-%m-%d').date()
                    
                    current_date = date_obj
                    created_count = 0
                    
                    while current_date <= repeat_until_obj:
                        weekday = str(current_date.weekday())
                        if weekday in weekdays:
                            # Create session for this date
                            Session.objects.create(
                                course=course,
                                location=location,
                                date=current_date,
                                start_time=start_time_obj,
                                end_time=end_time_obj,
                                is_active=is_active
                            )
                            created_count += 1
                        
                        current_date += timedelta(days=1)
                    
                    messages.success(request, f'Successfully created {created_count} recurring sessions.')
                else:
                    # Create single session
                    session = Session.objects.create(
                        course=course,
                        location=location,
                        date=date_obj,
                        start_time=start_time_obj,
                        end_time=end_time_obj,
                        is_active=is_active
                    )
                    messages.success(request, 'Session created successfully.')
                
            except (Course.DoesNotExist, Location.DoesNotExist):
                messages.error(request, 'Invalid course or location selected.')
            except ValueError:
                messages.error(request, 'Invalid date or time format.')
        
        elif action == 'update':
            # Handle session update
            session_id = request.POST.get('session_id')
            course_id = request.POST.get('course_id')
            location_id = request.POST.get('location_id')
            date = request.POST.get('date')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            is_active = request.POST.get('is_active') == 'on'
            
            try:
                session = Session.objects.get(id=session_id)
                course = Course.objects.get(id=course_id)
                location = Location.objects.get(id=location_id)
                
                # Validate date and times
                date_obj = datetime.strptime(date, '%Y-%m-%d').date()
                start_time_obj = datetime.strptime(start_time, '%H:%M').time()
                end_time_obj = datetime.strptime(end_time, '%H:%M').time()
                
                if end_time_obj <= start_time_obj:
                    messages.error(request, 'End time must be after start time.')
                    return redirect('session_management')
                
                # Update session
                session.course = course
                session.location = location
                session.date = date_obj
                session.start_time = start_time_obj
                session.end_time = end_time_obj
                session.is_active = is_active
                session.save()
                
                messages.success(request, 'Session updated successfully.')
            except (Session.DoesNotExist, Course.DoesNotExist, Location.DoesNotExist):
                messages.error(request, 'Invalid session, course or location selected.')
            except ValueError:
                messages.error(request, 'Invalid date or time format.')
        
        elif action == 'delete':
            # Handle session deletion
            session_id = request.POST.get('session_id')
            
            try:
                session = Session.objects.get(id=session_id)
                session.delete()
                messages.success(request, 'Session deleted successfully.')
            except Session.DoesNotExist:
                messages.error(request, 'Session not found.')
        
        return redirect('session_management')
    
    # Add is_upcoming and is_ongoing properties to each session for the template
    for session in page_obj:
        session.is_upcoming = session.date > today or (session.date == today and session.start_time > now)
        session.is_ongoing = (
            session.date == today and 
            session.start_time <= now <= session.end_time
        )
    
    context = {
        'courses': courses,
        'locations': locations,
        'active_locations': Location.objects.filter(is_active=True),
        'sessions': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'selected_course': int(selected_course) if selected_course else '',
        'selected_location': int(selected_location) if selected_location else '',
        'date_from': date_from,
        'date_to': date_to,
        'status': status,
    }
    
    return render(request, 'core/management/session_management.html', context)