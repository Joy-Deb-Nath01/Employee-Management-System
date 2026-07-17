from django import forms
from django.contrib.auth import get_user_model
from .models import Employee
from departments.models import Department

User = get_user_model()

class EmployeeRegisterForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'Last Name'})
    )
    username = forms.CharField(
        max_length=150, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'Username'})
    )
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'Email Address'})
    )
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES, 
        widget=forms.Select(attrs={'class': 'form-select form-control-custom'})
    )

    class Meta:
        model = Employee
        fields = ['phone', 'date_of_birth', 'gender', 'address', 'department', 'designation', 'date_of_joining', 'profile_photo']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'Phone Number'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control form-control-custom', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select form-control-custom'}),
            'address': forms.Textarea(attrs={'class': 'form-control form-control-custom', 'rows': 2, 'placeholder': 'Home Address'}),
            'department': forms.Select(attrs={'class': 'form-select form-control-custom'}),
            'designation': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'Designation (e.g., Software Engineer)'}),
            'date_of_joining': forms.DateInput(attrs={'class': 'form-control form-control-custom', 'type': 'date'}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control form-control-custom'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with this username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email address already exists.")
        return email


class EmployeeEditForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control form-control-custom'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control form-control-custom'})
    )
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={'class': 'form-control form-control-custom'})
    )

    class Meta:
        model = Employee
        fields = ['phone', 'date_of_birth', 'gender', 'address', 'department', 'designation', 'profile_photo']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control form-control-custom'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control form-control-custom', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select form-control-custom'}),
            'address': forms.Textarea(attrs={'class': 'form-control form-control-custom', 'rows': 2}),
            'department': forms.Select(attrs={'class': 'form-select form-control-custom'}),
            'designation': forms.TextInput(attrs={'class': 'form-control form-control-custom'}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control form-control-custom'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(id=self.instance.user.id).exists():
            raise forms.ValidationError("A user with this email address already exists.")
        return email
