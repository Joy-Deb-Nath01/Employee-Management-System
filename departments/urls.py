from django.urls import path
from .views import (
    DepartmentListView, DepartmentDetailView, DepartmentCreateView,
    DepartmentUpdateView, DepartmentDeleteView
)

urlpatterns = [
    path('', DepartmentListView.as_view(), name='department_list'),
    path('<int:pk>/', DepartmentDetailView.as_view(), name='department_detail'),
    path('add/', DepartmentCreateView.as_view(), name='department_add'),
    path('<int:pk>/edit/', DepartmentUpdateView.as_view(), name='department_edit'),
    path('<int:pk>/delete/', DepartmentDeleteView.as_view(), name='department_delete'),
]
