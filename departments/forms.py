from django import forms
from .models import Department
from employees.models import Employee

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description', 'head']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'Enter Department Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control form-control-custom', 'rows': 3, 'placeholder': 'Enter Department Description'}),
            'head': forms.Select(attrs={'class': 'form-select form-control-custom'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter potential department heads to active employees only
        self.fields['head'].queryset = Employee.objects.filter(is_active=True)
        self.fields['head'].required = False
        self.fields['head'].empty_label = "Select Department Head (Optional)"
