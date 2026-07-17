from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from employees.models import Employee
from departments.models import Department
from attendance.models import Attendance
from leave.models import LeaveRequest, LeaveBalance
from django.db.models import Count

@login_required
def dashboard_home(request):
    user = request.user
    today = timezone.now().date()

    if user.role in ['ADMIN', 'HR']:
        total_employees = Employee.objects.filter(is_active=True).count()
        total_departments = Department.objects.count()

        # Today's attendance summary
        present_today = Attendance.objects.filter(date=today, status__in=['Present', 'Late', 'Half-day']).count()
        
        # Calculate real absent count: active employees who are not marked present/late/half-day today
        # To avoid double-counting or negative numbers, get employees with check-ins today
        checked_in_ids = Attendance.objects.filter(date=today, status__in=['Present', 'Late', 'Half-day']).values_list('employee_id', flat=True)
        absent_today = Employee.objects.filter(is_active=True).exclude(id__in=checked_in_ids).count()

        pending_leaves = LeaveRequest.objects.filter(status='Pending').count()
        recent_joiners = Employee.objects.filter(is_active=True).order_by('-date_of_joining')[:5]

        # Attendance chart details
        status_counts = Attendance.objects.filter(date=today).values('status').annotate(count=Count('id'))
        attendance_chart = {'Present': 0, 'Late': 0, 'Half_day': 0, 'Absent': absent_today}
        for item in status_counts:
            key = item['status'].replace('-', '_')
            attendance_chart[key] = item['count']

        # Leaves chart details
        leave_counts = LeaveRequest.objects.values('status').annotate(count=Count('id'))
        leave_chart = {'Pending': 0, 'Approved': 0, 'Rejected': 0}
        for item in leave_counts:
            leave_chart[item['status']] = item['count']

        context = {
            'total_employees': total_employees,
            'total_departments': total_departments,
            'present_today': present_today,
            'absent_today': absent_today,
            'pending_leaves': pending_leaves,
            'recent_joiners': recent_joiners,
            'attendance_chart': attendance_chart,
            'leave_chart': leave_chart,
        }
        return render(request, 'dashboard/admin_dashboard.html', context)

    else:
        # Standard Employee
        try:
            employee = user.employee_profile
        except Employee.DoesNotExist:
            return render(request, 'dashboard/employee_dashboard.html', {
                'profile_missing': True,
                'username': user.username
            })

        # Monthly attendance calculation
        now = timezone.now()
        month_attendances = Attendance.objects.filter(
            employee=employee, 
            date__year=now.year, 
            date__month=now.month
        )
        present_days = month_attendances.filter(status='Present').count()
        late_days = month_attendances.filter(status='Late').count()
        half_days = month_attendances.filter(status='Half-day').count()
        absent_days = month_attendances.filter(status='Absent').count()

        # Verify leave balance is active
        leave_balance, created = LeaveBalance.objects.get_or_create(employee=employee)

        # Retrieve recent leaves
        recent_leaves = LeaveRequest.objects.filter(employee=employee).order_by('-applied_on')[:5]

        # Verify today's attendance record
        today_attendance = Attendance.objects.filter(employee=employee, date=today).first()

        context = {
            'employee': employee,
            'present_days': present_days,
            'late_days': late_days,
            'half_days': half_days,
            'absent_days': absent_days,
            'leave_balance': leave_balance,
            'recent_leaves': recent_leaves,
            'today_attendance': today_attendance,
        }
        return render(request, 'dashboard/employee_dashboard.html', context)
