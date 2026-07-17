from django.urls import path
from .views import leave_history, leave_apply, leave_list, leave_review

urlpatterns = [
    path('history/', leave_history, name='leave_history'),
    path('apply/', leave_apply, name='leave_apply'),
    path('admin-list/', leave_list, name='leave_list'),
    path('<int:pk>/review/', leave_review, name='leave_review'),
]
