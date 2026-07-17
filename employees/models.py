from django.db import models
from django.conf import settings
from departments.models import Department

class Employee(models.Model):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee_profile'
    )
    employee_id = models.CharField(max_length=20, unique=True, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees'
    )
    designation = models.CharField(max_length=100, blank=True, null=True)
    date_of_joining = models.DateField(blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)  # Soft delete field

    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username

    def save(self, *args, **kwargs):
        # Auto-generate employee_id if not present
        if not self.employee_id:
            last_emp = Employee.objects.all().order_by('id').last()
            if last_emp and last_emp.employee_id:
                try:
                    last_num = int(last_emp.employee_id.replace('EMP', ''))
                    self.employee_id = f"EMP{last_num + 1:04d}"
                except ValueError:
                    import uuid
                    self.employee_id = f"EMP{uuid.uuid4().hex[:6].upper()}"
            else:
                self.employee_id = "EMP0001"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.employee_id})"
