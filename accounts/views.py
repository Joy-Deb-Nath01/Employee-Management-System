from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordResetView, 
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
)
from django.urls import reverse_lazy
from django.contrib import messages

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        """Role-based redirect after successful login."""
        messages.success(self.request, f"Welcome back, {self.request.user.get_full_name() or self.request.user.username}!")
        return reverse_lazy('dashboard')

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password. Please try again.")
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')


class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        messages.success(self.request, "Password reset email sent. Please check your console/email.")
        return super().form_valid(form)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

    def form_valid(self, form):
        messages.success(self.request, "Your password has been reset successfully. You can now login.")
        return super().form_valid(form)


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'
