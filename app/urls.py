

from django.urls import path 
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

from .views import index, logout

from .views import index


urlpatterns = [   
    path('accounts/login/', LoginView.as_view(), name='login' ),
    path('accounts/logout/', LogoutView.as_view(next_page='base'), name='logout' ),
    path('accounts/base/', logout, name='base'),

    path('accounts/password_reset/', PasswordResetView.as_view(
                    template_name='registration/reset_password.html',
                    subject_template_name='registration/reset_subject.txt',
                    html_email_template_name='registration/reset_email.html', 
                    from_email = 'Администратор <extanydata@gmail.com>'),
                    name='password_reset' ),
    # Уведомление об отправке письма для сброса пароля
    path('accounts/password_reset/done/', PasswordResetDoneView.as_view(
                    template_name='registration/email_send.html'),
                    name = 'password_reset_done' ),
    # Сброс пароля
    path('accounts/reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
                    template_name='registration/confirm_password.html'),
                    name = 'password_reset_confirm' ),
    # Уведомление об успешном сбросе пароля
    path('accounts/reset/done/', PasswordResetCompleteView.as_view(
                    template_name= 'registration/password_confirmed.html' ),
                    name='password_reset_complete'),

    path('', index, name='mainapp')

    ]

