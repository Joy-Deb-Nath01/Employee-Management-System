from django.urls import path
from .views import check_in, check_out, attendance_list, attendance_history

urlpatterns = [
    path('check-in/', check_in, name='attendance_checkin'),
    path('check-out/', check_out, name='attendance_checkout'),
    path('admin-logs/', attendance_list, name='attendance_list'),
    path('history/', attendance_history, name='attendance_history'),
]
