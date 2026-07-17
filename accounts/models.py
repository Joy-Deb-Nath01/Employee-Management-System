from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('HR', 'HR/Manager'),
        ('EMPLOYEE', 'Employee'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='EMPLOYEE')

    def is_admin_or_hr(self):
        return self.role in ['ADMIN', 'HR']

    def is_hr(self):
        return self.role == 'HR'

    def is_employee(self):
        return self.role == 'EMPLOYEE'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
