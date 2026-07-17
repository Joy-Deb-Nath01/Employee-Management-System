from django.db import models
from employees.models import Employee

class Attendance(models.Model):
    STATUS_CHOICES = (
        ('Present', 'Present'),
        ('Late', 'Late'),
        ('Half-day', 'Half-day'),
        ('Absent', 'Absent'),
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Absent')

    class Meta:
        unique_together = ('employee', 'date')
        verbose_name_plural = "Attendance"

    def __str__(self):
        return f"{self.employee.full_name} - {self.date} ({self.status})"
