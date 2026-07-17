from django.contrib import admin
from .models import LeaveRequest, LeaveBalance

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'leave_type', 'start_date', 'employee__department')
    search_fields = ('employee__user__first_name', 'employee__user__last_name', 'employee__employee_id')

@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'sick_balance', 'casual_balance', 'earned_balance')
    search_fields = ('employee__user__first_name', 'employee__user__last_name', 'employee__employee_id')
