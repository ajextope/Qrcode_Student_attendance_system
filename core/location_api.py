from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from geopy.distance import geodesic
from .models import Location, Attendance, QRCode
import json

@require_POST
@login_required
def verify_location(request):
    """
    API endpoint to verify if a user's location is within the valid radius of a class location
    """
    try:
        data = json.loads(request.body)
        user_latitude = float(data.get('latitude'))
        user_longitude = float(data.get('longitude'))
        qrcode_uuid = data.get('qrcode_uuid')
        
        # Validate input
        if not all([user_latitude, user_longitude, qrcode_uuid]):
            return JsonResponse({'success': False, 'error': 'Missing required parameters'}, status=400)
        
        # Get QR code
        try:
            qrcode = QRCode.objects.get(uuid=qrcode_uuid)
        except QRCode.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Invalid QR code'}, status=404)
        
        # Check if QR code is expired
        if qrcode.is_expired():
            return JsonResponse({'success': False, 'error': 'QR code has expired'}, status=400)
        
        # Get location from session
        location = qrcode.session.location
        
        # Calculate distance between user and class location
        user_point = (user_latitude, user_longitude)
        location_point = (float(location.latitude), float(location.longitude))
        distance = geodesic(user_point, location_point).meters
        
        # Check if user is within the allowed radius
        is_within_radius = distance <= location.radius
        
        # If within radius, mark attendance
        if is_within_radius:
            # Check if student is enrolled in the course
            session = qrcode.session
            course = session.course
            if request.user not in course.students.all():
                return JsonResponse({
                    'success': False, 
                    'error': 'You are not enrolled in this course',
                    'distance': distance,
                    'max_radius': location.radius
                }, status=403)
            
            # Create or update attendance record
            attendance, created = Attendance.objects.get_or_create(
                student=request.user,
                session=session,
                defaults={
                    'qrcode': qrcode,
                    'verification_method': 'geolocation',
                    'is_present': True,
                    'latitude': user_latitude,
                    'longitude': user_longitude
                }
            )
            
            if not created:
                # Update existing record with geolocation data
                attendance.verification_method = 'geolocation'
                attendance.latitude = user_latitude
                attendance.longitude = user_longitude
                attendance.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Attendance marked successfully',
                'distance': distance,
                'max_radius': location.radius,
                'location_name': location.name
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'You are not within the required distance of the class location',
                'distance': distance,
                'max_radius': location.radius,
                'location_name': location.name
            }, status=400)
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
