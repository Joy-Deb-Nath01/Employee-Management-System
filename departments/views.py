from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.decorators import RoleRequiredMixin
from .models import Department
from .forms import DepartmentForm

class DepartmentListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = Department
    template_name = 'departments/department_list.html'
    context_object_name = 'departments'
    allowed_roles = ['ADMIN', 'HR']


class DepartmentDetailView(LoginRequiredMixin, RoleRequiredMixin, DetailView):
    model = Department
    template_name = 'departments/department_detail.html'
    context_object_name = 'department'
    allowed_roles = ['ADMIN', 'HR']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch active and inactive employees assigned to this department
        context['assigned_employees'] = self.object.employees.filter(is_active=True)
        context['inactive_employees'] = self.object.employees.filter(is_active=False)
        return context


class DepartmentCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'departments/department_form.html'
    success_url = reverse_lazy('department_list')
    allowed_roles = ['ADMIN', 'HR']

    def form_valid(self, form):
        messages.success(self.request, f"Department '{form.cleaned_data['name']}' created successfully.")
        return super().form_valid(form)


class DepartmentUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'departments/department_form.html'
    success_url = reverse_lazy('department_list')
    allowed_roles = ['ADMIN', 'HR']

    def form_valid(self, form):
        messages.success(self.request, f"Department '{form.cleaned_data['name']}' updated successfully.")
        return super().form_valid(form)


class DepartmentDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = Department
    template_name = 'departments/department_confirm_delete.html'
    success_url = reverse_lazy('department_list')
    allowed_roles = ['ADMIN', 'HR']

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Verify if department contains active employees
        if self.object.employees.filter(is_active=True).exists():
            messages.error(
                request, 
                f"Cannot delete department '{self.object.name}' because active employees are still assigned to it. "
                f"Please reassign or deactivate the employees first."
            )
            return redirect('department_list')
        
        messages.success(request, f"Department '{self.object.name}' deleted successfully.")
        return super().post(request, *args, **kwargs)
