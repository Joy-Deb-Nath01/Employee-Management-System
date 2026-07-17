from django import forms
from django.utils import timezone
from django.db import models
from .models import LeaveRequest, LeaveBalance

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'leave_type': forms.Select(attrs={'class': 'form-select form-control-custom'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control form-control-custom', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control form-control-custom', 'type': 'date'}),
            'reason': forms.Textarea(attrs={'class': 'form-control form-control-custom', 'rows': 3, 'placeholder': 'Please state the reason for this leave request...'}),
        }

    def __init__(self, *args, **kwargs):
        # Extract the employee instance passed by the view
        self.employee = kwargs.pop('employee', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        leave_type = cleaned_data.get('leave_type')

        if not start_date or not end_date or not leave_type or not self.employee:
            return cleaned_data

        # 1. Start Date & End Date Logic check
        if start_date > end_date:
            raise forms.ValidationError("End date cannot be earlier than start date.")

        # 2. Prevent past dates
        if start_date < timezone.now().date():
            raise forms.ValidationError("Cannot request leaves starting in the past.")

        # 3. Check overlapping requests
        overlapping = LeaveRequest.objects.filter(
            employee=self.employee,
            status__in=['Pending', 'Approved']
        ).exclude(id=self.instance.id).filter(
            models.Q(start_date__range=(start_date, end_date)) |
            models.Q(end_date__range=(start_date, end_date)) |
            models.Q(start_date__lte=start_date, end_date__gte=end_date)
        )
        if overlapping.exists():
            raise forms.ValidationError("You have an overlapping leave request (Pending/Approved) for the selected dates.")

        # 4. Validate remaining leave balance
        duration = (end_date - start_date).days + 1
        try:
            balance_record = self.employee.leave_balance
        except LeaveBalance.DoesNotExist:
            balance_record = LeaveBalance.objects.create(employee=self.employee)

        balance = balance_record.get_balance(leave_type)
        if leave_type != 'Unpaid' and balance < duration:
            raise forms.ValidationError(
                f"Insufficient leave balance. You requested {duration} day(s), "
                f"but you only have {balance} day(s) remaining for {leave_type} leave."
            )

        return cleaned_data
