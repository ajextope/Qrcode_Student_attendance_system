from django.urls import path
from . import views
from . import location_api
from . import attendance_utils

urlpatterns = [
    path('', views.home, name='home'),
    path('courses/', views.course_list, name='course_list'),
    path('qrcode/generate/', views.generate_qrcode, name='generate_qrcode'),
    path('qrcode/scan/', views.scan_qrcode, name='scan_qrcode'),
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/export/', attendance_utils.export_attendance, name='export_attendance'),
    path('session/manage/', views.session_management, name='session_management'),
    path('user/manage/', views.user_management, name='user_management'),
    path('course/manage/', views.course_management, name='course_management'),
    path('location/manage/', views.location_management, name='location_management'),
    path('enrolled_courses/', views.enrolled_courses, name='enrolled_courses'),

    path('api/qrcode/status/<int:qrcode_id>/', views.check_qrcode_status, name='check_qrcode_status'),
    path('api/location/verify/', location_api.verify_location, name='verify_location'),
     path('api/courses/<int:course_id>/available_students/', views.get_available_students, name='available_students'),
    path('api/courses/<int:course_id>/enrolled_students/', views.get_enrolled_students, name='enrolled_students'),
    path('api/courses/add_students/', views.add_students_to_course, name='add_students'),
    path('api/courses/remove_students/', views.remove_students_from_course, name='remove_students'),
]
