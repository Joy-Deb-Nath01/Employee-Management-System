from django.urls import path
from .views import (
    EmployeeListView, EmployeeDetailView, EmployeeCreateView,
    EmployeeUpdateView, toggle_employee_active
)

urlpatterns = [
    path('', EmployeeListView.as_view(), name='employee_list'),
    path('<int:pk>/', EmployeeDetailView.as_view(), name='employee_detail'),
    path('add/', EmployeeCreateView.as_view(), name='employee_add'),
    path('<int:pk>/edit/', EmployeeUpdateView.as_view(), name='employee_edit'),
    path('<int:pk>/toggle-active/', toggle_employee_active, name='employee_toggle_active'),
]
