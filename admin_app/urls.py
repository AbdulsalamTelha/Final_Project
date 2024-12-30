from django.urls import path
from .views import (
    login_view,
    student_library_view,
    instructor_dashboard_view,
    library_view,
    access_denied,
    
)

urlpatterns = [
    path('',  login_view, name='home'),
    path('login/', login_view, name='login'),
    path('student-library/', student_library_view, name='student_library'),
    path('instructor-dashboard/', instructor_dashboard_view, name='instructor_dashboard'),
    path('library/', library_view, name='library'),
    path('access-denied/', access_denied, name='access_denied'),
]
