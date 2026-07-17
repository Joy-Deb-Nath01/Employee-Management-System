from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from employees.models import Employee

class LeaveRequest(models.Model):
    LEAVE_TYPE_CHOICES = (
        ('Sick', 'Sick'),
        ('Casual', 'Casual'),
        ('Earned', 'Earned/Annual'),
        ('Unpaid', 'Unpaid'),
    )

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_requests'
    )
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    remarks = models.TextField(blank=True, null=True)
    applied_on = models.DateTimeField(auto_now_add=True)

    @property
    def duration(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0

    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type} ({self.start_date} to {self.end_date}) - {self.status}"


class LeaveBalance(models.Model):
    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_balance'
    )
    sick_balance = models.IntegerField(default=12)
    casual_balance = models.IntegerField(default=12)
    earned_balance = models.IntegerField(default=15)

    def get_balance(self, leave_type):
        if leave_type == 'Sick':
            return self.sick_balance
        elif leave_type == 'Casual':
            return self.casual_balance
        elif leave_type == 'Earned':
            return self.earned_balance
        elif leave_type == 'Unpaid':
            return 999  # Unpaid leave has no hard balance limit
        return 0

    def deduct_balance(self, leave_type, days):
        if leave_type == 'Sick':
            self.sick_balance = max(0, self.sick_balance - days)
        elif leave_type == 'Casual':
            self.casual_balance = max(0, self.casual_balance - days)
        elif leave_type == 'Earned':
            self.earned_balance = max(0, self.earned_balance - days)
        self.save()

    def __str__(self):
        return f"Balances for {self.employee.full_name}"


# Signal to create LeaveBalance automatically when an Employee is created
@receiver(post_save, sender=Employee)
def create_employee_leave_balance(sender, instance, created, **kwargs):
    if created:
        LeaveBalance.objects.get_or_create(employee=instance)
