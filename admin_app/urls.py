from django.shortcuts import render
from django.urls import path
from django.conf.urls import  handler400, handler403, handler404, handler500

from .views import (departments_list, library_my_uploaded_files, delete_file, departments_with_groups, get_groups_view, 
                    access_denied, change_password_view, edit_profile_view, group_students, 
                    instructor_dashboard, edit_file, upload_file, instructors_list, admin_dashboard, student_dashboard,
                    library_view, home_view, login_view, logout_view, profile_view, request_otp, resend_otp, reset_password, 
                    request_account, students_list, verify_otp)

from .views import (custom_400, custom_403, custom_404, custom_405, custom_500)

urlpatterns = [
    path('get-groups/', get_groups_view, name='get_groups'),
    # path('set_language/', include('django.conf.urls.i18n')), for jazzmin settings


    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'), 
    path('instructor_dashboard/', instructor_dashboard, name='instructor_dashboard'),
    path('student_dashboard/', student_dashboard, name='student_dashboard'),
    path('departments_list/', departments_list, name='departments_list'),
    path('instructors_list/', instructors_list, name='instructors_list'),
    path('students_list/', students_list, name='students_list'),
    path('departments_with_groups/', departments_with_groups, name='departments_with_groups'),
    path('group/<group_id>/students/', group_students, name='group_students'),
    path('library_list/', library_view, name='library_list'),
    path('library_list/library_my_uploaded_files/', library_my_uploaded_files, name='library_my_uploaded_files'),
    path('library_list/upload_file/',upload_file, name='upload_file'),
    path('library_my_uploaded_files/edit_file/<file_id>/', edit_file, name='edit_file'),
    path('library_my_uploaded_files/delete_file/<int:file_id>/', delete_file, name='delete_file'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit_profile/', edit_profile_view, name='edit_profile'),
    path('profile/change_password/', change_password_view, name='change_password'),
    path('request_account/', request_account, name='request_account'),

    path('',  home_view, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('access_denied/', access_denied, name='access_denied'),
    
    path('request_otp/', request_otp, name='request_otp'),
    path('verify_otp/', verify_otp, name='verify_otp'),
    path('reset_password/', reset_password, name='reset_password'),
    path('resend_otp/', resend_otp, name='resend_otp'),
    
    path('400/', custom_400, name='400'),
    path('403/', custom_403, name='403'),
    path('404/', custom_404, name='404'),
    path('405/', custom_405, name='405'),
    path('500/', custom_500, name='500'),
    path('test-404/', lambda request: render(request, '404.html', status=404)),

]

handler400 = 'admin_app.views.custom_400'
handler403 = 'admin_app.views.custom_403'
handler404 = 'admin_app.views.custom_404'
handler500 = 'admin_app.views.custom_500'

