from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db import models
from django.core.exceptions import PermissionDenied

from accounts.decorators import RoleRequiredMixin, role_required
from .models import Employee
from .forms import EmployeeRegisterForm, EmployeeEditForm
from departments.models import Department

User = get_user_model()

class EmployeeListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = Employee
    template_name = 'employees/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 10
    allowed_roles = ['ADMIN', 'HR']

    def get_queryset(self):
        # We start with all employees (both active and inactive) so Admin/HR can manage them
        queryset = Employee.objects.all().select_related('user', 'department').order_by('employee_id')
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                models.Q(employee_id__icontains=search_query) |
                models.Q(user__first_name__icontains=search_query) |
                models.Q(user__last_name__icontains=search_query) |
                models.Q(user__email__icontains=search_query) |
                models.Q(designation__icontains=search_query)
            )

        # Filters
        dept_filter = self.request.GET.get('department', '')
        if dept_filter:
            queryset = queryset.filter(department_id=dept_filter)

        designation_filter = self.request.GET.get('designation', '')
        if designation_filter:
            queryset = queryset.filter(designation__icontains=designation_filter)

        status_filter = self.request.GET.get('status', '')
        if status_filter == 'active':
            queryset = queryset.filter(is_active=True)
        elif status_filter == 'inactive':
            queryset = queryset.filter(is_active=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.all()
        
        # Fetch distinct designations for filter dropdown
        context['designations'] = Employee.objects.exclude(designation__isnull=True).exclude(designation='').values_list('designation', flat=True).distinct()
        
        # Keep URL query parameters for paginated links
        queries = self.request.GET.copy()
        if 'page' in queries:
            del queries['page']
        context['queries'] = queries.urlencode()
        
        return context


class EmployeeDetailView(LoginRequiredMixin, DetailView):
    model = Employee
    template_name = 'employees/employee_detail.html'
    context_object_name = 'employee'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        
        # Enforce that normal employees can only view their own profile
        if user.role == 'EMPLOYEE' and obj.user != user:
            raise PermissionDenied("You do not have permission to view other employees' profiles.")
        return obj


class EmployeeCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Employee
    form_class = EmployeeRegisterForm
    template_name = 'employees/employee_form.html'
    success_url = reverse_lazy('employee_list')
    allowed_roles = ['ADMIN', 'HR']

    def form_valid(self, form):
        # Extract fields for user creation
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        role = form.cleaned_data['role']

        # Create Django User account with default password
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        user.set_password('EmsPassword123')  # Default password
        user.save()

        # Build linked Employee profile
        employee = form.save(commit=False)
        employee.user = user
        employee.save()

        messages.success(
            self.request, 
            f"Employee registered successfully! A linked User account was created for '{username}' with default password 'EmsPassword123'."
        )
        return redirect(self.success_url)


class EmployeeUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = Employee
    form_class = EmployeeEditForm
    template_name = 'employees/employee_form.html'
    success_url = reverse_lazy('employee_list')
    allowed_roles = ['ADMIN', 'HR']

    def form_valid(self, form):
        # Save Employee profile
        employee = form.save()

        # Sync changes back to linked User model
        user = employee.user
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.email = form.cleaned_data['email']
        user.save()

        messages.success(self.request, f"Employee '{employee.full_name}' updated successfully.")
        return redirect(self.success_url)


@login_required
@role_required('ADMIN', 'HR')
def toggle_employee_active(request, pk):
    """
    Toggle employee's is_active (soft delete / reactivation).
    Deactivating the employee also disables their linked Django User login.
    """
    employee = get_object_or_404(Employee, pk=pk)
    
    # Toggle active status
    employee.is_active = not employee.is_active
    employee.save()
    
    # Toggle linked User active status
    user = employee.user
    user.is_active = employee.is_active
    user.save()
    
    status_str = "activated" if employee.is_active else "deactivated"
    messages.success(request, f"Employee '{employee.full_name}' and their user login have been successfully {status_str}.")
    return redirect('employee_list')
