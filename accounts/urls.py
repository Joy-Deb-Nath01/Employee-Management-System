from django.urls import path
from .views import (
    CustomLoginView, CustomLogoutView, CustomPasswordResetView,
    CustomPasswordResetDoneView, CustomPasswordResetConfirmView, CustomPasswordResetCompleteView
)

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
