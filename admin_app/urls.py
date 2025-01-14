from django.urls import path
from .views import (get_groups_view, access_denied, change_password_view, edit_profile_view,
                    instructor_dashboard_view, library_view, login_view, profile_view, 
                    student_library_view, check_email_request, request_account, instructors_list, students_list)
from django.contrib.auth.views import LogoutView
from . import views 
urlpatterns = [
    path('get-groups/', get_groups_view, name='get_groups'),
    # path('set_language/', include('django.conf.urls.i18n')), for jazzmin settings

    path('',  login_view, name='home'),
    path('login/', login_view, name='login'),
    path('student_library/', student_library_view, name='student_library'),
    path('instructor_dashboard/', instructor_dashboard_view, name='instructor_dashboard'),
    path('library/', library_view, name='library'),
    path('access_denied/', access_denied, name='access_denied'),
    path('profile/', profile_view, name='profile'),
    path('change_password/', change_password_view, name='change_password'),
    path('edit_profile/', edit_profile_view, name='edit_profile'),
    path('', LogoutView.as_view, name='logout'),
    path('request_account/', request_account, name='request_account'),
    path('check_email_request/', check_email_request, name='check_email_request'),


    path('instructors_list/', instructors_list, name='instructors_list'),
    
    path('students_list/', students_list, name='students_list'),
    path('request_otp/', views.request_otp, name='request_otp'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('resend_otp/', views.resend_otp, name='resend_otp'),
]
