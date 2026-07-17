from django.contrib import admin
from .models import Employee

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'full_name', 'department', 'designation', 'is_active')
    list_filter = ('department', 'designation', 'is_active', 'gender')
    search_fields = ('employee_id', 'user__first_name', 'user__last_name', 'user__email', 'designation')
    actions = ['activate_employees', 'deactivate_employees']

    def activate_employees(self, request, queryset):
        queryset.update(is_active=True)
    activate_employees.short_description = "Activate selected employees"

    def deactivate_employees(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_employees.short_description = "Deactivate selected employees"
