from django.urls import path

from .views import (get_groups_view, access_denied, change_password_view, edit_profile_view, group_students,
                    instructor_dashboard, instructor_upload_file, library_view, login_view, profile_view, request_otp, resend_otp, reset_password, 
                    student_library_view, check_email_request, request_account, students_list, verify_otp)

from .views import (get_groups_view, access_denied, change_password_view, edit_profile_view,
                    instructor_dashboard_view, library_view, login_view, profile_view, 
                    student_library_view, check_email_request, request_account, instructor_list, students_list)

from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('get-groups/', get_groups_view, name='get_groups'),
    # path('set_language/', include('django.conf.urls.i18n')), for jazzmin settings

    path('',  login_view, name='home'),
    path('login/', login_view, name='login'),
    path('student-library/', student_library_view, name='student_library'),
    path('instructor-dashboard/', instructor_dashboard, name='instructor_dashboard'),
    path('library/', library_view, name='library'),
    path('access-denied/', access_denied, name='access_denied'),
    path('profile/', profile_view, name='profile'),
    path('change_password/', change_password_view, name='change_password'),
    path('edit_profile/', edit_profile_view, name='edit_profile'),
    path('', LogoutView.as_view, name='logout'),
    path('request-account/', request_account, name='request_account'),
    path('check-email-request/', check_email_request, name='check_email_request'),


    path('instructors/', instructor_list, name='instructor_list'),
    
    path('students-list/', students_list, name='students_list'),
    path('request-otp/', request_otp, name='request_otp'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('reset-password/', reset_password, name='reset_password'),
    path('resend-otp/', resend_otp, name='resend_otp'),
    path('group/<int:group_id>/students/', group_students, name='group_students'),
    path('instructor-upload-file/',instructor_upload_file, name='instructor_upload_file'),

]
