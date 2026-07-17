from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.db import models
from accounts.decorators import role_required
from .models import Attendance
from employees.models import Employee
from departments.models import Department
import datetime

@login_required
def check_in(request):
    """
    Clock in for today. Auto-calculates late vs half-day vs present status based on timing.
    """
    if request.method != 'POST':
        return redirect('dashboard')

    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, "Only registered employees can check in.")
        return redirect('dashboard')

    today = timezone.now().date()
    
    # Verify no check-in exists for today
    existing = Attendance.objects.filter(employee=employee, date=today).first()
    if existing:
        messages.warning(request, "You have already checked in for today.")
        return redirect('dashboard')

    now = timezone.now()
    check_in_time = now.time()

    # Define shift rules
    # Standard start: 9:00 AM. Grace: 9:15 AM. Half-day: 12:00 PM.
    grace_limit = datetime.time(9, 15)
    half_day_limit = datetime.time(12, 0)

    if check_in_time <= grace_limit:
        status = 'Present'
    elif check_in_time <= half_day_limit:
        status = 'Late'
    else:
        status = 'Half-day'

    Attendance.objects.create(
        employee=employee,
        date=today,
        check_in=check_in_time,
        status=status
    )
    
    messages.success(request, f"Clock-in successful at {now.strftime('%I:%M %p')} (Status: {status}).")
    return redirect('dashboard')


@login_required
def check_out(request):
    """
    Clock out for today. Saves check_out timestamp.
    """
    if request.method != 'POST':
        return redirect('dashboard')

    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, "Only registered employees can check out.")
        return redirect('dashboard')

    today = timezone.now().date()
    attendance = Attendance.objects.filter(employee=employee, date=today).first()

    if not attendance:
        messages.error(request, "You must check in first before checking out.")
        return redirect('dashboard')

    if attendance.check_out:
        messages.warning(request, "You have already checked out for today.")
        return redirect('dashboard')

    now = timezone.now()
    attendance.check_out = now.time()
    attendance.save()

    messages.success(request, f"Clock-out successful at {now.strftime('%I:%M %p')}. Have a good day!")
    return redirect('dashboard')


@login_required
@role_required('ADMIN', 'HR')
def attendance_list(request):
    """
    Admin/HR dashboard to filter and view employee attendance logs.
    """
    attendances = Attendance.objects.all().select_related('employee__user', 'employee__department').order_by('-date', 'employee__employee_id')

    # Date filters
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    if start_date:
        attendances = attendances.filter(date__gte=start_date)
    if end_date:
        attendances = attendances.filter(date__lte=end_date)

    # Department filter
    dept_id = request.GET.get('department', '')
    if dept_id:
        attendances = attendances.filter(employee__department_id=dept_id)

    # Text search
    search = request.GET.get('search', '')
    if search:
        attendances = attendances.filter(
            models.Q(employee__employee_id__icontains=search) |
            models.Q(employee__user__first_name__icontains=search) |
            models.Q(employee__user__last_name__icontains=search)
        )

    departments = Department.objects.all()
    context = {
        'attendances': attendances,
        'departments': departments,
        'start_date': start_date,
        'end_date': end_date,
        'department_id': dept_id,
        'search': search,
    }
    return render(request, 'attendance/attendance_list.html', context)


@login_required
def attendance_history(request):
    """
    Employee's view of their personal attendance logging history and monthly calculations.
    """
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        return redirect('dashboard')

    logs = Attendance.objects.filter(employee=employee).order_by('-date')

    # Monthly calculation statistics
    now = timezone.now()
    month_logs = logs.filter(date__year=now.year, date__month=now.month)
    present_count = month_logs.filter(status='Present').count()
    late_count = month_logs.filter(status='Late').count()
    half_day_count = month_logs.filter(status='Half-day').count()
    absent_count = month_logs.filter(status='Absent').count()

    context = {
        'logs': logs,
        'present_count': present_count,
        'late_count': late_count,
        'half_day_count': half_day_count,
        'absent_count': absent_count,
        'current_month': now.strftime('%B %Y')
    }
    return render(request, 'attendance/attendance_history.html', context)
