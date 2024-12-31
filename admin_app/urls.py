from django.urls import path
from .views import (access_denied, change_password_view, edit_profile_view,
    instructor_dashboard_view, library_view, login_view, profile_view, student_library_view)
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('',  login_view, name='home'),
    path('login/', login_view, name='login'),
    path('student-library/', student_library_view, name='student_library'),
    path('instructor-dashboard/', instructor_dashboard_view, name='instructor_dashboard'),
    path('library/', library_view, name='library'),
    path('access-denied/', access_denied, name='access_denied'),
    path('profile/', profile_view, name='profile'),
    path('change_password/', change_password_view, name='change_password'),
    path('edit_profile/', edit_profile_view, name='edit_profile'),
    path('', LogoutView.as_view, name='logout'),

]
