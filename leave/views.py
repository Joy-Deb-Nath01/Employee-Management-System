from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from .models import LeaveRequest, LeaveBalance
from .forms import LeaveRequestForm
from employees.models import Employee
from departments.models import Department

@login_required
def leave_history(request):
    """
    Lists employee's own leave requests and displays active balances.
    """
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        return redirect('dashboard')

    leaves = LeaveRequest.objects.filter(employee=employee).order_by('-applied_on')
    balance, created = LeaveBalance.objects.get_or_create(employee=employee)

    context = {
        'leaves': leaves,
        'balance': balance,
    }
    return render(request, 'leave/leave_history.html', context)


@login_required
def leave_apply(request):
    """
    Form view to request new leaves. Passes employee to form context for validations.
    """
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, "Only registered employees can apply for leaves.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = LeaveRequestForm(request.POST, employee=employee)
        if form.is_valid():
            leave_req = form.save(commit=False)
            leave_req.employee = employee
            leave_req.save()
            messages.success(request, "Leave request submitted successfully and is pending approval.")
            return redirect('leave_history')
    else:
        form = LeaveRequestForm(employee=employee)

    return render(request, 'leave/leave_apply.html', {'form': form})


@login_required
@role_required('ADMIN', 'HR')
def leave_list(request):
    """
    Admin/HR view to filter, list, and examine all pending/resolved leave requests.
    """
    leaves = LeaveRequest.objects.all().select_related('employee__user', 'employee__department').order_by('-applied_on')

    # Filter by status
    status = request.GET.get('status', '')
    if status:
        leaves = leaves.filter(status=status)

    # Filter by department
    dept_id = request.GET.get('department', '')
    if dept_id:
        leaves = leaves.filter(employee__department_id=dept_id)

    departments = Department.objects.all()
    context = {
        'leaves': leaves,
        'departments': departments,
        'status_filter': status,
        'department_id': dept_id,
    }
    return render(request, 'leave/leave_list.html', context)


@login_required
@role_required('ADMIN', 'HR')
def leave_review(request, pk):
    """
    Detailed review page to Approve/Reject leaves with custom remarks.
    """
    leave_req = get_object_or_404(LeaveRequest, pk=pk)

    if leave_req.status != 'Pending':
        messages.warning(request, "This leave request has already been reviewed.")
        return redirect('leave_list')

    if request.method == 'POST':
        action = request.POST.get('action')
        remarks = request.POST.get('remarks', '')

        if action == 'approve':
            duration = leave_req.duration
            balance, created = LeaveBalance.objects.get_or_create(employee=leave_req.employee)
            available_balance = balance.get_balance(leave_req.leave_type)

            # Revalidate leave balance before processing approval
            if leave_req.leave_type != 'Unpaid' and available_balance < duration:
                messages.error(
                    request, 
                    f"Cannot approve leave request. Employee does not have enough balance "
                    f"({available_balance} available, {duration} requested)."
                )
                return redirect('leave_list')

            # Deduct balance and approve
            balance.deduct_balance(leave_req.leave_type, duration)
            leave_req.status = 'Approved'
            leave_req.remarks = remarks
            leave_req.save()
            messages.success(request, f"Leave request for {leave_req.employee.full_name} has been approved.")

        elif action == 'reject':
            leave_req.status = 'Rejected'
            leave_req.remarks = remarks
            leave_req.save()
            messages.success(request, f"Leave request for {leave_req.employee.full_name} has been rejected.")

        return redirect('leave_list')

    return render(request, 'leave/leave_review.html', {'leave': leave_req})
