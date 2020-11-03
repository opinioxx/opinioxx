from django.urls import path

from opinioxx.base import views
from django.contrib.auth import views as auth_views

from opinioxx.base.forms import LoginForm

app_name = 'base'

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/login', auth_views.LoginView.as_view(authentication_form=LoginForm), name='login'),
    path('accounts/password_reset',
         auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'), name='password_reset'),
    path('accounts/password_reset/done/',
         auth_views.PasswordResetView.as_view(template_name='registration/password_reset_success.html'),
         name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='registration/passwordresetconfirm.html'),
         name='password_reset_confirm'),
    path('accounts/reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/passwordresetcomplete.html'),
         name='password_reset_confirm'),
    path('accounts/register', views.register, name='register'),
    path('profile', views.profile, name='profile'),
    path('profile/changepassword', views.profile_changepassword, name='profile_changepassword'),
    path('profile/emailsettings', views.profile_emailsettings, name='profile_emailsettings'),
    path('new', views.newproject, name='newproject'),
    path('<int:project_id>', views.project, name='project'),
    path('<int:project_id>/c', views.project, {'compact': True}, name='projectcompact'),
    path('<int:project_id>/edit', views.newproject, name='editproject'),
    path('<int:project_id>/new', views.newidea, name='newidea'),
    path('<int:project_id>/<int:idea_id>/detail', views.idea, name='idea'),
    path('<int:project_id>/archive', views.project, {'archive': True}, name='archive'),
    path('<int:project_id>/c/archive', views.project, {'archive': True, 'compact': True}, name='archivecompact'),
    path('<int:project_id>/vote', views.vote, name='vote'),
    path('cron', views.cron, name='cron'),
]
